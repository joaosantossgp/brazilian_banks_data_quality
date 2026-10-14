"""Exploratory IF.data indicators, preserving literal components and contexts."""
from decimal import Decimal, InvalidOperation, localcontext
import hashlib
import json
import csv
import re
from datetime import datetime, timezone
from calendar import monthrange
from itertools import groupby
from pathlib import Path
import tempfile
import duckdb
from .ifdata_cadastro import open_cadastro, attach_values, _records
from .ifdata_odata import _path, _digest, FIELDS as NATIVE_FIELDS, PROVENANCE

CONTRACT = 'ifdata-indicator-pilot-v1'
TABLES = ('results', 'wide', 'coverage', 'statistics')

PRECISION = 100
DUPLICATE_POLICY = 'identical-native-rows-same-source-v1'
STOCK_DEFINITIONS = {
    ('1', '78182'): '[10000007] + [20000004]',
    ('1', '78186'): '[60000002] + [70000009]+ [80000006]',
    ('2', '78191'): '[16000001]-[16900008]',
    ('2', '78192'): '[16900008]', ('3', '78287'): '[41000007]',
    ('1', '140220'): '[1000000009] + [2000000008]',
    ('1', '140246'): '[6000000004]+ [7000000003]+ [8000000002]',
    ('2', '140205'): '[1600000007]', ('3', '140228'): '[4100000009]',
}


def calculate(numerator, denominator):
    """Divide finite numeric tokens to 100 significant digits; never normalize signs."""
    result = dict(numerator=numerator, denominator=denominator, value=None,
                  status='missing_component', negative_denominator=False)
    if numerator is None or denominator is None:
        return result
    if not isinstance(numerator, str) or not isinstance(denominator, str):
        result['status'] = 'invalid_numeric'
        return result
    try:
        n, d = Decimal(numerator), Decimal(denominator)
        if not n.is_finite() or not d.is_finite():
            raise InvalidOperation
    except (InvalidOperation, ValueError, TypeError):
        result['status'] = 'invalid_numeric'
        return result
    result['negative_denominator'] = d < 0
    if d == 0:
        result['status'] = 'zero_denominator'
        return result
    with localcontext() as context:
        context.prec = PRECISION
        token = format(n / d, 'f')
    result['value'] = token.rstrip('0').rstrip('.') if '.' in token else token
    result['status'] = 'ok'
    return result


def _coalesce_exact_occurrences(previous, row):
    """Resolve literal repeats within one captured page, retaining every locator.

    Equal balances alone cannot establish a repeat. Missing native fields,
    different semantic attributes/pages, or reused positions remain ambiguous.
    Authentication of the underlying page belongs to the existing input reader.
    """
    if any('ambiguous_occurrences' in r for r in (previous, row)):
        return None
    if not all(k in r for r in (previous, row) for k in NATIVE_FIELDS):
        return None
    if not isinstance(previous.get('CodInst'), str) or not previous['CodInst'].strip():
        return None
    semantic = (set(previous) | set(row)) - set(PROVENANCE) - {'source_occurrences'}
    if any(k not in previous or k not in row or type(previous[k]) is not type(row[k])
           or previous[k] != row[k] for k in semantic):
        return None
    source_fields = tuple(k for k in PROVENANCE if k != 'source_row')
    if any(not isinstance(previous.get(k), str) or not previous[k]
           or previous[k] != row.get(k) for k in source_fields):
        return None
    if not re.fullmatch('[0-9a-f]{64}', previous['source_sha256']):
        return None
    occurrences = []
    for item in (previous, row):
        occurrences.extend(item.get('source_occurrences',
                                    [{k:item.get(k) for k in PROVENANCE}]))
    positions = []
    for occurrence in occurrences:
        position = occurrence.get('source_row')
        if (any(occurrence.get(k) != previous[k] for k in source_fields)
                or not isinstance(position, str) or not re.fullmatch('[1-9][0-9]*', position)):
            return None
        positions.append(position)
    if len(set(positions)) != len(positions):
        return None
    occurrences = sorted(occurrences, key=lambda p:int(p['source_row']))
    return dict(previous, source_row=occurrences[0]['source_row'],
                source_occurrences=occurrences)


def build_pilot(values_root, cadastro, output, periods=None, opening_root=None):
    """Build immutable exploratory tables using authenticated local inputs."""
    values_root, cadastro, output = map(lambda p: Path(p).resolve(), (values_root, cadastro, output))
    if output.exists():
        raise FileExistsError(output)
    if periods is not None and (not periods or len(set(periods)) != len(periods)):
        raise ValueError('Empty or duplicate periods')
    output.mkdir(parents=True)
    manifest = dict(contract=CONTRACT, created_utc=datetime.now(timezone.utc).isoformat(),
                    precision=PRECISION, division='100 significant decimal digits, rounded',
                    statistics='approximate DOUBLE, no trimming or winsorization',
                    sample='technical native population; listed-company eligibility not certified',
                    csv_omits=['numerator_definition','denominator_definition','mean_stock_inputs'],
                    duplicate_policy=DUPLICATE_POLICY,
                    inputs=[], excluded_missing_codes=[], files=[], rows=0)
    manifest['inputs'].append(dict(dataset='cadastro', manifest_sha256=_digest((cadastro/'manifest.json').read_bytes())))
    with tempfile.TemporaryDirectory(dir=output) as temporary, open_cadastro(cadastro) as conn:
        stages, available = [], set()
        for dataset in ('financial', 'individual', 'capital'):
            root = values_root / dataset
            attach_values(conn, root)
            manifest['inputs'].append(dict(dataset=dataset, manifest_sha256=_digest((root/'manifest.json').read_bytes())))
            history = {}
            if dataset != 'capital':
                sources = [root]
                if opening_root is not None:
                    sources.append(Path(opening_root).resolve()/dataset)
                for stock_source in sources:
                    if stock_source != root:
                        attach_values(conn, stock_source)
                        manifest['inputs'].append(dict(dataset=dataset+'_opening',manifest_sha256=_digest((stock_source/'manifest.json').read_bytes())))
                    stock_rows = _records(conn.execute('''select * from ifdata_cadastrado where NumeroRelatorio='1'
                        and Conta in ('78182','78186','140220','140246') and CodInst is not null and CodInst<>''
                        and AnoMes<=? ''',[max(periods) if periods else '999912']))
                    for row in stock_rows:
                        key = row['CodInst'],row['AnoMes'],row['Conta']
                        if key in history:
                            previous=history[key]
                            resolved=_coalesce_exact_occurrences(previous,row)
                            if resolved is not None:
                                history[key]=resolved
                            else:
                                occurrences=previous.get('ambiguous_occurrences',[previous])
                                history[key]=dict(previous,Saldo=None,ambiguous_occurrences=[*occurrences,row])
                        else:
                            history[key] = row
                if len(sources)>1:
                    attach_values(conn, root)
            native_periods = [r[0] for r in conn.execute('select distinct AnoMes from ifdata order by AnoMes').fetchall()]
            available.update(native_periods)
            for period in native_periods:
                if periods is not None and period not in periods:
                    continue
                missing = conn.execute("select count(*) from ifdata where AnoMes=? and (CodInst is null or CodInst='')", [period]).fetchone()[0]
                if missing:
                    manifest['excluded_missing_codes'].append(dict(dataset=dataset, period=period, native_rows=missing, reason='missing_native_code'))
                accounts = list({k[1] for k in STOCK_DEFINITIONS} | {'78187','141870','78226','141867','78208','79664','79659'})
                placeholders = ','.join('?' for _ in accounts)
                rows = _records(conn.execute(f'''select * from ifdata_cadastrado
                    where AnoMes=? and CodInst is not null and CodInst<>'' and Conta in ({placeholders})
                    order by CodInst, NumeroRelatorio, Conta''', [period, *accounts]))
                units = _records(conn.execute('''select distinct CodInst,AnoMes,TipoInstituicao,
                    NomeInstituicao,Td,cadastro_encontrado from ifdata_cadastrado
                    where AnoMes=? and CodInst is not null and CodInst<>'' order by CodInst''',[period]))
                if not units:
                    continue
                grouped_rows = {code:list(grouped) for code,grouped in groupby(rows,key=lambda r:r['CodInst'])}
                stage = Path(temporary) / f'{dataset}-{period}.csv'
                with stage.open('w', newline='', encoding='utf-8') as stream:
                    writer = None
                    for unit in units:
                        evaluated = evaluate_unit(dataset, grouped_rows.get(unit['CodInst'],[]), unit=unit,
                                                  history=history,native_windows=True,retain_ambiguity=True)
                        if writer is None:
                            writer = csv.DictWriter(stream, fieldnames=list(evaluated[0]), quoting=csv.QUOTE_NOTNULL)
                            writer.writeheader()
                        writer.writerows(evaluated)
                        manifest['rows'] += len(evaluated)
                compressed=stage.with_suffix('.parquet')
                conn.execute('''create or replace temp table stage_source as select * replace(
                    cast(negative_denominator as boolean) as negative_denominator,
                    cast(cadastro_found as boolean) as cadastro_found)
                    from read_csv(?, all_varchar=true, header=true, nullstr='', allow_quoted_nulls=false)''',[str(stage)])
                conn.execute('copy stage_source to ? (format parquet,compression zstd)',[str(compressed)])
                conn.execute('drop table stage_source')
                stage.unlink()
                stages.append(str(compressed))
        if periods is not None and not set(periods) <= available:
            raise ValueError('Unknown periods')
        if not stages:
            raise ValueError('No native units in selection')
        conn.from_parquet(stages).create_view('results')
        if conn.execute('''select count(*) from (select dataset,code,period,indicator,method,count(*) n
            from results group by all having n<>1)''').fetchone()[0]:
            raise ValueError('Duplicate result identity')
        combinations = conn.execute('select distinct indicator,method from results order by all').fetchall()
        pivots = []
        for indicator, method in combinations:
            column = indicator if method == 'nativo' else indicator+'_'+method
            for field, suffix in [('value',''),('status','_status'),('version','_version')]:
                pivots.append(f"max({field}) filter(where indicator='{indicator}' and method='{method}') as {column}{suffix}")
        conn.execute('''create temp table wide as select dataset,perspective,unit_class,code,period,name,
            cadastro_found,consolidation_type,''' + ','.join(pivots) + ' from results group by all')
        dimensions = 'dataset,perspective,unit_class,period,indicator,method,version,unit,"window",window_months,mean_weights'
        conn.execute(f'''create temp table coverage as select {dimensions},status,count(*) as n
            from results group by all order by all''')
        conn.execute(f'''create temp table statistics as select {dimensions},count(*) as n_total,
            count(x) as n_valid,count(*) filter(where status='ok') as n_calculated,
            avg(x) as mean,stddev_samp(x) as stddev,min(x) as minimum,
            quantile_cont(x,0.25) as p25,median(x) as median,quantile_cont(x,0.75) as p75,max(x) as maximum
            from (select *,case when status='ok' and isfinite(try_cast(value as double))
                then try_cast(value as double) end as x from results) group by all order by all''')
        for table in TABLES:
            for extension, options in [('parquet','format parquet, compression zstd'),
                                       ('csv',"format csv, header true, force_quote *")]:
                target = output / f'{table}.{extension}'
                relation = '(select * exclude(numerator_definition,denominator_definition,mean_stock_inputs) from results)' if table=='results' and extension=='csv' else table
                conn.execute(f'copy {relation} to ? ({options})',[str(target)])
                manifest['files'].append(dict(file=target.name,sha256=_digest(target.read_bytes())))
        _render_panel(conn, output / 'painel.html', manifest)
        manifest['files'].append(dict(file='painel.html',sha256=_digest((output/'painel.html').read_bytes())))
    (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return manifest


def open_pilot(output):
    """Authenticate generated tables and expose four SQL views."""
    output = Path(output).resolve()
    manifest = json.loads((output/'manifest.json').read_text(encoding='utf-8'))
    expected = {f'{t}.{e}' for t in TABLES for e in ('parquet','csv')} | {'painel.html'}
    files = manifest.get('files',[])
    if manifest.get('contract') != CONTRACT or len(files) != len(expected) or {f['file'] for f in files} != expected:
        raise ValueError('Incomplete pilot inventory')
    for item in files:
        if _digest(_path(output,item['file']).read_bytes()) != item['sha256']:
            raise ValueError('Pilot file hash mismatch')
    conn = duckdb.connect()
    try:
        for table in TABLES:
            conn.from_parquet(str(output/f'{table}.parquet')).create_view(table)
        if conn.execute('select count(*) from results').fetchone()[0] != manifest['rows']:
            raise ValueError('Pilot result count mismatch')
        return conn
    except Exception:
        conn.close()
        raise


def _render_panel(conn, output, manifest):
    """Build a self-contained offline exploration from the same SQL results."""
    payload = dict(statistics=_records(conn.execute('select * from statistics')),
                   coverage=_records(conn.execute('select * from coverage')),
                   excluded=manifest['excluded_missing_codes'],
                   names=conn.execute('select distinct dataset,code,period,name from results order by all').fetchall(),
                   points=conn.execute('''select dataset,unit_class,period,code,indicator,method,version,cast(value as double)
                       from results where status='ok' and isfinite(try_cast(value as double))
                       order by dataset,unit_class,period,code,indicator,method''').fetchall())
    encoded = json.dumps(payload,ensure_ascii=False,separators=(',',':'),allow_nan=False).replace('<','\\u003c')
    output.write_text(PANEL.replace('__DATA__',encoded),encoding='utf-8')


PANEL = '''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>IF.data · Laboratório de indicadores</title>
<style>
:root{color-scheme:light;font-family:Segoe UI,Arial,sans-serif;color:#173748;background:#f1f6f8;font-size:15px}*{box-sizing:border-box}body{margin:0}header{background:#123a4a;color:white;padding:32px max(5vw,20px)}header small{letter-spacing:.15em;color:#a9d8df}h1{font-family:Georgia,serif;font-size:clamp(28px,4vw,43px);font-weight:400;margin:12px 0}header p{max-width:850px;line-height:1.6;color:#d0e1e8}main{max-width:1500px;margin:auto;padding:24px 5vw}nav{display:flex;flex-wrap:wrap;gap:16px;padding:20px 0;border-bottom:1px solid #c7d9e1}label{display:grid;gap:7px;font-size:13px;font-weight:600}select{font:inherit;color:inherit;border:1px solid #acc1cc;border-radius:5px;padding:9px;background:white;max-width:300px}select:focus{outline:3px solid #61b6cb}.grid{display:grid;grid-template-columns:1.4fr 1fr;gap:20px;margin:24px 0}article{padding:20px;background:white;border:1px solid #d5e2e8;border-radius:8px;min-width:0}h2{font-size:19px;font-weight:600;margin:0 0 8px}.sub{font-size:13px;line-height:1.5;color:#55717f}.chart{width:100%;height:auto;display:block;min-height:200px}.metrics{display:flex;flex-wrap:wrap;gap:25px;margin:20px 0}.metrics strong{display:block;font-size:25px;font-variant-numeric:tabular-nums}.metrics span{font-size:12px;color:#55717f}table{width:100%;border-collapse:collapse;font-size:13px}td,th{text-align:left;padding:10px;border-bottom:1px solid #e1eaee}td:last-child{text-align:right;font-variant-numeric:tabular-nums}.scroll{max-height:300px;overflow:auto}.notice{border-left:4px solid #deac55;padding:13px 17px;background:#fff8e8;line-height:1.6}.empty{padding:45px 10px;color:#55717f;text-align:center}.legend{display:flex;gap:20px;font-size:12px}.wide{grid-column:1/-1}button{background:#176278;color:white;border:0;border-radius:5px;padding:10px 14px;cursor:pointer;font:inherit}footer{font-size:12px;line-height:1.7;color:#55717f;padding:24px 0}@media(max-width:850px){.grid{grid-template-columns:1fr}nav label{width:100%}select{max-width:none}.wide{grid-column:auto}main{padding:16px}header{padding:24px}}
</style>
<header><small>IF.DATA / PESQUISA EXPLORATÓRIA</small><h1>Desempenho financeiro, por perspectiva.</h1><p>Oito candidatos em teste. Explore resultados, distribuições e cobertura mantendo instituições individuais, conglomerados e perímetro prudencial identificados.</p></header>
<main><div class="notice">População técnica disponível na fonte; elegibilidade de capital aberto ainda não certificada. Lucros e receitas usam a janela nativa de 3 ou 6 meses do semestre, conforme inferência contábil documentada; não são anualizados. ROE e ROA comparam médias de abertura/fechamento e trimestral simples, incluindo abertura com pesos iguais. Provisão é razão assinada literal; índices prudenciais permanecem na escala nativa.</div>
<nav><label>Perspectiva<select id="context"></select></label><label>Indicador / método<select id="indicator"></select></label><label>Definição / versão<select id="version"></select></label><label>Data-base<select id="period"></select></label><label>Instituição<select id="bank"></select></label></nav>
<div id="metrics" class="metrics" aria-live="polite"></div><div class="grid">
<article><h2>Evolução na mesma definição</h2><p class="sub">Mediana e intervalo entre percentis 25 e 75, ou trajetória da instituição selecionada. A linha interrompe em referências sem valor; versões ficam separadas.</p><div id="trend"></div></article>
<article><h2>Distribuição na data-base</h2><p class="sub">Todas as observações válidas do recorte, sem corte de extremos. Valores na unidade indicada, sem multiplicação por 100.</p><div id="hist"></div></article>
<article><h2>Relação entre indicadores</h2><label>Comparar com<select id="compare"></select></label><label>Versão do comparador<select id="compareVersion"></select></label><p class="sub">Pares do mesmo código, perspectiva e data; versões dos dois eixos explícitas. Associação descritiva, sem inferência causal.</p><div id="scatter"></div></article>
<article><h2>Cobertura e motivos</h2><p class="sub">Inclui resultados não calculados; nenhum motivo vira zero. Contagens pertencem à definição selecionada.</p><div id="coverage" class="scroll"></div><p id="missing" class="sub"></p></article>
<article class="wide"><h2>Dados do recorte</h2><p class="sub">Componentes literais, fórmulas, versões e motivos estão em results.parquet, incluindo a proveniência completa. results.csv é compacto: omite os três campos JSON de definições e estoques da média. wide.csv / wide.parquet oferecem uma coluna por indicador e método.</p><button id="download">Exportar valores exibidos em CSV</button><div id="rows" class="scroll"></div></article></div>
<footer>Razões calculadas com Decimal, 100 algarismos significativos; divisões não terminantes são arredondadas. Gráficos e estatística descritiva usam aproximação numérica. Não há seleção automática da amostra, soma de perspectivas, corte de valores extremos ou ponte certificada entre regimes. Os arquivos da base mantêm os componentes e a proveniência.</footer></main>
<script type="application/json" id="data">__DATA__</script><script>
const D=JSON.parse(document.getElementById('data').textContent),$=id=>document.getElementById(id),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),fmt=x=>x==null?'—':Number(x).toLocaleString('pt-BR',{maximumSignificantDigits:6});
const titles={roe:'ROE · janela nativa',roa:'ROA · janela nativa',margem_liquida:'Margem líquida',credito_depositos:'Crédito / depósitos',provisao_credito:'Provisão / crédito · assinada',pl_ativo:'PL / ativo total',basileia:'Basileia · escala nativa',capital_principal:'Capital principal · escala nativa'};
const reasons={duplicate_binding:'Mais de uma ocorrência do componente',duplicate_stock_binding:'Estoque da média com ocorrências repetidas',ok:'Calculado / publicado',window_unproven:'Janela do fluxo não comprovada',mapping_unproven:'Componente histórico não conciliado',binding_missing:'Componente não observado',null_balance:'Saldo nulo',zero_denominator:'Denominador zero',invalid_numeric:'Token não numérico',definition_unproven:'Definição não aprovada',opening_stock_missing:'Estoque da média não observado',opening_regime_incompatible:'Abertura atravessa regime não conciliado',opening_perimeter_unproven:'Perímetro da abertura desconhecido ou alterado'};
function options(id,items){let before=$(id).value;$(id).replaceChildren(...items.map(([v,t])=>{let o=document.createElement('option');o.value=v;o.textContent=t;return o}));if(items.some(i=>i[0]===before))$(id).value=before}
const uniq=a=>[...new Set(a)],context=r=>r.dataset+'|'+r.unit_class,ind=r=>r.indicator+'|'+r.method;
options('context',uniq(D.statistics.map(context)).map(x=>[x,x.replace('financial|','Financeira · ').replace('individual|','Individual · ').replace('capital|','Prudencial · ')]));
const names=new Map(D.names.map(r=>[r[0]+'|'+r[1]+'|'+r[2],r[3]||r[1]])),bankName=(ds,c)=>names.get(ds+'|'+c+'|'+$('period').value)||c;
function base(){return D.statistics.filter(r=>context(r)===$('context').value)}
function versionLabel(v,rows){let a=rows.filter(r=>r.version===v),p=a.map(r=>r.period).sort(),m=a[0]?.window_months;return p[0]+'–'+p.at(-1)+(m?' · '+m+' meses':'')+' · '+v.slice(0,6)}
function updateOptions(level=0){const b=base();if(level<=0){let ids=uniq(b.map(ind));options('indicator',ids.map(x=>[x,titles[x.split('|')[0]]+' / '+x.split('|')[1]]));options('compare',ids.map(x=>[x,titles[x.split('|')[0]]+' / '+x.split('|')[1]]))}
if(level<=1){options('version',uniq(b.filter(r=>ind(r)===$('indicator').value).map(r=>r.version)).map(x=>[x,versionLabel(x,b)]));options('compareVersion',uniq(b.filter(r=>ind(r)===$('compare').value).map(r=>r.version)).map(x=>[x,versionLabel(x,b)]))}
const s=b.filter(r=>ind(r)===$('indicator').value&&r.version===$('version').value);if(level<=2){options('period',uniq(s.map(r=>r.period)).sort().map(x=>[x,x.slice(0,4)+' / '+x.slice(4)]));$('period').value=s.map(r=>r.period).sort().at(-1)||'';const [ds,cl]=$('context').value.split('|');let codes=uniq(D.points.filter(p=>p[0]===ds&&p[1]===cl&&p[4]+'|'+p[5]===$('indicator').value&&p[6]===$('version').value).map(p=>p[3]));options('bank',[['','Todas · mediana'],...codes.map(c=>[c,(bankName(ds,c))+' · '+c])])}draw()}
function points(){let [ds,cl]=$('context').value.split('|'),[id,m]=$('indicator').value.split('|');return D.points.filter(p=>p[0]===ds&&p[1]===cl&&p[4]===id&&p[5]===m&&p[6]===$('version').value)}
function svg(body,xmin,xmax,ymin,ymax,xlabel='',ylabel=''){let fx=x=>xlabel==='Referência'?String(x).slice(0,4)+' / '+String(x).slice(4):fmt(x);return '<svg class="chart" role="img" aria-label="'+esc(xlabel+' '+ylabel)+'" viewBox="0 0 720 300"><path d="M65 20V255H700" fill="none" stroke="#a7becb"/><text x="65" y="278" font-size="12">'+esc(fx(xmin))+'</text><text x="650" y="278" font-size="12">'+esc(fx(xmax))+'</text><text x="5" y="30" font-size="12">'+esc(fmt(ymax))+'</text><text x="5" y="255" font-size="12">'+esc(fmt(ymin))+'</text>'+body+'</svg>'}
function range(a){let lo=Math.min(...a),hi=Math.max(...a);if(lo===hi){lo-=Math.abs(lo)*.05||1;hi+=Math.abs(hi)*.05||1}return[lo,hi]}
function scales(xs,ys){let [a,b]=range(xs),[c,d]=range(ys);return{x:v=>65+(v-a)/(b-a)*630,y:v=>255-(v-c)/(d-c)*225,a,b,c,d}}
function empty(id){$(id).innerHTML='<div class="empty">Sem valores calculáveis neste recorte. Consulte os motivos de cobertura.</div>'}
function draw(){let stats=base().filter(r=>ind(r)===$('indicator').value&&r.version===$('version').value),s=stats.find(r=>r.period===$('period').value),all=points(),now=all.filter(p=>p[2]===$('period').value),shown=$('bank').value?now.filter(p=>p[3]===$('bank').value):now;
$('metrics').innerHTML=[['Observações válidas',s?.n_valid],['Observações no recorte',s?.n_total],['Mediana',s?.median],['Média',s?.mean],['Desvio padrão',s?.stddev]].map(([l,v])=>'<div><strong>'+esc(fmt(v))+'</strong><span>'+esc(l)+'</span></div>').join('');
let series=$('bank').value?all.filter(p=>p[3]===$('bank').value).map(p=>({period:p[2],median:Number(p[7]),p25:Number(p[7]),p75:Number(p[7])})):stats.filter(r=>r.n_valid>0);series.sort((a,b)=>a.period.localeCompare(b.period));
if(!series.length)empty('trend');else{let q=t=>Number(t.slice(0,4))*4+Number(t.slice(4))/3,sc=scales(series.map(r=>q(r.period)),series.flatMap(r=>[r.p25,r.p75]));let body='';series.forEach((r,i)=>{let x=sc.x(q(r.period)),y=sc.y(r.median);if(i&&q(r.period)-q(series[i-1].period)===1){let p=series[i-1];body+='<line x1="'+sc.x(q(p.period))+'" y1="'+sc.y(p.median)+'" x2="'+x+'" y2="'+y+'" stroke="#176278" stroke-width="2"/>'}body+='<line x1="'+x+'" y1="'+sc.y(r.p25)+'" x2="'+x+'" y2="'+sc.y(r.p75)+'" stroke="#8cc8d1" stroke-width="5"/><circle cx="'+x+'" cy="'+y+'" r="3" fill="#176278"><title>'+r.period+': '+fmt(r.median)+'</title></circle>'});$('trend').innerHTML=svg(body,series[0].period,series.at(-1).period,sc.c,sc.d,'Referência','Valor')}
if(!now.length)empty('hist');else{let values=now.map(p=>Number(p[7])),[lo,hi]=range(values),bins=Array(20).fill(0);values.forEach(v=>bins[Math.min(19,Math.floor((v-lo)/(hi-lo)*20))]++);let max=Math.max(...bins),body=bins.map((n,i)=>'<rect x="'+(65+i*31.5)+'" y="'+(255-n/max*225)+'" width="30" height="'+(n/max*225)+'" fill="#358b9f"><title>'+fmt(lo+i*(hi-lo)/20)+' a '+fmt(lo+(i+1)*(hi-lo)/20)+': '+n+'</title></rect>').join('');$('hist').innerHTML=svg(body,lo,hi,0,max,'Valor','Observações')}
let [ds,cl]=$('context').value.split('|'),[ci,cm]=$('compare').value.split('|'),other=new Map(D.points.filter(p=>p[0]===ds&&p[1]===cl&&p[2]===$('period').value&&p[4]===ci&&p[5]===cm&&p[6]===$('compareVersion').value).map(p=>[p[3],Number(p[7])])),pairs=now.filter(p=>other.has(p[3]));
if(!pairs.length)empty('scatter');else{let sc=scales(pairs.map(p=>Number(p[7])),pairs.map(p=>other.get(p[3])));$('scatter').innerHTML=svg(pairs.map(p=>'<circle cx="'+sc.x(Number(p[7]))+'" cy="'+sc.y(other.get(p[3]))+'" r="3" fill="#176278" opacity=".55"><title>'+esc(bankName(ds,p[3]))+': '+fmt(p[7])+' / '+fmt(other.get(p[3]))+'</title></circle>').join(''),sc.a,sc.b,sc.c,sc.d,'Indicador selecionado','Comparador')}
let coverage=D.coverage.filter(r=>context(r)===$('context').value&&ind(r)===$('indicator').value&&r.version===$('version').value&&r.period===$('period').value);$('coverage').innerHTML='<table><tr><th>Estado</th><th>Observações</th></tr>'+coverage.map(r=>'<tr><td>'+esc(reasons[r.status]||r.status)+'</td><td>'+r.n+'</td></tr>').join('')+'</table>';
let excluded=D.excluded.filter(r=>r.dataset===ds&&r.period===$('period').value).reduce((n,r)=>n+r.native_rows,0);$('missing').textContent=excluded?excluded+' linhas nativas sem código estão no diagnóstico e não formam uma unidade calculável.':'';
$('rows').innerHTML='<table><tr><th>Instituição / código</th><th>Valor · '+esc(s?.unit||'')+'</th></tr>'+shown.slice(0,150).map(p=>'<tr><td>'+esc(bankName(ds,p[3]))+' · '+esc(p[3])+'</td><td>'+esc(fmt(p[7]))+'</td></tr>').join('')+'</table><p class="sub">'+shown.length+' valores; tabela mostra os primeiros 150. Exportação inclui todos.</p>';
$('download').onclick=()=>{let csv='dataset,unit_class,period,code,indicator,method,version,value\\r\\n'+shown.map(p=>p.map(x=>'"'+String(x).replace(/"/g,'""')+'"').join(',')).join('\\r\\n'),url=URL.createObjectURL(new Blob(['\\ufeff'+csv],{type:'text/csv;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download='indicadores-recorte.csv';a.click();URL.revokeObjectURL(url)}}
$('context').onchange=()=>updateOptions(0);$('indicator').onchange=()=>updateOptions(1);$('version').onchange=()=>updateOptions(2);$('period').onchange=draw;$('bank').onchange=draw;$('compare').onchange=()=>{options('compareVersion',uniq(base().filter(r=>ind(r)===$('compare').value).map(r=>r.version)).map(x=>[x,versionLabel(x,base())]));draw()};$('compareVersion').onchange=draw;updateOptions();
</script></html>'''


def evaluate_unit(dataset, rows, unit=None, history=None, native_windows=False,retain_ambiguity=False):
    """Evaluate one native code/date; unproved flows remain explicit gaps."""
    if dataset not in ('financial', 'individual', 'capital') or (not rows and unit is None):
        raise ValueError('Unknown dataset or empty unit')
    first = rows[0] if rows else unit
    if first['TipoInstituicao'] != {'financial': '2', 'individual': '3', 'capital': '1'}[dataset]:
        raise ValueError('Dataset/native type mismatch')
    bindings = {}
    duplicates = {}
    for row in rows:
        if (row['CodInst'], row['AnoMes'], row['TipoInstituicao']) != (
                first['CodInst'], first['AnoMes'], first['TipoInstituicao']):
            raise ValueError('Mixed native units')
        key = (row['NumeroRelatorio'], row['Conta'])
        if key in bindings:
            resolved = None if key in duplicates else _coalesce_exact_occurrences(bindings[key],row)
            if resolved is not None:
                bindings[key] = resolved
            else:
                if not retain_ambiguity:
                    raise ValueError('Duplicate native binding')
                duplicates.setdefault(key,[bindings[key]]).append(row)
        else:
            bindings[key] = row
    td = first.get('Td') if first.get('cadastro_encontrado') else None
    unit_class = ('individual' if dataset == 'individual' else
                  {'C': 'conglomerado', 'I': 'independente'}.get(td, 'desconhecido'))
    modern = first['AnoMes'] >= '202503'
    at, pl, ll = ('140220', '140246', '141870') if modern else ('78182', '78186', '78187')
    credit, dep = ('140205', '140228') if modern else ('78191', '78287')
    rat = '141867' if modern else '78226'
    rules = ([('basileia', 'nativo', ('5', '79664'), None),
              ('capital_principal', 'nativo', ('5', '79659'), None)] if dataset == 'capital' else [
        ('roe', method, ('1', ll), ('1', pl)) for method in ('abertura_fechamento', 'media_trimestral')])
    if dataset != 'capital':
        rules += [('roa', method, ('4', rat), ('1', at)) for method in ('abertura_fechamento', 'media_trimestral')]
        rules += [('margem_liquida', 'nativo', ('4', ll), ('4', '78208')),
                  ('credito_depositos', 'nativo', ('2', credit), ('3', dep)),
                  ('provisao_credito', 'nativo', ('2', '78192'), ('2', credit)),
                  ('pl_ativo', 'nativo', ('1', pl), ('1', at)),
                  ('basileia', 'nativo', ('1', '79664'), None),
                  ('capital_principal', 'nativo', ('1', '79659'), None)]
    result = []
    for indicator, method, nk, dk in rules:
        n, d = bindings.get(nk), bindings.get(dk) if dk else None
        numerator, denominator = n['Saldo'] if n else None, d['Saldo'] if d else None
        native = dk is None
        flow = indicator in ('roe','roa','margem_liquida')
        window_start,window_end,window_months,mean_inputs,mean_dates = None,None,None,[],[]
        window_rule = 'native-semester-v1' if flow and native_windows else None
        calculation = calculate(numerator, '1' if native else denominator)
        nstate = 'binding_missing' if n is None else 'null_balance' if numerator is None else 'present'
        dstate = 'not_applicable' if native else 'binding_missing' if d is None else 'null_balance' if denominator is None else 'present'
        if calculation['status'] == 'missing_component':
            calculation['status'] = 'binding_missing' if 'binding_missing' in (nstate, dstate) else 'null_balance'
        if not native and indicator not in ('roe', 'roa', 'margem_liquida') and all(r is not None for r in (n, d)):
            if any(r['DescricaoColuna'] != STOCK_DEFINITIONS.get(k) for r, k in ((n, nk), (d, dk))):
                calculation.update(value=None, status='definition_unproven')
        if native:
            calculation['value'] = numerator if calculation['status'] == 'ok' else None
        if flow:
            calculation.update(value=None, status='window_unproven')
            if native_windows:
                year,month=int(first['AnoMes'][:4]),int(first['AnoMes'][4:])
                start_month = 1 if month<=6 else 7
                window_start=f'{year:04d}-{start_month:02d}-01'
                window_end=f'{year:04d}-{month:02d}-{monthrange(year,month)[1]:02d}'
                window_months=month-start_month+1
                opening=f'{year-1:04d}12' if start_month==1 else f'{year:04d}06'
                if indicator in ('roe','roa'):
                    mean_dates=[opening,first['AnoMes']] if method=='abertura_fechamento' else [opening]+[f'{year:04d}{m:02d}' for m in range(start_month+2,month+1,3)]
                if modern and indicator=='margem_liquida':
                    calculation.update(status='mapping_unproven')
                elif not _flow_verified(n,first['AnoMes']) or (indicator=='margem_liquida' and not _flow_verified(d,first['AnoMes'])):
                    calculation.update(status='binding_missing' if n is None or (indicator=='margem_liquida' and d is None) else 'definition_unproven')
                elif indicator=='margem_liquida':
                    calculation=calculate(numerator,denominator)
                else:
                    wanted=mean_dates
                    mean_inputs=[(history or {}).get((first['CodInst'],p,dk[1])) for p in wanted]
                    mean_status=_mean_status(mean_inputs,wanted,first,dk)
                    if mean_status:
                        calculation.update(status=mean_status)
                    else:
                        with localcontext() as context:
                            context.prec=PRECISION
                            total=sum(Decimal(r['Saldo']) for r in mean_inputs)
                        denominator=calculate(format(total,'f'),str(len(mean_inputs)))['value']
                        calculation=calculate(numerator,denominator)
        if modern and indicator == 'provisao_credito':
            calculation.update(value=None, status='mapping_unproven')
        if nk in duplicates or dk in duplicates:
            calculation.update(value=None,status='duplicate_binding')
        if calculation['status']=='missing_component':
            calculation['status']='binding_missing' if 'binding_missing' in (nstate,dstate) else 'null_balance'
        definition = [(r.get(k) if r else None) for r in (n, d)
                      for k in ('NumeroRelatorio', 'Conta', 'Grupo', 'NomeColuna', 'DescricaoColuna')]
        version = hashlib.sha256(json.dumps([dataset, first['TipoInstituicao'], indicator,
                                            method, definition,window_rule,window_months], ensure_ascii=False).encode()).hexdigest()[:16]
        result.append(dict(dataset=dataset, perspective={'financial': 'financeira',
                           'individual': 'individual', 'capital': 'prudencial'}[dataset],
                           unit_class=unit_class, code=first['CodInst'], period=first['AnoMes'],
                           name=first.get('NomeInstituicao'), indicator=indicator, method=method,
                           cadastro_found=bool(first.get('cadastro_encontrado')), consolidation_type=td,
                           numerator_state=nstate, denominator_state=dstate,
                           version=version, unit='escala_nativa' if native else 'razao',
                           formula=f'{nk[0]}/{nk[1]}' + (f' / media_{method}({dk[0]}/{dk[1]};datas={",".join(mean_dates)};pesos=1/{len(mean_dates)})' if mean_dates else f' / {dk[0]}/{dk[1]}' if dk else ''),
                           window='semestre_nativo_parcial' if flow and native_windows else 'nao_comprovada' if flow else 'data_base',
                           window_start=window_start,window_end=window_end,window_months=window_months,window_rule=window_rule,
                           mean_stock_inputs=json.dumps(mean_inputs,ensure_ascii=False) if mean_inputs else None,
                           mean_dates=json.dumps(mean_dates) if mean_dates else None,
                           mean_weights='iguais_incluindo_abertura' if indicator in ('roe','roa') else None,
                           numerator_code=nk[1], denominator_code=dk[1] if dk else None,
                           numerator_definition=json.dumps({'ambiguous_occurrences':duplicates[nk]} if nk in duplicates else n, ensure_ascii=False) if n else None,
                           denominator_definition=json.dumps({'ambiguous_occurrences':duplicates[dk]} if dk in duplicates else d, ensure_ascii=False) if d else None,
                           negative_denominator=calculation['negative_denominator'],
                           numerator=numerator, denominator=denominator,
                           value=calculation['value'], status=calculation['status']))
    return result


RIF_DESCRIPTION = 'Somatório de Rendas de Operações de Crédito, Rendas de Operações de Arrendamento Mercantil, Rendas de Operações com TVM, Rendas de Operações com Instrumentos Financeiros Derivativos, Resultado de Operações de Câmbio e Rendas de Aplicações Compulsórias'


def _flow_verified(row,period):
    if row is None:
        return False
    definitions = {
        '78187':'[70000009]+[80000006]-'+ ('[81955002]' if period<'201903' else '[81956001]'),
        '141870':'[7000000003] + [8000000002] - [8195600001]',
        '78226':'Somatório do Resultado Operacional e do Resultado Não Operacional',
        '141867':'[7100000006] + [7300000002] + [8100000005] + [8300000001] - [8195600001]',
        '78208':RIF_DESCRIPTION,
    }
    return row['DescricaoColuna']==definitions.get(row['Conta'])


def _mean_status(rows,periods,current,binding):
    if periods[0]<'202503'<=current['AnoMes']:
        return 'opening_regime_incompatible'
    if any(row is None for row in rows):
        return 'opening_stock_missing'
    if any('ambiguous_occurrences' in row for row in rows):
        return 'duplicate_stock_binding'
    if any(row['TipoInstituicao']!=current['TipoInstituicao'] or
           not row.get('cadastro_encontrado') or not current.get('cadastro_encontrado') or
           row.get('Td') not in ('I','C') or current.get('Td') not in ('I','C') or
           row.get('Td')!=current.get('Td') for row in rows):
        return 'opening_perimeter_unproven'
    if any(row['DescricaoColuna']!=STOCK_DEFINITIONS.get(binding) for row in rows):
        return 'definition_unproven'
    for row in rows:
        state=calculate(row['Saldo'],'1')['status']
        if state!='ok':
            return 'null_balance' if state=='missing_component' else state
    return None
