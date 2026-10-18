"""Export a pinned analytical composition as a self-contained local HTML.

Presentation only: existing joint cells are recomposed algebraically.
No indicator is recalculated. Embedded fractions and distributions stay exact.
"""
import argparse
import base64
import gzip
import hashlib
import json
import re
from pathlib import Path
import sys
import time

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bank_quality import ifdata_analysis as math


METRIC_INFO = {
    'LA': ['Liquidez contábil / ativo · LA', 'Disponibilidades e aplicações interfinanceiras / ativo; não prova recursos livres ou liquidez sob estresse.'],
    'LC': ['Crédito / ativo · LC', 'Participação do crédito no ativo; não mede qualidade da carteira.'],
    'LF-DEP': ['Depósitos / captações · LF', 'Participação de depósitos nas quatro rubricas conciliadas de captações.'],
    'LF-OC': ['Compromissadas / captações · LF', 'Participação de compromissadas nas captações conciliadas.'],
    'LF-EM': ['Emissões / captações · LF', 'Participação de emissões nas captações conciliadas.'],
    'LF-REP': ['Empréstimos e repasses / captações · LF', 'Participação de empréstimos e repasses nas captações conciliadas.'],
    'RS': ['Serviços / renda selecionada · RS', 'Serviços e tarifas / renda selecionada antes da provisão; não representa toda a receita operacional.'],
    'E3': ['Custos / ativo médio · E3', 'Pessoal e administração / ativo médio; intensidade de custo, distinta de eficiência técnica.'],
    'R4': ['Intermediação / ativo médio · R4', 'Resultado de intermediação / ativo médio; inclui provisão, não é NIM.'],
    'R5': ['Rendas de crédito / crédito médio · R5', 'Rendas de crédito / crédito médio; não é spread líquido nem taxa contratual.'],
}
FORMULAS = {
    'LA': '(disponibilidades + aplicações interfinanceiras) / AT', 'LC': 'crédito / AT',
    'LF-DEP': 'depósitos / captações', 'LF-OC': 'compromissadas / captações',
    'LF-EM': 'emissões / captações', 'LF-REP': 'empréstimos e repasses / captações',
    'RS': '(serviços + tarifas) / (resultado de intermediação − resultado de provisão + serviços + tarifas)',
    'E3': '−(pessoal + administração) / AT médio',
    'R4': 'resultado de intermediação / AT médio', 'R5': 'rendas de crédito / crédito médio',
}
ADEQUACY = {
    'B1': 'Bancos: o mix de crédito, tesouraria e serviços condiciona a comparação.',
    'B2': 'Bancos de investimento/câmbio: crédito e depósitos podem não representar o negócio predominante.',
    'B3S': 'Cooperativas singulares: centralização, regime e benefício ao cooperado exigem análise própria.',
    'B3C': 'Centrais/confederações: centralização e obrigações com filiadas precisam de medidas específicas e controle de sobreposição.',
    'B4': 'Desenvolvimento: LA/LF descrevem composição; não medem maturidade do funding, restrições ou cumprimento do mandato.',
    'N1': 'Não bancárias de crédito: verificar subtipo. Leasing, SCD, SEP e fomento não herdam automaticamente a carteira e o risco dos bancos.',
    'N2': 'Corretoras/distribuidoras: carteira própria difere de custódia; obrigações de clientes e contraparte não estão integralmente medidas.',
    'N4': 'Pagamentos: LA/LF não medem salvaguarda. Recursos elegíveis, contas de usuários, modalidade e liquidação exigem medidas próprias.',
}


def macro_view(row):
    """Labels describe the persisted window; never derive another statistic."""
    s, v, c, method = (row[k] for k in ('series', 'variable', 'category', 'method'))
    source, url = 'IBGE · SIDRA', 'https://sidra.ibge.gov.br/'
    note = 'Contexto Brasil; associação temporal não demonstra causalidade.'
    if s == 'gdp_current_brl_million' and v == '585' and c == '90707' and method in ('official_quarter','sum_four_quarters'):
        label, unit = 'PIB nominal · ' + ('12 meses' if method == 'sum_four_quarters' else 'trimestre'), 'BRL_million'
        note += ' Fluxo em milhões de reais correntes; não é estoque nem PIB real.'
    elif s == 'gdp_official_rates' and c == '90707' and method == 'official_quarter':
        label, unit = 'PIB · ' + {'6561':'variação sobre mesmo trimestre do ano anterior','6562':'variação de quatro trimestres sobre os quatro anteriores','6564':'variação trimestral com ajuste sazonal'}[v], 'percent'
    elif s in ('gdp_volume_and_sectors','gdp_volume_sa') and method == 'official_quarter' and v == ('584' if s == 'gdp_volume_sa' else '583'):
        sector = {'90707':'PIB','90687':'Agropecuária','90691':'Indústria','90696':'Serviços','90697':'Comércio','90700':'Atividades financeiras, seguros e relacionadas'}[c]
        if s == 'gdp_volume_sa' and c != '90707':
            raise ValueError('Unsupported adjusted GDP category')
        label, unit = sector+' · volume'+(' com ajuste sazonal' if s == 'gdp_volume_sa' else ' sem ajuste sazonal'), 'index_1995_mean100'
        note += ' Índice encadeado, média de 1995 = 100; índices setoriais não são aditivos nem lucro bancário.'
    elif s == 'industrial_production' and c == '129314' and method == 'mean_three_months':
        label, unit = 'Produção industrial · média trimestral '+{'12606':'sem ajuste sazonal','12607':'com ajuste sazonal'}[v], 'index_2022_mean100'
        note += ' Média dos três índices mensais; média de 2022 = 100.'
    elif s == 'ipca' and c == 'total' and (v,method) in [('2263','quarter_end_month'),('2265','quarter_end_month'),('2266','quarter_end_month'),('63','compound_three_months')]:
        label = 'IPCA · '+{'2263':'acumulado oficial em 3 meses','2265':'acumulado oficial em 12 meses','2266':'índice no fim do trimestre','63':'3 meses recompostos das taxas mensais'}[v]
        unit = 'index_1993dec100' if v == '2266' else 'percent'
        note += ' Referência: último mês do trimestre. A recomposição pode diferir da taxa oficial pela precisão publicada.'
    elif s == 'labor_income' and c == 'total' and method == 'official_quarter':
        label, unit = {'5929':('Renda média habitual · nominal','BRL_nominal'),'5933':('Renda média habitual · real','BRL_at_latest_quarter_prices')}[v]
        note += ' PNAD trimestral, disponível desde 2012. Renda real aos preços médios do último trimestre divulgado na captura (2026T2), não reais constantes de 2024; não deflacionar novamente.'
    elif s == 'unemployment' and v == '4099' and c == 'total' and method == 'official_quarter':
        label, unit = 'Taxa de desocupação · trimestre civil', 'percent'
        note += ' PNAD disponível desde 2012; 2010–2011 permanecem sem observação, sem emenda com a PME.'
    elif c == 'total' and ((s == 'real_policy_rate_expost' and v == 'Fisher_Selic_IPCA' and method in ('fisher_three_months','fisher_twelve_months')) or (s == 'selic_effective_monthly' and v == 'BM12_TJOVER12' and method in ('compound_three_months','compound_twelve_months'))):
        real = s == 'real_policy_rate_expost'
        label, unit = ('Juro real ex post · Fisher' if real else 'Selic Over efetiva')+' · '+('12 meses' if 'twelve' in method else '3 meses'), 'percent_period'
        source, url = ('Ipeadata/BCB + IBGE · derivado Fisher' if real else 'Ipeadata · fonte BCB/Boletim'), 'https://www.ipeadata.gov.br/api/odata4/Metadados(%27BM12_TJOVER12%27)'
        note += ' Retorno acumulado no período, antes de tributos/custos; não é meta Selic anualizada, custo do crédito, taxa neutra ou expectativa.'
    else:
        raise ValueError('Unsupported macro presentation view')
    if source == 'IBGE · SIDRA':
        url='https://sidra.ibge.gov.br/tabela/'+{'gdp_current_brl_million':'1846','gdp_official_rates':'5932','gdp_volume_and_sectors':'1620','gdp_volume_sa':'1621','industrial_production':'8888','ipca':'1737','labor_income':'6472','unemployment':'6468'}[s]
    if row['unit'] != unit:
        raise ValueError('Macro presentation unit mismatch')
    return dict(key='|'.join((s,v,c,method)), label=label, unit=unit, source=source, url=url, note=note)


def presentation_macro(root, pin, authenticate=None):
    root = Path(root).resolve()
    def auth(path, expected):
        if authenticate is not None:
            authenticate(path, expected)
        elif math._digest_file(path) != expected:
            raise ValueError('Macro presentation input hash mismatch')
    auth(root/'manifest.json',pin)
    manifest = math._json_unique((root/'manifest.json').read_bytes())
    if manifest.get('contract') != 'macro-context-v1':
        raise ValueError('Pinned macro-context-v1 required')
    entries=[e for e in manifest['files'] if e['file']=='quarterly.parquet']
    if len(entries)!=1:
        raise ValueError('Exactly one quarterly macro table required')
    file=math._contained(root,entries[0]['file']);auth(file,entries[0]['sha256'])
    with duckdb.connect(config={'threads':1,'memory_limit':'128MiB'}) as con:
        rows=[math._json_unique(r[0].encode('utf-8')) for r in con.execute('select payload from read_parquet(?)',[str(file)]).fetchall()]
    if len(rows)!=entries[0]['rows']:
        raise ValueError('Macro row count mismatch')
    views,seen={},set()
    for row in rows:
        view=macro_view(row);key=(view['key'],row['period'])
        if key in seen:
            raise ValueError('Duplicate macro period/view')
        seen.add(key);views[view['key']]=view
        if not re.fullmatch(r'20(?:1[0-9]|2[0-4])(?:03|06|09|12)',row['period']):
            raise ValueError('Macro period outside quarterly 2010–2024 window')
        f=row['value_fraction']
        if row['status']=='ok':
            if not isinstance(f,list) or len(f)!=2 or any(not isinstance(x,str) or not re.fullmatch(r'-?\d+',x) for x in f) or int(f[1])<=0:
                raise ValueError('Invalid exact macro fraction')
        elif f is not None:
            raise ValueError('Unavailable macro observation has a value')
    return dict(contract='explorer-macro-v1',manifest=pin,series=list(views.values()),rows=rows)


def prior_correction_derivation(manifest, package):
    """Membership-only children retain the authenticated correction ancestry."""
    seen=set()
    while manifest.get('derivation',{}).get('rule')=='dated_historical_membership_v1':
        source=manifest['derivation']['composition'];key=(source['root'],source['expected_manifest_sha256'])
        if key in seen:raise ValueError('Cyclic presentation correction ancestry')
        seen.add(key);manifest=package(*key)
        if manifest.get('contract')!='ifdata-composed-analysis-v1':raise ValueError('Unexpected correction ancestry contract')
    return manifest.get('derivation',{})


def export(root, pin, output, template, macro_root=None, macro_pin=None):
    root, output, template = Path(root).resolve(), Path(output).resolve(), Path(template).resolve()
    if output.exists() or output.with_suffix('.receipt.json').exists():
        raise FileExistsError(output)
    if root == output or root in output.parents or output in root.parents:
        raise ValueError('HTML destination overlaps composition')
    started = time.perf_counter()
    guards = {}

    def authenticate(path, expected):
        if math._digest_file(path) != expected:
            raise ValueError('Presentation input hash mismatch: ' + path.name)
        s = path.stat()
        guards[path] = (s.st_size, s.st_mtime_ns, s.st_ctime_ns)

    def no_overlap(path):
        if path == output or path in output.parents or output in path.parents:
            raise ValueError('HTML destination overlaps an input package')

    def package(path, expected):
        no_overlap(path)
        authenticate(path / 'manifest.json', expected)
        return math._json_unique((path / 'manifest.json').read_bytes())

    manifest = package(root, pin)
    if manifest.get('contract') != 'ifdata-composed-analysis-v1':
        raise ValueError('Pinned analytical composition required')
    if manifest['config'].get('analytical_company_scope') != 'admitted_associations_2024':
        raise ValueError('Explicit admitted 32-company analytical scope required')
    monetary = manifest.get('monetary_scale_info', {})
    if monetary.get('currency') != 'BRL' or str(monetary.get('native_scale')) != '1':
        raise ValueError('Verified native BRL scale 1 metadata required')
    def guard_sources(value):
        if isinstance(value, dict):
            if isinstance(value.get('root'), str):
                no_overlap(Path(value['root']).resolve())
            for nested in value.values():
                guard_sources(nested)
        elif isinstance(value, list):
            for nested in value:
                guard_sources(nested)
    guard_sources(manifest['config'])
    guard_sources(manifest.get('derivation',{}))
    if (macro_root is None) != (macro_pin is None):
        raise ValueError('Macro package and manifest pin must be supplied together')
    macro = None
    if macro_root is not None:
        macro_root=Path(macro_root).resolve();no_overlap(macro_root)
        macro=presentation_macro(macro_root,macro_pin,authenticate)
    connection = duckdb.connect(config={'threads': 1, 'memory_limit': '256MiB'})

    def table(path, source_manifest, name):
        entries = [e for e in source_manifest['files'] if e['file'] == name + '.parquet']
        if len(entries) != 1:
            raise ValueError('Missing presentation table: ' + name)
        entry = entries[0]
        file = math._contained(path, entry['file'])
        authenticate(file, entry['sha256'])
        cursor = connection.execute('select payload from read_parquet(?)', [str(file)])
        count = 0
        while batch := cursor.fetchmany(128):
            for payload, in batch:
                count += 1
                yield math._json_unique(payload.encode('utf-8'))
        if count != entry['rows']:
            raise ValueError('Presentation row count mismatch')

    # Compact observed joint cells only. Fractions remain exact strings until
    # presentation; browser performs algebraic recomposition, no indicator build.
    records = []
    fields = ('Tcb', 'SegmentoTb', 'Tc', 'Td', 'Sr', 'SrAnalitico')
    count_fields = ('expected_units', 'eligible_units', 'calculable_units',
                    'missing_units', 'unknown_units', 'not_applicable_units')
    def fraction(value):
        return None if value is None else [str(value['numerator']), str(value['denominator'])]
    def stock(r, name, value):
        prefix = 'asset_coverage' if name == 'AT' else 'representation_coverage.' + name
        asset = name == 'AT'
        known = value.get('known_unit_count')
        unknown = value.get('unknown_unit_count')
        negative = value.get('negative_known_unit_count')
        if any(type(count) is not int or count < 0 for count in (known, unknown, negative)):
            raise ValueError('Complete nonnegative integer stock counts required: ' + prefix)
        if negative > known:
            raise ValueError('Negative stock count exceeds known units: ' + prefix)
        return [fraction(value['known_asset_fraction' if asset else 'known_stock_fraction']),
                fraction(value['eligible_known_asset_fraction' if asset else 'eligible_known_stock_fraction']),
                known, unknown, negative]
    seen = set()
    for r in table(root, manifest, 'joint_cells'):
        if r['cohort'] not in ('sample', 'remaining', 'unknown'):
            raise ValueError('Joint cells must use disjoint cohorts')
        if set(r['dimensions']) != set(fields):
            raise ValueError('Six typed joint dimensions required')
        key = json.dumps([r[k] for k in ('period', 'dataset', 'metric', 'horizon', 'cohort')] + [r['dimensions']], sort_keys=True)
        if key in seen:
            raise ValueError('Duplicate joint cell')
        seen.add(key)
        distribution = r['distribution_sorted_fractions']
        if len(distribution) != r['counts']['eligible_units']:
            raise ValueError('Complete eligible joint distribution required')
        company_lists = {k: v for k, v in r['lists'].items() if k.endswith('_companies')}
        weights = r['representation_coverage']
        flags = sorted(set(r['flags']) | set(r['asset_coverage'].get('flags', [])) |
                       set(weights['credit'].get('flags', [])) | set(weights['PL'].get('flags', [])))
        records.append([r[k] for k in ('period', 'dataset', 'metric', 'horizon', 'cohort')] +
            [r['dimensions'], [r['counts'][k] for k in count_fields], company_lists,
             fraction(r['numerator_fraction']), fraction(r['denominator_fraction']), distribution,
             [stock(r, 'AT', r['asset_coverage']), stock(r, 'credit', weights['credit']), stock(r, 'PL', weights['PL'])],
             r['missing_reason_counts'], flags,
             sorted({unit for name in ('missing_units', 'unknown_units', 'diagnostic_units', 'not_applicable_units')
                     for unit in r['lists'].get(name, [])})[:8]])
    membership_spec = manifest['config']['membership']
    membership_root = Path(membership_spec['root']).resolve()
    membership = package(membership_root, membership_spec['expected_manifest_sha256'])
    companies = {r['company_cnpj14']: r['company_name_2024'] for r in table(membership_root, membership, 'companies')}
    needed = {unit for cell in records for unit in cell[14]}
    names, sr_coverage = {}, {}
    for r in table(root, manifest, 'unit_periods'):
        if r['unit_id'] in needed:
            name = (r.get('own_cadastro') or {}).get('NomeInstituicao')
            if isinstance(name, str) and name.strip():
                names[r['unit_id']] = name
        state = r.get('sr_analytic_status')
        if not state:
            raise ValueError('Explicit Sr analytic status is required for every unit')
        group = sr_coverage.setdefault(r['dataset'] + '|' + r['period'], {})
        group[state] = group.get(state, 0) + 1
    profile_path = Path(__file__).resolve().parents[1] / 'bank_quality/ifdata-analysis-universe-profile-2010-2024.json'
    baseline_spec = manifest['config']['baseline']
    baseline = package(Path(baseline_spec['root']).resolve(), baseline_spec['expected_manifest_sha256'])
    authenticate(profile_path, baseline['profile_sha256'])
    profile = math._json_unique(profile_path.read_bytes())
    formulas = {k: v['formula_documentation'] for k, v in profile['metrics'].items()}
    formulas.update(FORMULAS)
    template_pin = math._digest_file(template)
    authenticate(template, template_pin)
    corrections = []
    for spec in manifest['config']['corrections']:
        source = package(Path(spec['root']).resolve(), spec['expected_manifest_sha256'])
        scope = source['scope']
        if 'period' in scope and scope['period'].startswith('2019'):
            issue = 138 if scope['dataset'] == 'individual' else 137 if scope['metric'] == 'R2' else 133 if scope['period'] == '201903' else 134
            corrections.append(dict(issue=issue, scope=[scope[k] for k in ('period','dataset','metric','horizon')],
                                    manifest=spec['expected_manifest_sha256'], note='Ponte nativa delimitada de 2019; exceções e perímetros preservados.'))
    derivation=prior_correction_derivation(manifest,lambda root,pin:package(Path(root).resolve(),pin))
    if derivation.get('rule')=='terra-individual-history-financial-202412-v1':
        spec=derivation['patch'];source=package(Path(spec['root']).resolve(),spec['expected_manifest_sha256'])
        corrections.append(dict(issue=154,scope=['202412','financial','Terra','quarter/ttm'],manifest=spec['expected_manifest_sha256'],
            note='Ponte finita Terra: histórico Individual 4T2023–3T2024; corrente Financeiro preservado. Originais mantidos no pacote. Não preenche os 21 períodos sem unidade Financeiro; crédito zero mantém Q2/R5 indefinidos.'))
    data = dict(cells=records, cell_contract="joint-cells-compact-v1", monetary_unit="BRL", monetary_scale=1, names=names, companies=companies, formulas=formulas, metric_info=METRIC_INFO,
                adequacy=ADEQUACY, manifest=pin, periods=manifest['periods'], source_counts=manifest['tables'],
                corrections=corrections,
                historical_membership=manifest.get('derivation',{}).get('rule')=='dated_historical_membership_v1',
                caixa=dict(periods=['202109', '202112', '202203', '202206']),
                sr_linkage=dict(coverage=sr_coverage, attributes_manifest=manifest['config']['sr']['expected_manifest_sha256'],
                                segmentation_manifest=pin),
                monetary_scale_info=monetary, notes='Presentation recomposes exact persisted joint cells; no indicator recalculation. Company lists are complete.')
    if macro is not None:
        data['macro']=macro
    packed = base64.b64encode(gzip.compress(json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), mtime=0)).decode('ascii')
    html = template.read_text(encoding='utf-8')
    if html.count('__PACKED_DATA__') != 1:
        raise ValueError('Presentation template placeholder mismatch')
    for path, before in guards.items():
        s = path.stat()
        if before != (s.st_size, s.st_mtime_ns, s.st_ctime_ns):
            raise ValueError('Presentation input changed during export')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html.replace('__PACKED_DATA__', packed), encoding='utf-8')
    receipt = dict(html_sha256=math._digest_file(output), html_bytes=output.stat().st_size,
                   composition_manifest_sha256=pin, template_sha256=template_pin,
                   exporter_sha256=math._digest_file(Path(__file__)), rows=len(records), companies=len(companies),
                   elapsed_seconds=time.perf_counter()-started)
    if macro is not None:
        receipt['macro_manifest_sha256']=macro_pin
        receipt['macro_rows']=len(macro['rows'])
    output.with_suffix('.receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    connection.close()
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--composition', required=True)
    parser.add_argument('--expected-manifest-sha256', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--template', default=str(Path(__file__).with_name('ifdata-explorer-template.html')))
    parser.add_argument('--macro-context')
    parser.add_argument('--macro-manifest-sha256')
    args = parser.parse_args()
    print(json.dumps(export(args.composition, args.expected_manifest_sha256, args.output, args.template,args.macro_context,args.macro_manifest_sha256), ensure_ascii=False))
