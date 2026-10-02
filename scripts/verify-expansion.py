"""Build the three-quarter view from immutable accepted sources and verify replay."""
import csv
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import unquote
from bank_quality.archive import load_body
from bank_quality.coverage import audit_coverage, reporting_window
from bank_quality.replay import replay

root=Path(__file__).resolve().parent.parent
old=json.loads((root/'data/pilot-20261001.collection.json').read_text(encoding='utf-8'))
new_path=root/'data/runs/expansion-202312-20261001/collection.json'
new=json.loads(new_path.read_text(encoding='utf-8'))
if new['periods']!=[202312] or not new['quarters']['202312']['values_complete']:raise ValueError('New batch not accepted')
gate=json.loads((root/'data/derived/expansion-20261001/coverage.json').read_text(encoding='utf-8'))
if not gate['gate_passed']:raise ValueError('Original coverage gate not passed')
quarters={};profiles=[];verified=0;seen=set();new_manifests=[]
for period in (201012,202312,202412):
    collection=new if period==202312 else old
    raw=(root/collection['raw_directory']).resolve()
    quarter={**collection['quarters'][str(period)],'raw_directory':str(raw)}
    evidence=[]
    if period==202312:
        for path in raw.glob('*.json'):
            item=json.loads(path.read_text(encoding='utf-8'))
            if 'body_path' in item:evidence.append(item)
        new_manifests=evidence
    else:evidence=collection['evidence_manifests']
    quarter['evidence_manifests']=evidence
    for manifest in evidence:
        key=(str(raw),manifest['body_path'])
        load_body(manifest,raw)
        if key not in seen:seen.add(key);verified+=1
    index=quarter['portal_export_index']
    table=json.loads(load_body(index['state_manifest'],raw))
    cad=[m for m in evidence if m.get('http_status')==200 and f'/cadastro{period}_1006.json' in unquote(m['url'])]
    if len(cad)!=1:raise ValueError('Registration snapshot is not unambiguous')
    identifier_column=next(i for i,col in enumerate(table['columns']) if col['ifd']==79706)
    coverage=audit_coverage(json.loads(load_body(cad[0],raw)),{str(row[identifier_column]) for row in table['rows']},period,
        odata_state='not_attempted_this_quarter' if period==202312 else 'unavailable_in_pilot')
    if not coverage['gate_passed']:raise ValueError(f'New composite coverage failed {period}')
    result_window=reporting_window(period)
    profile={'period':period,'source_mode':quarter['source_mode'],'report_id':table['report']['id'],
        'generation_date':table['report'].get('ge'),'reporting_date':f'{period//100:04d}-12-31',
        'result_window_start':result_window[0],'result_window_end':result_window[1],
        'state_sha256':index['state_manifest']['sha256'],'csv_sha256':index['csv_manifest']['sha256'],
        'raw_directory':str(raw),'coverage':coverage,'columns':table['columns'],
        'limitation':'Result columns accumulate July–December; different generation dates are retained, no Q4 derivation or economic identity asserted'}
    quarter['source_profile']=profile
    quarters[str(period)]=quarter;profiles.append(profile)
output=root/'data/derived/expansion-20261001';output.mkdir(parents=True,exist_ok=True)
composite={'periods':[201012,202312,202412],'institution_type':3,'report_name':'Resumo',
    'raw_directory':str(root),'quarters':quarters,'financial_scope':'IF.data individual Resumo technical comparison; not chosen thesis universe'}
path=output/'collection.json';path.write_text(json.dumps(composite,ensure_ascii=False,indent=2),encoding='utf-8')
summary=replay(path,output/'inventory')
replay(path,output/'replay')
hashes={}
for artifact in (output/'inventory').iterdir():
    if artifact.is_file():
        other=output/'replay'/artifact.name
        if artifact.read_bytes()!=other.read_bytes():raise ValueError('Non-deterministic replay '+artifact.name)
        hashes[artifact.name]=hashlib.sha256(artifact.read_bytes()).hexdigest()
(output/'source-profiles.json').write_text(json.dumps(profiles,ensure_ascii=False,indent=2),encoding='utf-8')
with (output/'source-profiles.csv').open('w',encoding='utf-8-sig',newline='') as handle:
    writer=csv.DictWriter(handle,fieldnames=['period','report_id','generation_date','reporting_date',
        'result_window_start','result_window_end','source_mode','state_sha256','csv_sha256','limitation'],extrasaction='ignore')
    writer.writeheader();writer.writerows(profiles)
index=new['quarters']['202312']['portal_export_index']
diagnostic_files=[p.name for p in (root/new['raw_directory']).glob('portal-failed-*.json')]
statistics={'verified_at_utc':datetime.now(timezone.utc).isoformat(),'original_and_new_raw_manifests_verified':verified,
    'new_raw_manifests':len(new_manifests),'new_raw_body_bytes':sum(m['bytes'] for m in new_manifests),
    'new_http_body_bytes':sum(m['bytes'] for m in new_manifests if m['kind']=='http_response'),
    'export_attempts':new['quarters']['202312']['export_attempts'],'failed_attempt_indices':diagnostic_files,
    'budget':index['budget'],'inventory':summary,'byte_identical_replay_files':len(hashes),'artifact_sha256':hashes,
    'source_profiles':profiles}
(root/'reports/expansion-20261001.verification.json').write_text(json.dumps(statistics,ensure_ascii=False,indent=2),encoding='utf-8')
text='# Resultado local: expansão restrita IF.data\n\n'
text+='Escopo executado: um novo trimestre, 202312, individual/Resumo, pelo portal oficial BCB. Financeiro apenas IF.data; nenhuma decisão de unidade/amostra da tese de capital aberto. Nenhum commit, push ou publicação.\n\n'
text+='| Referência | Instituições | Indicadores | Observações | Estados brutos |\n|---|---:|---:|---:|---|\n'
for period,q in summary['quarters'].items():
    text+=f"| {period} | {q['institutions']} | {q['variables']} | {q['observations']} | {json.dumps(q['value_states'],ensure_ascii=False)} |\n"
text+=f"\n{verified} manifests/corpos verificados; {len(hashes)} arquivos de inventário idênticos após reprodução offline. Novo lote: {statistics['new_raw_body_bytes']:,} bytes brutos ({statistics['new_raw_body_bytes']/1024/1024:.2f} MiB), {statistics['export_attempts']} tentativa(s), {len(diagnostic_files)} índice(s) de falha. Limites: 80 MiB/tentativa, 480 segundos totais/exportação, reserva de150 MiB, até duas tentativas. Guardas não convertem falha em universo vazio.\n\n"
text+='Cadastros REST e tabelas correspondem exatamente nos três snapshots recuperados. Isso não prova universo histórico elegível. OData não foi tentado em202312: modo portal explícito após falhas documentadas no piloto; nenhuma nova afirmação de indisponibilidade OData nesse trimestre. CSV mantém hash/status gerado e arredondamento; valores do inventário vêm dos tokens oficiais da tabela, com seus próprios hashes.\n\n'
text+='Janelas de resultado: julho–dezembro em cada ano; estoques na data de referência. Vintages e IDs brutos preservados em source-profiles.json/csv. Lucro2010/2024 usa IDs diferentes; não afirmar ausência do conceito ou equivalência econômica pela igualdade do rótulo. Nenhuma subtração Q4 ou comparação automática de valores.\n\n'
text+='Dossiê: oito candidatos BB/Bradesco/Itaú Holding e banco, vínculos históricos unknown. Ainda faltam prova jurídica datada e decisões humanas de unidade, janela final e elegibilidade antes de escala.\n'
(root/'reports/expansion-20261001.md').write_text(text,encoding='utf-8')
print(json.dumps({k:v for k,v in statistics.items() if k not in ('source_profiles','artifact_sha256')},ensure_ascii=False))
