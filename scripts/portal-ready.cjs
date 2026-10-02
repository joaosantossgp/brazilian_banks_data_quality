/* Serialized by Playwright into the official portal browser context. */
module.exports=function ready(period) {
  const report=window.selRelatorio?.trel, table=window.table, exporter=window.document?.getElementById('divExport');
  return Boolean(window.selDataBase?.dt===period&&window.selTipoInst?.id===1006&&report?.n==='Resumo'&&
    exporter&&exporter.style.display!=='none'&&table?.rows?.length>0&&
    window.selExpectedAreas>0&&window.selDados?.length===window.selExpectedAreas&&
    table.cols?.length===report.c?.length&&table.cols.every((col,index)=>col.ifd?.id===report.c[index].ifd));
};
