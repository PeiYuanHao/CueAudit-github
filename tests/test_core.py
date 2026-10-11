import csv
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cueaudit.pipeline import audit, screening_rules, DEFAULT_THRESHOLDS
from cueaudit.statistics import categorical, foreground
from cueaudit.verification import verify


class StatisticsTests(unittest.TestCase):
    def test_perfect_and_independent(self):
        self.assertAlmostEqual(categorical(['a', 'b'], ['x', 'y'])['cramers_v'], 1)
        self.assertAlmostEqual(categorical(['a', 'a', 'b', 'b'], ['x', 'y', 'x', 'y'])['cramers_v'], 0)

    def test_degenerate_not_promoted(self):
        result = categorical(['a', 'a'], ['x', 'x'], ['a', 'a'])
        self.assertTrue(result['degenerate'])
        self.assertEqual(screening_rules(result, DEFAULT_THRESHOLDS), [])

    def test_explicit_alignment_differs_from_decoding(self):
        result = categorical(['a', 'b'], ['x', 'y'], ['b', 'a'])
        self.assertEqual(result['alignment'], 0)
        self.assertEqual(result['majority_decoding_accuracy'], 1)

    def test_boundaries_are_strict(self):
        self.assertEqual(screening_rules({'alignment': .8, 'cramers_v': .5,
                         'foreground_class_gap': .1}, DEFAULT_THRESHOLDS), [])
        self.assertEqual(screening_rules({'cramers_v': .5001}, DEFAULT_THRESHOLDS), ['cramers_v'])

    def test_invalid_arrays(self):
        for cues, labels in [([], []), (['a'], ['x', 'y'])]:
            with self.assertRaises(ValueError):
                categorical(cues, labels)
        with self.assertRaises(ValueError):
            foreground([math.nan], ['x'])

    def test_class_gap(self):
        self.assertAlmostEqual(foreground([.2, .4, .8], ['a', 'a', 'b'])['foreground_class_gap'], .5)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.write('input.csv', [['label', 'cue'], ['x', 'a'], ['y', 'b']])
        self.candidate = {'hypothesis': 'Invented cue', 'module': 'metadata', 'manifest': 'input.csv'}

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, rows):
        with (self.base / name).open('w', encoding='utf-8', newline='') as stream:
            csv.writer(stream).writerows(rows)

    def run_audit(self, **settings):
        return audit({'candidates': [self.candidate], **settings}, self.base)['findings'][0]

    def test_screen_and_provenance(self):
        result = self.run_audit()
        self.assertEqual(result['status'], 'screen_promoted')
        self.assertEqual(len(result['provenance']['manifest_sha256']), 64)

    def test_missing_vs_invalid(self):
        self.candidate['manifest'] = 'absent.csv'
        self.assertEqual(self.run_audit()['status'], 'unsupported')
        self.candidate['manifest'] = 'input.csv'
        self.write('input.csv', [['label', 'cue'], ['x', '']])
        self.assertEqual(self.run_audit()['status'], 'failed')

    def test_unknown_module_and_review_only(self):
        self.candidate.update(module='missing', review_note='Uncertain observation')
        result = self.run_audit()
        self.assertEqual(result['status'], 'unsupported')
        self.assertEqual(result['review_lead']['status'], 'review_only')

    def test_budget_and_unavailable_verifier(self):
        self.assertEqual(self.run_audit(depth='verify', max_verifications=0)['status'], 'verification_incomplete')
        self.assertEqual(self.run_audit(depth='verify')['status'], 'verification_unsupported')

    def test_verification_preserves_data_evidence(self):
        self.write('pairs.csv', [['seed', 'id_accuracy', 'ood_accuracy'], ['invented', '.8', '.5']])
        self.candidate['verification'] = {'manifest': 'pairs.csv', 'intervention': 'invented intervention', 'producer': 'test fixture'}
        result = self.run_audit(depth='verify')
        self.assertEqual(result['status'], 'verified')
        self.assertFalse(result['model_promoted'])
        # Exactly 30 pp must not cross the strict threshold.
        self.write('pairs.csv', [['seed', 'id_accuracy', 'ood_accuracy'], ['invented', '.3', '0']])
        self.assertFalse(self.run_audit(depth='verify')['model_promoted'])
        self.assertIn('cramers_v', result['screen_triggers'])
        self.write('pairs.csv', [['seed', 'id_accuracy', 'ood_accuracy'], ['invented', '80', '50']])
        self.assertEqual(self.run_audit(depth='verify')['status'], 'verification_failed')

    def test_duplicate_seeds_rejected(self):
        self.write('pairs.csv', [['seed', 'id_accuracy', 'ood_accuracy'], ['same', '.9', '.5'], ['same', '.8', '.5']])
        with self.assertRaises(ValueError):
            verify({'manifest': 'pairs.csv', 'intervention': 'test', 'producer': 'fixture'}, self.base)

    def test_explicit_subset_verification(self):
        self.write('input.csv', [['label', 'cue'], ['x', 'a'], ['y', 'a'], ['x', 'b'], ['y', 'b']])
        self.assertEqual(self.run_audit(depth='verify')['status'], 'screen_below_threshold')
        self.candidate['verification_reason'] = 'A separately specified subset requires review'
        self.assertEqual(self.run_audit(depth='verify')['status'], 'verification_unsupported')

    def test_invalid_policy(self):
        for setting in ({'thresholds': {'alignment': math.nan}}, {'max_verifications': -1}, {'depth': 'unknown'}):
            with self.assertRaises(ValueError):
                self.run_audit(**setting)

    def test_cli(self):
        request = self.base / 'request.json'
        request.write_text(json.dumps({'candidates': [self.candidate]}), encoding='utf-8')
        output = self.base / 'report.json'
        result = subprocess.run([sys.executable, '-m', 'cueaudit.cli', str(request), '--output', str(output)], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(output.read_text())['findings'][0]['status'], 'screen_promoted')


if __name__ == '__main__':
    unittest.main()
