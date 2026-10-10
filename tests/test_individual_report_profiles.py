import copy
from contextlib import contextmanager
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlencode
from bank_quality import financial_report_profiles as profiles


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


@contextmanager
def individual_fixture():
    """Five explicit local archives, generated solely from public tree metadata.

    The population, numeric observations, capture contexts and portal are synthetic.
    Root and the fixture's independent policy pins are the only patched guards.
    """
    installed = profiles.load_individual_context()['profile']
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        files = [{} for _ in range(31)]
        native_files = {'cadaster':'ifdata/202412/cadastro202412_1006.json',
                        'dictionary':'ifdata/202412/info202412.json',
                        'numeric:1':'ifdata/202412/dados202412_1.json'}
        for sid, position in (('cadaster',1),('dictionary',9),('numeric:1',3)):
            files[position] = {'f':native_files[sid]}
        definitions = {}
        numeric_lids = set()
        for item in installed['reports']:
            position = int(item['catalog_pointer'].split('/')[3])
            files[position] = {'f':'synthetic/report-' + str(item['report']['id']) + '.json',
                               'trel':copy.deepcopy(item['report'])}
            for node in item['nodes']:
                definition = copy.deepcopy(node['definition'])
                if definition['id'] in definitions:
                    assert definitions[definition['id']] == definition
                definitions[definition['id']] = definition
                if node['kind'] == 'numeric':
                    numeric_lids.add(node['lid'])
        catalog = [{} for _ in range(100)]
        catalog[99] = {'dt':202412,'files':files}
        cadaster = [{**{f'c{i}':'synthetic' for i in range(38)},
                     'c0':str(index),'c1':'202412'} for index in range(1585)]
        numeric = {'id':1,'values':[{'e':0,'v':[{'i':lid,'v':'123.4500'} for lid in sorted(numeric_lids)]}]}
        portal = bytearray(b' ' * 34000)
        for offset in (28520,33835):
            fragment = b'case 13: value/1000.0;'
            portal[offset:offset+len(fragment)] = fragment
        bodies = {'cadaster':encoded(cadaster),'dictionary':encoded(list(definitions.values())),
                  'numeric:1':encoded(numeric),'catalog':encoded(catalog),'portal':bytes(portal)}
        pins = {}
        for sid, body in bodies.items():
            name = sid.replace(':','-')
            path = root / 'data/raw/synthetic' / (name + '.json')
            path.parent.mkdir(parents=True,exist_ok=True)
            (path.parent / (name + '.bin')).write_bytes(body)
            url = ('https://www3.bcb.gov.br/ifdata/rest/relatorios2000a2024' if sid=='catalog'
                   else 'https://www3.bcb.gov.br/ifdata/index.html' if sid=='portal'
                   else 'https://www3.bcb.gov.br/ifdata/rest/arquivos?' + urlencode({'nomeArquivo':native_files[sid]}))
            manifest = {'url':url,'final_url':url,'method':'GET','http_status':200,'outcome':'ok',
                'truncated':False,'diagnostics':[],'bytes':len(body),'sha256':profiles._sha(body),
                'body_path':name+'.bin','retrieved_at_utc':'2026-10-03T17:41:48-03:00',
                'response_headers':{'Content-Length':str(len(body))},
                'context':{'synthetic':True,'period':202412,'purpose':'explicit offline test fixture'}}
            manifest_body = encoded(manifest)
            path.write_bytes(manifest_body)
            pins[sid] = {'manifest_path':path.relative_to(root).as_posix(),
                         'manifest_sha256':profiles._sha(manifest_body),
                         'body_sha256':profiles._sha(body),'bytes':len(body)}
        with patch.object(profiles,'CHECKOUT_ROOT',root), patch.object(profiles,'_INDIVIDUAL_PINS',pins):
            yield root, installed


class IndividualProfileTests(unittest.TestCase):
    def test_closed_selection_and_profile(self):
        context = profiles.load_individual_context()
        self.assertEqual(context['selection'], {'period': 202412, 'perspective': 1006, 'reports': [93, 77, 100, 94]})
        self.assertEqual(len(context['profile']['cadaster_columns']), 38)
        self.assertEqual(sum(len(r['nodes']) for r in context['profile']['reports']), 129)
        with self.assertRaises(TypeError):
            profiles.load_individual_context(profile_path='other.json')
        for selection in ({'period':202412,'perspective':1005,'reports':[93,77,100,94]},
                          {'period':202412,'perspective':1006,'reports':[77,93,100,94]}):
            with self.assertRaises(ValueError):
                profiles.load_individual_context(selection)

    def test_timestamp_preserves_original_instant(self):
        self.assertEqual(profiles._individual_utc('2026-10-03T17:41:48-03:00'), '2026-10-03T20:41:48+00:00')
        for value in ('2026-10-03T17:41:48', 'invalid', None):
            with self.assertRaises(ValueError):
                profiles._individual_utc(value)

    def test_duplicate_json_rejected(self):
        with self.assertRaises(ValueError):
            profiles._json(b'{"id":1,"id":2}')

    def test_sources_cannot_be_rebound_by_caller(self):
        with individual_fixture():
            source = profiles._individual_sources()['cadaster']
            profiles._authenticate_individual_source(source)
            for key, value in [('manifest_path','data/raw/other.json'), ('manifest_sha256','0'*64),
                               ('body_sha256','0'*64), ('native_file','ifdata/202412/cadastro202412_1005.json')]:
                with self.subTest(key=key):
                    mutated = copy.deepcopy(source)
                    mutated[key] = value
                    with self.assertRaises(ValueError):
                        profiles._authenticate_individual_source(mutated)

    def test_synthetic_sources_and_full_reconstruction(self):
        with individual_fixture() as (_, installed):
            profile = profiles.author_individual_profile()
            self.assertEqual(profile['selection'], installed['selection'])
            for actual, expected in zip(profile['reports'], installed['reports']):
                self.assertEqual(actual['report'], expected['report'])
                self.assertEqual(actual['catalog_pointer'], expected['catalog_pointer'])
                # Definition pointers belong to this synthetic dictionary's order.
                for node, original in zip(actual['nodes'], expected['nodes']):
                    self.assertEqual({k:v for k,v in node.items() if k != 'definition_pointer'},
                                     {k:v for k,v in original.items() if k != 'definition_pointer'})
            nodes = [n for r in profile['reports'] for n in r['nodes']]
            self.assertEqual({k:sum(n['kind']==k for n in nodes) for k in ('group','attribute','quantity','numeric')},
                             {'group':9,'attribute':44,'quantity':2,'numeric':74})
            profit = next(n for n in profile['reports'][0]['nodes'] if n['lid']==78187)
            self.assertEqual(profit['window_start'], '2024-07-01')
            for sid, source in profile['source_members'].items():
                pin = profiles._INDIVIDUAL_PINS[sid]
                self.assertEqual(source['manifest_sha256'],pin['manifest_sha256'])
                self.assertEqual(source['body_sha256'],pin['body_sha256'])
                self.assertEqual(source['retrieved_at_original'], '2026-10-03T17:41:48-03:00')
                self.assertEqual(source['retrieved_at_utc_derived'], '2026-10-03T20:41:48+00:00')
                self.assertNotIn('source_complete', source)

    def test_physical_manifest_and_body_mutations_fail_with_repin(self):
        for mode in ('body','manifest_hash','context','url','timestamp','duplicate','schema'):
            with self.subTest(mode=mode), individual_fixture() as (root, _):
                source = profiles._individual_sources()['cadaster']
                # A valid physical archive must authenticate before each mutation.
                profiles._authenticate_individual_source(source)
                manifest_path = root / source['manifest_path']
                manifest = json.loads(manifest_path.read_bytes())
                if mode == 'body':
                    (manifest_path.parent / manifest['body_path']).write_bytes(b'[]')
                elif mode == 'manifest_hash':
                    manifest_path.write_bytes(manifest_path.read_bytes() + b' ')
                elif mode == 'duplicate':
                    manifest_path.write_bytes(b'{"url":"x","url":"y"}')
                else:
                    if mode == 'context': manifest['context']['period'] = 202312
                    if mode == 'url': manifest['url'] = 'https://example.org/forged'
                    if mode == 'timestamp': manifest['retrieved_at_utc'] = '2026-10-01T01:32:35'
                    if mode == 'schema': manifest['http_status'] = '200'
                    body = encoded(manifest)
                    manifest_path.write_bytes(body)
                    source['manifest_sha256'] = profiles._sha(body)
                    source['provenance_sha256'] = profiles._digest(manifest)
                with self.assertRaises(ValueError):
                    profiles._authenticate_individual_source(source)
                if mode in ('url','timestamp','schema','duplicate'):
                    # Even a fixture-policy repin cannot satisfy structural guards.
                    body = manifest_path.read_bytes()
                    profiles._INDIVIDUAL_PINS['cadaster']['manifest_sha256'] = profiles._sha(body)
                    with self.assertRaises(ValueError):
                        source = profiles._individual_sources()['cadaster']
                        profiles._authenticate_individual_source(source)

        # Repin synthetic policy to reach schema checks beyond physical integrity.
        for mode, sid in (('cadaster_width','cadaster'), ('duplicate_entity','numeric:1'),
                          ('missing_definition','dictionary'), ('wrong_membership','catalog')):
            with self.subTest(native_schema=mode), individual_fixture() as (root, _):
                pin = profiles._INDIVIDUAL_PINS[sid]
                manifest_path = root / pin['manifest_path']
                manifest = json.loads(manifest_path.read_bytes())
                body_path = manifest_path.parent / manifest['body_path']
                value = json.loads(body_path.read_bytes())
                if mode == 'cadaster_width': del value[0]['c37']
                if mode == 'duplicate_entity': value['values'].append(copy.deepcopy(value['values'][0]))
                if mode == 'missing_definition': value.pop()
                if mode == 'wrong_membership': value[99]['files'][29]['trel']['s'] = [{'id':1005}]
                body = encoded(value)
                body_path.write_bytes(body)
                manifest.update(bytes=len(body),sha256=profiles._sha(body))
                manifest['response_headers']['Content-Length'] = str(len(body))
                manifest_body = encoded(manifest)
                manifest_path.write_bytes(manifest_body)
                pin.update(bytes=len(body),body_sha256=profiles._sha(body),manifest_sha256=profiles._sha(manifest_body))
                # Authentication really succeeds; native compilation must reject.
                profiles._authenticate_individual_source(profiles._individual_sources()[sid])
                with self.assertRaises(ValueError):
                    profiles.author_individual_profile()

    def test_financial_namespace_stays_closed(self):
        with self.assertRaises(ValueError):
            profiles.descriptor_for_selection({'period':202412,'perspective':1006,'reports':[93,77,100,94]})
        context = profiles.load_installed_context({'period':202412,'perspective':1005,'reports':[92,96,101,98]})
        self.assertEqual(context['selection']['perspective'],1005)
