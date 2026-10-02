const test=require('node:test'),assert=require('node:assert/strict');
const ready=require('../scripts/portal-ready.cjs');
test('transient null report/data during selection must wait instead of throw',()=>{
  global.window={selDataBase:{dt:201012},selTipoInst:{id:1006},selRelatorio:null};
  assert.equal(ready(201012),false);
});
test('ready requires correct scope, complete shards and selected columns',()=>{
  global.window={selDataBase:{dt:201012},selTipoInst:{id:1006},selRelatorio:{trel:{n:'Resumo',c:[{ifd:1}]}},
    document:{getElementById:()=>({style:{display:'block'}})},table:{rows:[[1]],cols:[{ifd:{id:1}}]},selDados:[{}],selExpectedAreas:1};
  assert.equal(ready(201012),true);
  assert.equal(ready(202412),false);
  window.selRelatorio.trel.c[0].ifd=2;assert.equal(ready(201012),false);
  window.selRelatorio.trel.c[0].ifd=1;window.selDados=[];assert.equal(ready(201012),false);
});
