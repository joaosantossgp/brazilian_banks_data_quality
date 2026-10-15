"""Causal population tests using small authenticated native packages."""
import copy
import csv
import hashlib
import importlib
import json
from pathlib import Path
import tempfile
import unittest

import duckdb

from bank_quality.ifdata_cadastro import FIELDS, ORIGIN, CONTRACT as CAD_CONTRACT
from bank_quality.ifdata_odata import COLUMNS, CONTRACT as DATA_CONTRACT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, obj):
    path.write_text(json.dumps(obj, sort_keys=True, ensure_ascii=False) + '\n', encoding='utf-8')


def package(root, fields, rows, contract, period='202412', native_type=None):
    root.mkdir()
    part = root / 'part.parquet'
    with duckdb.connect(config={'memory_limit': '512MiB', 'threads': 1}) as conn:
        conn.execute('create table native (' + ','.join('"'+f+'" VARCHAR' for f in fields) + ')')
        if rows:
            conn.executemany('insert into native values ('+','.join('?' for _ in fields)+')',
                             [[r.get(f) for f in fields] for r in rows])
        conn.execute('copy native to ? (format parquet)', [str(part)])
    entry = dict(file=part.name, sha256=digest(part), rows=len(rows), period=period)
    if native_type is not None:
        entry['type'] = int(native_type)
    manifest = dict(contract=contract, rows=len(rows), files=[entry])
    dump(root / 'manifest.json', manifest)
    return dict(root=str(root), expected_manifest_sha256=digest(root / 'manifest.json'))


def cadastro(code, parent=None, prudential=None, **extra):
    return dict(CodInst=code, Data='202412', NomeInstituicao='literal '+code,
                CodConglomeradoFinanceiro=parent, CodConglomeradoPrudencial=prudential,
                Td='I', source_sha256='a'*64, source_row=code, **extra)


def value(code, ti='3', account='account', saldo=None):
    return dict(TipoInstituicao=ti, CodInst=code, AnoMes='202412', Conta=account,
                NumeroRelatorio='7', Saldo=saldo, source_sha256='b'*64,
                source_row=code or 'null', source_file='native.gz')


class PopulationTests(unittest.TestCase):
    def setUp(self):
        try:
            self.api = importlib.import_module('bank_quality.ifdata_population')
        except ModuleNotFoundError:
            self.api = None
        self.assertIsNotNone(self.api, 'Missing population API: implement the released population contract')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def fixture(self, rows=None, cad=None, datasets=None, missing_company=False):
        # Twenty-four declared companies, two of which share a financial unit.
        maps = [dict(company_cnpj14='company-'+str(i), company_name_2024='company '+str(i),
                     period='202412', native_target_code='F', operator_base8='O', native_cadastro={})
                for i in range(24)]
        if missing_company:
            maps[-1]['native_target_code'] = None
            maps[-1]['operator_base8'] = None
        sample = self.root / 'sample'; sample.mkdir()
        for name, obj in [('company-quarter-map.json', maps), ('annual-verification.json', []),
                          ('complementary-annual-verification.json', {'rows': []})]:
            dump(sample / name, obj)
        dump(sample / 'manifest.json', dict(schema=1, issue=125,
             files={p.name:digest(p) for p in sample.iterdir()}))
        inputs = {'sample': dict(root=str(sample), expected_manifest_sha256=digest(sample/'manifest.json'))}
        cad = cad if cad is not None else [cadastro('F','F','P'), cadastro('O','F','P'),
               cadastro('P','F','P'), cadastro('M','F','P', Sr=None, Tcb=''),
               cadastro('B','X','Q'), cadastro('X','X','Q'), cadastro('Q','X','Q'), cadastro('N')]
        inputs['cadastro'] = package(self.root/'cadastro', FIELDS+ORIGIN, cad, CAD_CONTRACT)
        datasets = datasets or {'individual': rows if rows is not None else [value('M'),value('B'),value('N')]}
        for ds, vs in datasets.items():
            inputs[ds] = package(self.root/ds, COLUMNS, vs, DATA_CONTRACT,
                                 native_type={'financial':'2','individual':'3','capital':'1','segmentation':'1'}[ds])
        catalog = self.root / 'catalogue'; catalog.mkdir()
        dump(catalog/'catalogue.json', [])
        dump(catalog/'manifest.json', dict(contract='ifdata-variable-catalog-v1',
              inputs={ds:dict(manifest_sha256=inputs[ds]['expected_manifest_sha256']) for ds in datasets},
              files=[dict(file='catalogue.json', sha256=digest(catalog/'catalogue.json'))]))
        inputs['catalogue'] = dict(root=str(catalog), expected_manifest_sha256=digest(catalog/'manifest.json'))
        return dict(periods=['202412'], datasets=sorted(datasets), inputs=inputs)

    def build(self, cfg):
        out = self.root/'output'
        manifest = self.api.build_population(cfg, out)
        with self.api.open_population(out, digest(out/'manifest.json')) as conn:
            rows = [json.loads(x[0]) for x in conn.execute('select payload from unit_periods order by unit_id').fetchall()]
        return manifest, rows

    def test_partition_deduplicates_companies_and_preserves_conflicts(self):
        rows = [dict(unit_id='A', membership='sample', company_id='one'),
                dict(unit_id='A', membership='sample', company_id='two'),
                dict(unit_id='B', membership='remaining'),dict(unit_id='C', membership='unknown')]
        self.assertEqual(self.api.partition_membership(rows),
                         {'total':{'A','B','C'},'sample':{'A'},'remaining':{'B'},'unknown':{'C'}})
        rows.append(dict(unit_id='A',membership='remaining'))
        self.assertEqual(self.api.partition_membership(rows)['unknown'], {'A','C'})
        with self.assertRaises(ValueError):
            self.api.partition_membership([dict(unit_id='A',membership='invalid')])

    def test_native_positive_negative_and_null_without_metric_values(self):
        manifest, rows = self.build(self.fixture())
        by = {r['code']:r for r in rows}
        self.assertEqual({c:r['membership'] for c,r in by.items()}, {'M':'sample','B':'remaining','N':'unknown'})
        self.assertEqual(by['M']['classifications']['Sr'], None)
        self.assertEqual(by['M']['classifications']['Tcb'], '')
        self.assertEqual(len(manifest['matrices'][0]['company_rows']),24)
        self.assertEqual(by['B']['matrix_id'],'financial|202412')
        self.assertEqual(by['M']['aggregate_selection_status'],'technical_occurrence_only')
        self.assertEqual(manifest['tables']['unit_periods'],3)

    def test_partial_company_matrix_keeps_positive_but_prevents_negative(self):
        manifest, rows = self.build(self.fixture(missing_company=True))
        self.assertEqual({r['code']:r['membership'] for r in rows}, {'M':'sample','B':'unknown','N':'unknown'})
        self.assertEqual(len(manifest['company_map_missing']),2)
        self.assertFalse(manifest['matrices'][0]['financial_complete'])

    def test_coincident_code_is_not_an_individual_link(self):
        cfg = self.fixture([value('F')], [cadastro('F'),cadastro('O')])
        _, rows = self.build(cfg)
        self.assertEqual(rows[0]['membership'],'unknown')

    def test_operator_proof_conflict_and_cycle_are_unknown(self):
        cfg = self.fixture([value('O'),value('M')], [cadastro('F','F'),cadastro('O','X'),
                           cadastro('X','X'),cadastro('M','A'),cadastro('A','Z'),cadastro('Z','A')])
        _, rows = self.build(cfg)
        by={r['code']:r for r in rows}
        self.assertEqual(by['O']['membership_reason'],'operator_target_parent_conflict')
        self.assertEqual(by['M']['membership_reason'],'cycle')

    def test_prudential_target_absence_member_presence_and_namespace(self):
        cfg=self.fixture(datasets={'capital':[value('M','1')], 'segmentation':[value('P','1')]})
        manifest, rows=self.build(cfg)
        self.assertEqual([r['membership'] for r in rows],['sample','sample'])
        self.assertEqual(len({r['unit_id'] for r in rows}),2)
        self.assertEqual({r['perspective'] for r in rows},{'prudential'})
        self.assertEqual({r['aggregate_selection_status'] for r in rows},{'prudential_overlap_unproven'})
        self.assertFalse(manifest['matrices'][0]['target_values_presence']['capital']['P'])
        self.assertTrue(manifest['matrices'][0]['target_values_presence']['segmentation']['P'])

    def test_report_rubrics_do_not_multiply_unit_and_null_is_nominal_diagnostic(self):
        cfg=self.fixture([value('M'),value('M',account='other'),value(None,saldo='1.00')])
        manifest, rows=self.build(cfg)
        self.assertEqual(len(rows),1)
        self.assertEqual(manifest['null_identities'][0]['Saldo'],'1.00')
        self.assertEqual(manifest['null_identities'][0]['CodInst'],None)
        self.assertNotIn('unit_id',manifest['null_identities'][0])

    def test_native_aggregate_without_proof_is_not_automatically_removed(self):
        _, rows=self.build(self.fixture([value('TOTAL')],[cadastro('TOTAL')]))
        self.assertEqual(rows[0]['code'],'TOTAL')
        self.assertEqual(rows[0]['aggregate_selection_status'],'technical_occurrence_only')

    def test_duplicate_cadastro_refuses_ambiguous_historical_classification(self):
        cfg=self.fixture(cad=[cadastro('M',Sr='S1'),cadastro('M',Sr='S2')])
        with self.assertRaisesRegex(ValueError,'Duplicate.*cadastro'):
            self.api.build_population(cfg,self.root/'output')

    def test_duplicate_native_occurrence_is_rejected(self):
        cfg=self.fixture([value('M'),value('M')])
        with self.assertRaisesRegex(ValueError,'Duplicate native'):
            self.api.build_population(cfg,self.root/'output')

    def test_wrong_native_perspective_is_rejected(self):
        cfg=self.fixture([value('M','2')])
        with self.assertRaisesRegex(ValueError,'type'):
            self.api.build_population(cfg,self.root/'output')

    def test_source_tampering_and_external_lineage_are_rejected(self):
        cfg=self.fixture()
        cfg['inputs']['individual']['expected_manifest_sha256']='0'*64
        with self.assertRaises(ValueError):self.api.build_population(cfg,self.root/'output')
        self.assertFalse((self.root/'output'/'manifest.json').exists())

    def test_catalogue_lineage_not_newly_computed_digest(self):
        cfg=self.fixture()
        r=Path(cfg['inputs']['catalogue']['root']); m=json.loads((r/'manifest.json').read_text())
        m['inputs']['individual']['manifest_sha256']='0'*64;dump(r/'manifest.json',m)
        cfg['inputs']['catalogue']['expected_manifest_sha256']=digest(r/'manifest.json')
        with self.assertRaisesRegex(ValueError,'lineage'):self.api.build_population(cfg,self.root/'output')

    def test_bad_configs_rejected_before_output(self):
        cfg=self.fixture()
        for change in [dict(periods=['202412','202412']),dict(periods=['202503']),
                       dict(datasets=['individual','individual']),dict(typo=True)]:
            with self.subTest(change=change),self.assertRaises(ValueError):
                self.api.build_population(dict(cfg,**change),self.root/'output')
        self.assertFalse((self.root/'output').exists())

    def test_missing_source_period_is_distinct_from_empty_population(self):
        cfg=self.fixture();cfg['periods']=['202409','202412']
        sample=Path(cfg['inputs']['sample']['root']);maps=json.loads((sample/'company-quarter-map.json').read_text())
        maps += [dict(r,period='202409',native_target_code=None,operator_base8=None) for r in maps]
        dump(sample/'company-quarter-map.json',maps)
        m=json.loads((sample/'manifest.json').read_text());m['files']['company-quarter-map.json']=digest(sample/'company-quarter-map.json');dump(sample/'manifest.json',m)
        cfg['inputs']['sample']['expected_manifest_sha256']=digest(sample/'manifest.json')
        manifest,_=self.build(cfg)
        absent=next(r for r in manifest['periods'] if r['period']=='202409')
        self.assertEqual(absent['population_state'],'source_period_not_captured')
        self.assertEqual(absent['observed_identified_total'],0)

    def test_replay_order_and_authenticated_cross_format_disagreement(self):
        cfg=self.fixture()
        self.api.build_population(cfg,self.root/'output')
        cfg['periods']=list(reversed(cfg['periods']));cfg['datasets']=list(reversed(cfg['datasets']))
        self.api.build_population(cfg,self.root/'replay')
        for name in ('unit_periods.json','unit_periods.csv','unit_periods.parquet',
                     'membership_links.json','membership_links.csv','membership_links.parquet','manifest.json'):
            self.assertEqual((self.root/'output'/name).read_bytes(),(self.root/'replay'/name).read_bytes(),name)
        with self.assertRaises(FileExistsError):self.api.build_population(cfg,self.root/'output')
        out=self.root/'output';rows=json.loads((out/'unit_periods.json').read_text());rows[0]['membership']='sample' if rows[0]['membership']!='sample' else 'remaining';dump(out/'unit_periods.json',rows)
        manifest=json.loads((out/'manifest.json').read_text())
        for entry in manifest['files']:
            if entry['file']=='unit_periods.json':entry['sha256']=digest(out/'unit_periods.json')
        dump(out/'manifest.json',manifest)
        with self.assertRaisesRegex(ValueError,'disagree'):
            self.api.open_population(out,digest(out/'manifest.json'))

    def test_native_payload_and_schema_tampering_are_rejected(self):
        cfg=self.fixture()
        part=Path(cfg['inputs']['individual']['root'])/'part.parquet'
        with part.open('ab') as stream:stream.write(b'tampered')
        with self.assertRaisesRegex(ValueError,'hash'):
            self.api.build_population(cfg,self.root/'output')

    def test_authenticated_wrong_textual_schema_is_rejected(self):
        cfg=self.fixture()
        other=self.root/'other'
        wrong=package(other,('TipoInstituicao','CodInst','AnoMes'),[value('M')],DATA_CONTRACT,native_type='3')
        cfg['inputs']['individual']=wrong
        catalog=Path(cfg['inputs']['catalogue']['root']);m=json.loads((catalog/'manifest.json').read_text())
        m['inputs']['individual']['manifest_sha256']=wrong['expected_manifest_sha256'];dump(catalog/'manifest.json',m)
        cfg['inputs']['catalogue']['expected_manifest_sha256']=digest(catalog/'manifest.json')
        with self.assertRaisesRegex(ValueError,'schema'):
            self.api.build_population(cfg,self.root/'output')

    def test_missing_own_parent_and_selected_ancestor_preserve_unknown(self):
        cfg=self.fixture([value('no-own'),value('M'),value('A')],
            [cadastro('F','F'),cadastro('O','F'),cadastro('M','missing'),
             cadastro('A','X'),cadastro('X','F')])
        _,rows=self.build(cfg)
        self.assertEqual({r['code']:r['membership_reason'] for r in rows},
            {'no-own':'missing_own_cadastro','M':'missing_parent_cadastro','A':'selected_ancestor_requires_scope'})

    def test_graph_copresence_is_diagnostic_and_never_selects_roots(self):
        cfg=self.fixture(datasets={'capital':[value('P','1'),value('M','1')]})
        manifest,rows=self.build(cfg)
        self.assertEqual(len(rows),2)
        self.assertEqual([r['membership'] for r in rows],['sample','sample'])
        self.assertEqual(manifest['parent_copresence'][0]['selection'],'diagnostic_only')
        self.assertEqual(manifest['parent_copresence'][0]['parent_code'],'P')

    def test_same_code_different_datasets_retains_two_native_keys(self):
        cfg=self.fixture(datasets={'financial':[value('F','2')],'individual':[value('F','3')]},
            cad=[cadastro('F'),cadastro('O')])
        _,rows=self.build(cfg)
        self.assertEqual({r['unit_id']:r['membership'] for r in rows},
            {'financial|2|F|202412':'sample','individual|3|F|202412':'unknown'})

    def test_graph_diagnostics_include_cycle_without_copresent_parent(self):
        cfg=self.fixture(datasets={'financial':[value('A','2')]},
            cad=[cadastro('F','F'),cadastro('O','F'),cadastro('A','X'),cadastro('X','Z'),cadastro('Z','X')])
        _,rows=self.build(cfg)
        self.assertEqual(rows[0].get('native_graphs',{}).get('financial',{}).get('state'),'cycle')
        self.assertEqual(rows[0]['membership'],'remaining')

    def test_open_rejects_pin_and_unlisted_files(self):
        cfg=self.fixture();self.api.build_population(cfg,self.root/'output');out=self.root/'output'
        with self.assertRaises(ValueError):self.api.open_population(out,'0'*64)
        (out/'unlisted.txt').write_text('unlisted')
        with self.assertRaisesRegex(ValueError,'Unlisted'):
            self.api.open_population(out,digest(out/'manifest.json'))

    def test_null_occurrences_are_not_duplicate_unit_keys(self):
        cfg=self.fixture([value('M'),value(None,saldo='1.00'),value(None,saldo='2.00')])
        try:
            manifest,rows=self.build(cfg)
        except ValueError as exc:
            self.fail('Null diagnostic rows must not be rejected as duplicate unit keys: '+str(exc))
        self.assertEqual(len(rows),1)
        self.assertEqual([r['Saldo'] for r in manifest['null_identities']],['1.00','2.00'])

    def test_each_part_count_is_verified_not_only_balanced_quarter_total(self):
        cfg=self.fixture()
        root=Path(cfg['inputs']['individual']['root']);m=json.loads((root/'manifest.json').read_text())
        original=m['files'][0];other=root/'other.parquet';other.write_bytes((root/original['file']).read_bytes())
        original['rows']=4;m['files'].append(dict(original,file='other.parquet',rows=2));m['rows']=6
        dump(root/'manifest.json',m);cfg['inputs']['individual']['expected_manifest_sha256']=digest(root/'manifest.json')
        catalog=Path(cfg['inputs']['catalogue']['root']);cm=json.loads((catalog/'manifest.json').read_text())
        cm['inputs']['individual']['manifest_sha256']=cfg['inputs']['individual']['expected_manifest_sha256'];dump(catalog/'manifest.json',cm)
        cfg['inputs']['catalogue']['expected_manifest_sha256']=digest(catalog/'manifest.json')
        with self.assertRaisesRegex(ValueError,'part count'):
            self.api.build_population(cfg,self.root/'output')

    def test_parquet_row_groups_bound_wide_population_materialization(self):
        cfg=self.fixture([value('outside-'+str(i)) for i in range(2050)])
        self.api.build_population(cfg,self.root/'output')
        with duckdb.connect(config={'memory_limit':'512MiB','threads':1}) as conn:
            for table in ('unit_periods','membership_links'):
                maximum=conn.execute('select max(row_group_num_rows) from parquet_metadata(?)',
                    [str(self.root/'output'/(table+'.parquet'))]).fetchone()[0]
                self.assertLessEqual(maximum,2048)

    def rewrite_population_table(self, out, table, rows):
        """Create internally consistent repinned formats, not ordinary tampering."""
        columns=self.api.TABLE_COLUMNS[table]
        (out/(table+'.json')).write_text(json.dumps(rows,sort_keys=True)+'\n',encoding='utf-8')
        values=[[row.get(k) for k in columns[:-1]]+
                [json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(',',':'))] for row in rows]
        with (out/(table+'.csv')).open('w',encoding='utf-8',newline='') as stream:
            writer=csv.writer(stream,quoting=csv.QUOTE_NOTNULL);writer.writerow(columns);writer.writerows(values)
        with duckdb.connect(config={'memory_limit':'512MiB','threads':1}) as conn:
            conn.execute('create table rewritten ('+','.join('"'+c+'" VARCHAR' for c in columns)+')')
            if values:
                conn.executemany('insert into rewritten values ('+','.join('?' for _ in columns)+')',values)
            parquet=out/(table+'.parquet');parquet.unlink()
            conn.execute('copy rewritten to ? (format parquet)',[str(parquet)])
        manifest=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
        manifest['tables'][table]=len(rows)
        for entry in manifest['files']:
            if entry['file'].startswith(table+'.'):
                entry.update(rows=len(rows),sha256=digest(out/entry['file']))
        dump(out/'manifest.json',manifest)
        return digest(out/'manifest.json')

    def test_open_requires_a_decision_link_for_every_unit(self):
        cfg=self.fixture();out=self.root/'output';self.api.build_population(cfg,out)
        links=json.loads((out/'membership_links.json').read_text(encoding='utf-8'))
        for label,remaining in [('all_missing',[]),('one_missing',[r for r in links if '|N|' not in r['unit_id']])]:
            with self.subTest(case=label):
                pin=self.rewrite_population_table(out,'membership_links',remaining)
                with self.assertRaisesRegex(ValueError,'Membership.*reconciliation'):
                    with self.api.open_population(out,pin):pass

    def test_open_requires_matching_link_identity_fields(self):
        cfg=self.fixture();out=self.root/'output';self.api.build_population(cfg,out)
        links=json.loads((out/'membership_links.json').read_text(encoding='utf-8'))
        for field,value in [('dataset','capital'),('period','202409'),('matrix_id','prudential|202412'),
                            ('membership','unknown'),('relation','different_reason'),('link_id','different_identity')]:
            with self.subTest(field=field):
                changed=copy.deepcopy(links);changed[0][field]=value
                pin=self.rewrite_population_table(out,'membership_links',changed)
                with self.assertRaisesRegex(ValueError,'Membership.*reconciliation'):
                    with self.api.open_population(out,pin):pass

    def test_open_requires_exact_sample_company_set(self):
        cfg=self.fixture();out=self.root/'output';self.api.build_population(cfg,out)
        links=json.loads((out/'membership_links.json').read_text(encoding='utf-8'))
        sample=[r for r in links if r['membership']=='sample'];self.assertEqual(len(sample),24)
        omitted=[r for r in links if r['link_id']!=sample[0]['link_id']]
        extra=copy.deepcopy(sample[0]);extra['company_id']='not-declared';extra['link_id']=extra['unit_id']+'|not-declared'
        for label,changed in [('omitted_company',omitted),('extra_company',links+[extra])]:
            with self.subTest(case=label):
                pin=self.rewrite_population_table(out,'membership_links',changed)
                with self.assertRaisesRegex(ValueError,'Membership.*reconciliation'):
                    with self.api.open_population(out,pin):pass

    def test_open_requires_one_null_company_decision_for_non_sample(self):
        cfg=self.fixture();out=self.root/'output';self.api.build_population(cfg,out)
        links=json.loads((out/'membership_links.json').read_text(encoding='utf-8'))
        for state in ('remaining','unknown'):
            with self.subTest(state=state):
                changed=copy.deepcopy(links)
                row=next(r for r in changed if r['membership']==state)
                row['company_id']='unproven';row['link_id']=row['unit_id']+'|unproven'
                pin=self.rewrite_population_table(out,'membership_links',changed)
                with self.assertRaisesRegex(ValueError,'Membership.*reconciliation'):
                    with self.api.open_population(out,pin):pass


if __name__=='__main__':unittest.main()
