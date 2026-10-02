/* Bounded official BCB CSV fallback. This does not interact with Codex. */
const fs=require('node:fs'), path=require('node:path'), crypto=require('node:crypto');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const ready=require('./portal-ready.cjs');
const {Budget}=require('./budget.cjs');
const period=Number(process.argv[2]), raw=path.resolve(process.argv[3]);
if (![201012,202312,202412].includes(period)) throw Error('Only 201012, 202312 and 202412 are authorized');
fs.mkdirSync(raw,{recursive:true});
const manifests=[], diagnostics=[],requestFailures=[];
const startedAt=new Date().toISOString(),attempt=Number(process.env.PILOT_ATTEMPT||1);
if(![1,2].includes(attempt))throw Error('Attempt exceeds approved two-attempt bound');
const maxMs=Number(process.env.PILOT_TIMEOUT_MS || 480000);
if(!Number.isFinite(maxMs)||maxMs<1000||maxMs>480000)throw Error('Invalid bounded execution deadline');
const budget=new Budget(80*1024*1024,maxMs);
const space=fs.statfsSync(raw);budget.checkSpace(Number(space.bavail)*Number(space.bsize));
function save(body,url,status,headers,kind,context={}) {
  const fullLength=body.length,fullHash=crypto.createHash('sha256').update(body).digest('hex');
  const retained=budget.take(fullLength);body=body.subarray(0,retained);
  const now=new Date().toISOString(), stem=`${now.replace(/[:.]/g,'')}_${period}_${crypto.randomUUID()}`;
  const item={url,final_url:url,method:kind==='http_response'?'GET':'browser_export',
    query_parameters:[...new URL(url).searchParams.entries()],context:{period,...context},
    http_status:status,response_headers:headers,retrieved_at_utc:now,bytes:body.length,
    sha256:crypto.createHash('sha256').update(body).digest('hex'),body_path:stem+'.bin',manifest_path:stem+'.json',
    kind,outcome:retained<fullLength?'budget_truncated':status===null?'generated_evidence':status===200?'ok':'http_error',
    diagnostics:kind==='http_response'?['Playwright stores decoded response-body bytes']:['Official browser-generated evidence, not an HTTP response']};
  fs.writeFileSync(path.join(raw,item.body_path),body,{flag:'wx'});
  if(retained<fullLength) {
    item.truncated=true;item.observed_response_bytes=fullLength;item.observed_response_sha256=fullHash;
    item.diagnostics.push('80 MiB raw-body budget exhausted. Retained prefix only; not accepted evidence.');
  }
  fs.writeFileSync(path.join(raw,item.manifest_path),JSON.stringify(item,null,2),{flag:'wx'});
  manifests.push(item);
  if(item.truncated)throw Error('Raw-body budget exceeded; truncated prefix archived and export rejected');
  return item;
}
(async()=>{
  let browser,deadlineTimer,complete=false;
  try {
  browser=await chromium.launch({headless:true,executablePath:process.env.PILOT_BROWSER_PATH || undefined});
  const context=await browser.newContext({acceptDownloads:true}), page=await context.newPage(), pending=[];
  deadlineTimer=setTimeout(()=>{diagnostics.push('TIME_BUDGET_EXCEEDED');browser.close().catch(()=>{});},maxMs);
  page.on('dialog',async d=>{diagnostics.push(d.message());await d.dismiss();});
  /* Capture before forwarding: large catalogs can be evicted from Chromium's inspector cache. */
  await page.route('**/ifdata/**',async route=>{
    const url=route.request().url();
    if(new URL(url).hostname!=='www3.bcb.gov.br')return route.continue();
    const requestStartedAt=new Date().toISOString();
    const operation=(async()=>{
      budget.checkTime();
      const response=await route.fetch({timeout:Math.max(1,Math.min(90000,budget.deadline-Date.now()))}),body=await response.body();
      save(body,response.url(),response.status(),response.headers(),'http_response',
        {requested_url:url,request_started_at_utc:requestStartedAt,body_capture:'Intercepted official response bytes before browser fulfillment'});
      await route.fulfill({response,body});
    })().catch(async error=>{
      diagnostics.push(`ARCHIVE_FAILURE ${url}: ${error.message}`);
      const failure={period,attempt,url,method:'GET',query_parameters:[...new URL(url).searchParams.entries()],
        started_at_utc:requestStartedAt,finished_at_utc:new Date().toISOString(),http_status:null,
        outcome:'request_or_archive_failure',diagnostics:[error.message],response_body_preserved:false,
        limitation:'A corresponding HTTP manifest may already exist; this record alone does not establish response status/body'};
      requestFailures.push(failure);
      fs.writeFileSync(path.join(raw,`request-failure-${period}-${crypto.randomUUID()}.json`),JSON.stringify(failure,null,2),{flag:'wx'});
      await route.abort().catch(()=>{});
      if(budget.exceeded)await context.close().catch(()=>{});
    });
    pending.push(operation);await operation;
  });
    const url=`https://www3.bcb.gov.br/ifdata/index2024.html?dt=${period}`;
    await page.goto(url,{waitUntil:'domcontentloaded',timeout:60000});
    await page.waitForFunction(p=>window.selDataBase?.dt===p,period,{timeout:90000});
    await page.getByRole('button',{name:'Toggle Dropdown'}).nth(1).click();
    await page.getByRole('link',{name:'Instituições Individuais',exact:true}).click();
    await page.getByRole('button',{name:'Toggle Dropdown'}).nth(2).click();
    await page.getByRole('link',{name:'Resumo',exact:true}).click();
    await page.waitForFunction(ready,period,{timeout:180000});
    const state=await page.evaluate(()=>({period:selDataBase.dt,type_id:selTipoInst.id,type_name:selTipoInst.n,
      report:{id:selRelatorio.trel.id,n:selRelatorio.trel.n,cp:selRelatorio.trel.cp,ge:selRelatorio.trel.ge,rp:selRelatorio.trel.rp,ri:selRelatorio.trel.ri},
      columns:table.cols.map(c=>({ifd:c.ifd.id,fid:c.fid})),rows:table.rows,
      infos:selInfos.map(i=>({id:i.id,n:i.n,d:i.d,a:i.a,ty:i.ty})),header_lines:csvHeaderLines,
      expected_columns:selRelatorio.trel.c.map(c=>c.ifd),expected_areas:selExpectedAreas,loaded_areas:selDados.length}));
    const sm=save(Buffer.from(JSON.stringify(state)),url,null,{},'portal_table_state');
    const [download]=await Promise.all([page.waitForEvent('download',{timeout:30000}),
      page.locator('#aExportCsv').click({timeout:30000})]);
    const csv=fs.readFileSync(await download.path());
    const cm=save(csv,url,null,{'Content-Type':'text/csv;charset=utf-8'},'official_portal_csv',
      {state_sha256:sm.sha256,source_function:'Official downloadCsv() blob export',filename:download.suggestedFilename()});
    await Promise.all(pending);
    budget.checkTime();
    if(diagnostics.some(d=>d.startsWith('ARCHIVE_FAILURE')))throw Error('Required archive incomplete: '+diagnostics.join('; '));
    const index={period,complete:true,state_manifest:sm,csv_manifest:cm,manifests,diagnostics,request_failures:requestFailures,
      started_at_utc:startedAt,finished_at_utc:new Date().toISOString(),
      budget:{raw_body_bytes:budget.bytes,max_raw_body_bytes:budget.maxBytes,max_ms:maxMs,attempt:Number(process.env.PILOT_ATTEMPT||1)},
      limitation:'Shared quarterly portal shards may include other report data. Only the individual Resumo table is accepted. CSV is formatted/rounded; raw HTTP and unformatted state are preserved.'};
    const indexPath=path.join(raw,`portal-export-${period}-${crypto.randomUUID()}.json`);
    fs.writeFileSync(indexPath,JSON.stringify(index,null,2),{flag:'wx'});
    complete=true;
    console.log(JSON.stringify({export_index:indexPath,period,rows:state.rows.length,columns:state.columns.length}));
  }catch(error){diagnostics.push(error.message);throw error;}
  finally{
    if(deadlineTimer)clearTimeout(deadlineTimer);
    if(browser)await browser.close().catch(()=>{});
    if(!complete)fs.writeFileSync(path.join(raw,`portal-failed-${period}-${crypto.randomUUID()}.json`),JSON.stringify({period,attempt,complete:false,manifests,diagnostics,
      request_failures:requestFailures,started_at_utc:startedAt,finished_at_utc:new Date().toISOString(),
      budget:{raw_body_bytes:budget.bytes,max_raw_body_bytes:budget.maxBytes,max_ms:maxMs,exceeded:budget.exceeded}},null,2),{flag:'wx'});
  }
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
