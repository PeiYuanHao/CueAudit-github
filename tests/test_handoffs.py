import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from cueaudit.handoffs import OfflineTransport, run_roles
from cueaudit.openclaw_runtime import ROLES, prepare, parse_reply, OpenClawTransport

REPOSITORY = Path(__file__).resolve().parents[1]


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / 'input.csv').write_text('label,cue\nx,a\ny,b\n', encoding='utf-8')
        self.task = {'base': str(self.root), 'request': {'dataset': 'invented', 'candidates': [
            {'hypothesis': 'Invented cue', 'module': 'metadata', 'manifest': 'input.csv'}]}}

    def tearDown(self):
        self.temp.cleanup()

    def test_offline_chain(self):
        output = self.root / 'run'
        artifact = run_roles(self.task, OfflineTransport(), output, REPOSITORY)
        self.assertEqual([x['role'] for x in artifact['trace']], list(ROLES))
        self.assertEqual(artifact['mode'], 'offline_contract_demo')
        self.assertFalse(artifact['historical_experiment'])
        evidence = json.loads((output / 'audit.json').read_text())
        self.assertEqual(evidence['findings'][0]['measurement']['cramers_v'], 1)
        summary = json.loads((output / 'summarize.json').read_text())
        self.assertEqual(summary['evidence_sha256'], artifact['evidence_sha256'])

    def test_unsafe_selection_stops_chain(self):
        fixture = OfflineTransport()
        def bad(role, message):
            if role == 'executive':
                return {'selected_indices': [100], 'routing_reason': 'invalid'}
            return fixture(role, message)
        with self.assertRaises(ValueError):
            run_roles(self.task, bad, self.root / 'bad', REPOSITORY)
        self.assertFalse((self.root / 'bad' / 'handoff-trace.json').exists())

    def test_numbers_cannot_replace_quantitative_artifact(self):
        fixture = OfflineTransport()
        def bad(role, message):
            reply = fixture(role, message)
            if role == 'quantitative':
                reply['report_sha256'] = 'fabricated'
            return reply
        with self.assertRaises(ValueError):
            run_roles(self.task, bad, self.root / 'tampered', REPOSITORY)

    def test_provider_failure_has_no_fixture_fallback(self):
        def failed(role, message):
            raise RuntimeError('Provider unavailable')
        with self.assertRaises(RuntimeError):
            run_roles(self.task, failed, self.root / 'failed', REPOSITORY)
        self.assertFalse((self.root / 'failed' / 'handoff-trace.json').exists())

    def test_existing_output_preserved(self):
        output = self.root / 'existing'
        output.mkdir()
        with self.assertRaises(ValueError):
            run_roles(self.task, OfflineTransport(), output, REPOSITORY)

    def test_prepare_isolated_workspaces(self):
        path = prepare(REPOSITORY, self.root / 'runtime', 'provider/model')
        config = json.loads(path.read_text())
        self.assertEqual(len(config['agents']['list']), 5)
        self.assertNotIn('channels', config)
        for entry in config['agents']['list']:
            self.assertTrue(Path(entry['agentDir']).is_relative_to((self.root / 'runtime' / 'state').resolve()))
            self.assertTrue((Path(entry['workspace']) / 'SOUL.md').is_file())
        with self.assertRaises(ValueError):
            prepare(REPOSITORY, self.root / 'runtime', 'provider/model')

    def test_parse_cli_envelopes(self):
        for envelope in ({'payloads': [{'text': '{"ok":true}'}]},
                         {'result': {'payloads': [{'text': '```json\n{"ok":true}\n```'}]}}):
            self.assertEqual(parse_reply(json.dumps(envelope)), {'ok': True})
        with self.assertRaises(ValueError):
            parse_reply(json.dumps({'payloads': [{'text': 'not json'}]}))

    def test_live_transport_environment(self):
        config = prepare(REPOSITORY, self.root / 'runtime', 'provider/model')
        entry = self.root / 'openclaw.mjs'
        entry.write_text('// fixture', encoding='utf-8')
        transport = OpenClawTransport('node', entry, config, config.parent / 'state')
        with patch('cueaudit.openclaw_runtime.subprocess.run') as run:
            run.return_value.returncode = 0
            run.return_value.stdout = json.dumps({'payloads': [{'text': '{"ok":true}'}]})
            self.assertEqual(transport('identify', 'fixture'), {'ok': True})
        args, kwargs = run.call_args
        self.assertNotIn('--deliver', args[0])
        self.assertIn('--local', args[0])
        self.assertEqual(kwargs['env']['OPENCLAW_CONFIG_PATH'], str(config))
        self.assertEqual(kwargs['env']['OPENCLAW_STATE_DIR'], str(config.parent / 'state'))

    def test_private_agent_directory_rejected(self):
        config_path = prepare(REPOSITORY, self.root / 'runtime', 'provider/model')
        config = json.loads(config_path.read_text())
        config['agents']['list'][0]['agentDir'] = str(self.root / 'private')
        config_path.write_text(json.dumps(config), encoding='utf-8')
        entry = self.root / 'openclaw.mjs'
        entry.touch()
        with self.assertRaises(ValueError):
            OpenClawTransport('node', entry, config_path, config_path.parent / 'state')

    def test_tool_policy_cannot_enable_execution(self):
        config_path = prepare(REPOSITORY, self.root / 'runtime', 'provider/model')
        config = json.loads(config_path.read_text())
        config['tools'] = {'profile': 'full'}
        config_path.write_text(json.dumps(config), encoding='utf-8')
        entry = self.root / 'openclaw.mjs'
        entry.touch()
        with self.assertRaises(ValueError):
            OpenClawTransport('node', entry, config_path, config_path.parent / 'state')

    def test_public_workspace_digests(self):
        import hashlib
        provenance = json.loads((REPOSITORY / 'openclaw/provenance.json').read_text(encoding='utf-8'))
        for role in provenance['roles']:
            for name, digest in role['public_file_sha256'].items():
                path = REPOSITORY / 'openclaw/workspaces' / role['role'] / name
                canonical = path.read_text(encoding='utf-8').replace('\r\n', '\n').encode('utf-8')
                self.assertEqual(hashlib.sha256(canonical).hexdigest(), digest)
