"""Export a pinned analytical composition as a self-contained local HTML.

Presentation only: existing joint cells are recomposed algebraically.
No indicator is recalculated. Embedded fractions and distributions stay exact.
"""
import argparse
import base64
import gzip
import hashlib
import json
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


def export(root, pin, output, template):
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
    data = dict(cells=records, cell_contract="joint-cells-compact-v1", monetary_unit="BRL", monetary_scale=1, names=names, companies=companies, formulas=formulas, metric_info=METRIC_INFO,
                adequacy=ADEQUACY, manifest=pin, periods=manifest['periods'], source_counts=manifest['tables'],
                corrections=corrections,
                caixa=dict(periods=['202109', '202112', '202203', '202206']),
                sr_linkage=dict(coverage=sr_coverage, attributes_manifest=manifest['config']['sr']['expected_manifest_sha256'],
                                segmentation_manifest=pin),
                monetary_scale_info=monetary, notes='Presentation recomposes exact persisted joint cells; no indicator recalculation. Company lists are complete.')
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
    output.with_suffix('.receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    connection.close()
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--composition', required=True)
    parser.add_argument('--expected-manifest-sha256', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--template', default=str(Path(__file__).with_name('ifdata-explorer-template.html')))
    args = parser.parse_args()
    print(json.dumps(export(args.composition, args.expected_manifest_sha256, args.output, args.template), ensure_ascii=False))
