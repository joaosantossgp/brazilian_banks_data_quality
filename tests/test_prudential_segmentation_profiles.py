"""Synthetic prudential metadata archives; no local data/ dependency or real C."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bank_quality import financial_report_profiles as profiles

SELECTION = {'period': 202312, 'perspective': 1009, 'reports': [102]}
# Hand-checked native column/ifd/td/area/lid/fid associations.
BINDINGS = [(17989,79670,1,1,2,8),(17990,79706,1,1,0,9),
 (17991,79671,1,1,3,1),(17992,79675,1,1,4,1),(17993,79676,1,1,6,1),
 (17994,79672,1,1,11,1),(17995,79673,1,1,10,1),(17996,79678,1,1,1,14),
 (17997,79707,3,1,85843,16),(17998,79708,3,1,85844,16),(17999,79709,3,1,85845,16),
 (18000,79710,3,1,86846,13),(18001,79711,3,1,87071,11),(18002,79679,1,1,12,1),
 (18003,79730,1,1,31,1)]

def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()

def sha(body):
    return hashlib.sha256(body).hexdigest()

class PrudentialMetadataTests(unittest.TestCase):
    def setUp(self):
        # Missing API is a clear assertion failure in the pre-implementation RED.
        self.assertTrue(callable(getattr(profiles, 'author_prudential_metadata', None)),
                        'Prudential metadata authoring is absent')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        files = [{} for _ in range(14)]
        for index, name in ((2,'cadastro202312_1009'),(9,'info202312'),(3,'dados202312_1')):
            files[index] = {'f': 'ifdata/202312/' + name + '.json'}
        files[13] = {'trel': {'id':102,'s':[{'id':1009}], 'rp':[{'note':'synthetic'}],
            'c':[{'id':col,'ifd':ifd,'fid':fid,'sc':[]} for col,ifd,td,area,lid,fid in BINDINGS]}}
        catalog = [{} for _ in range(96)]
        catalog[95] = {'dt':202312,'files':files}
        dictionary = [{'id':ifd,'td':td,'a':area,'lid':lid,'n':'Synthetic '+str(col)}
                      for col,ifd,td,area,lid,fid in BINDINGS]
        self.payloads = {'catalog':catalog,'dictionary':dictionary,'numeric:1':{'id':1,'values':[]},'portal':b'synthetic portal'}
        self.pins = {}
        for sid, payload in self.payloads.items():
            self.archive(sid, payload)
        self.addCleanup(patch.stopall)
        patch.object(profiles, 'CHECKOUT_ROOT', self.root).start()
        patch.object(profiles, '_PRUDENTIAL_METADATA_PINS', self.pins).start()

    def archive(self, sid, payload):
        body = payload if isinstance(payload, bytes) else encoded(payload)
        name = sid.replace(':','-')
        path = self.root / 'data/raw/synthetic' / (name+'.json')
        path.parent.mkdir(parents=True, exist_ok=True)
        (path.parent / (name+'.bin')).write_bytes(body)
        url = ('https://www3.bcb.gov.br/ifdata/rest/relatorios2000a2024' if sid=='catalog'
               else 'https://www3.bcb.gov.br/ifdata/index.html' if sid=='portal'
               else 'https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata/202312/' +
                    ('info202312.json' if sid=='dictionary' else 'dados202312_1.json'))
        manifest = {'url':url,'final_url':url,'method':'GET','http_status':200,'outcome':'ok',
            'bytes':len(body),'sha256':sha(body),'body_path':name+'.bin',
            'retrieved_at_utc':'2026-10-01T03:37:20.509Z','response_headers':{'Content-Length':str(len(body))},
            'context':{'period':202312,'body_capture':'Intercepted official response bytes before browser fulfillment'},
            'diagnostics':['Playwright stores decoded response-body bytes'] if sid in ('dictionary','numeric:1') else []}
        if sid in ('catalog','portal'):
            manifest['truncated'] = False
        path.write_bytes(encoded(manifest))
        self.pins[sid] = {'manifest_path':path.relative_to(self.root).as_posix(),
                         'manifest_sha256':sha(path.read_bytes()),'body_sha256':sha(body),'bytes':len(body)}

    def author(self, selection=None):
        return profiles.author_prudential_metadata(SELECTION if selection is None else selection)

    def test_deterministic_incomplete_metadata_retains_native_bindings(self):
        result = self.author()
        self.assertEqual(result, self.author())
        self.assertEqual(result['contract'], 'ifdata-prudential-metadata-candidate-v1')
        self.assertEqual(result['selection'], SELECTION)
        self.assertEqual(result['missing_sources'], ['cadaster'])
        self.assertEqual(result['required_sources'], ['cadaster','catalog','dictionary','numeric:1','portal'])
        for key in ('cadaster_columns','cadaster_fields','population','grid','accepted','profile_path'):
            self.assertNotIn(key, result)
        nodes = result['reports'][0]['nodes']
        self.assertEqual([(n['column_id'],n['ifd'],n['td'],n['area'],n['lid'],n['fid']) for n in nodes], BINDINGS)
        self.assertEqual([n['definition_pointer'] for n in nodes], ['/'+str(i) for i in range(15)])
        self.assertEqual([n['catalog_pointer'] for n in nodes], ['/95/files/13/trel/c/'+str(i) for i in range(15)])
        legacy = result['source_members']['dictionary']
        self.assertEqual(legacy['truncation_state'], 'undeclared_legacy')
        self.assertNotIn('truncated', legacy)
        self.assertEqual(legacy['diagnostics'], ['Playwright stores decoded response-body bytes'])
        self.assertEqual(legacy['retrieved_at_original'], '2026-10-01T03:37:20.509Z')

    def test_semantics_keep_flags_and_currencies_separate_from_origin(self):
        nodes = {n['column_id']:n for n in self.author()['reports'][0]['nodes']}
        for col in (17989,17990,17991,17992,17993,17994,17995,17996,18002,18003):
            n = nodes[col]
            self.assertEqual((n['origin_kind'],n['kind'],n['unit'],n['encoding']),
                             ('cadaster','attribute','not_applicable','utf8_string_exact_v1'))
        for col in (17997,17998,17999):
            n = nodes[col]
            self.assertEqual((n['origin_kind'],n['kind'],n['unit'],n['encoding']),
                             ('numeric','flag','not_applicable','json_native_token_v1'))
            self.assertEqual(n['presentation'], {'labels':['Sim','Não']})
        for col, currency in ((18000,'BRL'),(18001,'USD')):
            n = nodes[col]
            self.assertEqual((n['kind'],n['unit'],n['encoding']), ('numeric_measure','unknown','json_native_token_v1'))
            self.assertEqual(n['presentation'], {'currency':currency,'scale':'mil'})
            self.assertEqual((n['raw_currency'],n['raw_scale']), ('unknown','unknown'))

    def test_namespace_selection_and_caller_trust_overrides_rejected(self):
        for selection in ({**SELECTION,'perspective':1005},{**SELECTION,'perspective':1006},
                          {**SELECTION,'period':202412},{**SELECTION,'reports':[102,102]},
                          {**SELECTION,'reports':[103]},{**SELECTION,'period':True},
                          {**SELECTION,'family':'Capital'}):
            with self.subTest(selection=selection), self.assertRaises(ValueError):
                self.author(selection)
        with self.assertRaises(TypeError):
            profiles.author_prudential_metadata(SELECTION, sources=self.pins)
        for loader in (profiles.load_installed_context, profiles.load_individual_context):
            with self.assertRaises(ValueError):
                loader(SELECTION)

    def test_reports_tuple_is_rejected_before_json_normalization(self):
        with self.assertRaises(ValueError):
            self.author({**SELECTION, 'reports':(102,)})

    def test_mutated_physical_bytes_cannot_be_authorized_by_caller(self):
        for sid in self.pins:
            path = self.root / self.pins[sid]['manifest_path']
            original = path.read_bytes()
            path.write_bytes(original+b' ')
            with self.subTest(sid=sid), self.assertRaises(ValueError):
                self.author()
            path.write_bytes(original)
        path = self.root / self.pins['dictionary']['manifest_path']
        body_path = path.parent / json.loads(path.read_bytes())['body_path']
        body_path.write_bytes(b'[]')
        with self.assertRaises(ValueError):
            self.author()

    def test_invalid_native_offer_and_binding_trees_fail_even_when_fixture_repinned(self):
        for mode in ('reference','perspective','report','duplicate-column','duplicate-definition',
                     'missing-definition','origin','area','negative-cadaster-lid','file-pointer'):
            with self.subTest(mode=mode):
                catalog = copy.deepcopy(self.payloads['catalog'])
                dictionary = copy.deepcopy(self.payloads['dictionary'])
                report = catalog[95]['files'][13]['trel']
                if mode=='reference': catalog[95]['dt']=202412
                elif mode=='perspective': report['s']=[{'id':1005}]
                elif mode=='report': report['id']=103
                elif mode=='duplicate-column': report['c'].append(copy.deepcopy(report['c'][0]))
                elif mode=='duplicate-definition': dictionary.append(copy.deepcopy(dictionary[0]))
                elif mode=='missing-definition': dictionary.pop()
                elif mode=='origin': dictionary[8]['td']=2
                elif mode=='area': dictionary[8]['a']=2
                elif mode=='negative-cadaster-lid': dictionary[0]['lid']=-1
                elif mode=='file-pointer': catalog[95]['files'][2]['f']='ifdata/202312/cadastro202312_1005.json'
                self.archive('catalog',catalog)
                self.archive('dictionary',dictionary)
                with self.assertRaises(ValueError): self.author()
                self.archive('catalog',self.payloads['catalog'])
                self.archive('dictionary',self.payloads['dictionary'])

if __name__ == '__main__':
    unittest.main()
