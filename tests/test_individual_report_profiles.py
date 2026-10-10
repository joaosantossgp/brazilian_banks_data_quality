import copy
import unittest
from bank_quality import financial_report_profiles as profiles


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
        source = profiles._individual_sources()['cadaster']
        for key, value in [('manifest_path','data/raw/other.json'), ('manifest_sha256','0'*64),
                           ('body_sha256','0'*64), ('native_file','ifdata/202412/cadastro202412_1005.json')]:
            mutated = copy.deepcopy(source)
            mutated[key] = value
            with self.assertRaises(ValueError):
                profiles._authenticate_individual_source(mutated)

    def test_real_sources_and_full_reconstruction(self):
        profile = profiles.author_individual_profile()
        self.assertEqual(profile, profiles.load_individual_context()['profile'])
        nodes = [n for r in profile['reports'] for n in r['nodes']]
        self.assertEqual({k:sum(n['kind']==k for n in nodes) for k in ('group','attribute','quantity','numeric')},
                         {'group':9,'attribute':44,'quantity':2,'numeric':74})
        profit = next(n for n in profile['reports'][0]['nodes'] if n['lid']==78187)
        self.assertEqual(profit['window_start'], '2024-07-01')
        for source in profile['source_members'].values():
            self.assertEqual(source['retrieved_at_original'], source['retrieved_at_utc'])
            self.assertEqual(source['retrieved_at_utc_derived'], profiles._individual_utc(source['retrieved_at_original']))
            self.assertNotIn('source_complete', source)

    def test_physical_manifest_and_body_mutations_fail_with_repin(self):
        import json
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        sources = profiles._individual_sources()
        for mode in ('body','context','url','timestamp','duplicate'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                for pin in profiles._INDIVIDUAL_PINS.values():
                    src = profiles.CHECKOUT_ROOT / pin['manifest_path']
                    dst = root / pin['manifest_path']
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_bytes(src.read_bytes())
                original = sources['cadaster']
                manifest_path = root / original['manifest_path']
                manifest = json.loads(manifest_path.read_bytes())
                source = copy.deepcopy(original)
                if mode == 'body':
                    (manifest_path.parent / manifest['body_path']).write_bytes(b'[]')
                elif mode == 'duplicate':
                    manifest_path.write_bytes(b'{"url":"x","url":"y"}')
                else:
                    if mode == 'context': manifest['context']['period'] = 202312
                    if mode == 'url': manifest['url'] = 'https://example.org/forged'
                    if mode == 'timestamp': manifest['retrieved_at_utc'] = '2026-10-01T01:32:35'
                    body = json.dumps(manifest).encode()
                    manifest_path.write_bytes(body)
                    source['manifest_sha256'] = profiles._sha(body)
                    source['provenance_sha256'] = profiles._digest(manifest)
                with patch.object(profiles,'CHECKOUT_ROOT',root), self.assertRaises(ValueError):
                    profiles._authenticate_individual_source(source)

    def test_financial_namespace_stays_closed(self):
        with self.assertRaises(ValueError):
            profiles.descriptor_for_selection({'period':202412,'perspective':1006,'reports':[93,77,100,94]})
        context = profiles.load_installed_context({'period':202412,'perspective':1005,'reports':[92,96,101,98]})
        self.assertEqual(context['selection']['perspective'],1005)
