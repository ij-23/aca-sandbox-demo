"""Unit-test doubles only: no Azure/Copilot calls or agent execution."""
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('smoke', Path(__file__).parents[1] / 'smoke_test_sandbox.py')
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)
CONNECTION = '11111111-1111-1111-1111-111111111111'


def fixture(nonce):
    result = {'nonce': nonce, 'answer': 'pong', 'sum': 5, 'branch': 'verified', 'workflow_run_id': 'test-only',
              'steps': [{'step': name, 'status': 'passed', 'duration_ms': 1, 'result': value} for name, value in (
                  ('prepare', {'sum': 5, 'observation_window_ms': 3000}),
                  ('agent', {'nonce': nonce, 'answer': 'pong', 'sum': 5}),
                  ('verify', {'branch': 'verified', 'reason': 'agent_matches_deterministic_result'}))]}
    events = [{'timestamp': '2026-10-13T00:00:00.000Z', 'workflow_run_id': 'test-only', 'nonce': nonce,
               'step': step, 'status': status} for step in ('prepare', 'agent', 'verify') for status in ('running', 'passed')]
    return result, events


class FakeSandbox:
    sandbox_id = 'unit-test-only'

    def __init__(self, group):
        self.group = group
        self.files = {}

    def write_file(self, path, value):
        self.files[Path(path).name] = value

    def read_file(self, path):
        return self.files[Path(path).name].encode()

    def exec(self, command):
        if 'runner.py capabilities' in command:
            data = {'environment': {'COPILOT_GITHUB_TOKEN': not self.group.no_auth},
                    'version': {'stdout': 'GitHub Copilot CLI 1.0.97.', 'exit_code': 0},
                    'help': {'stdout': '--no-auto-update --no-custom-instructions --disable-builtin-mcps --available-tools --deny-tool'},
                    'workflow_help': {'stdout': 'General help only' if self.group.no_workflow else '--args --result-file'}}
            return SimpleNamespace(exit_code=0, stdout=json.dumps(data))
        if 'subprocess.Popen' in command:
            if self.group.workflow_error:
                raise TimeoutError('TEST DOUBLE timeout')
            nonce = json.loads(self.files['input.json'])['nonce']
            result, events = fixture(nonce)
            if self.group.bad_result:
                result['nonce'] = 'wrong'
            self.files.update({'status.json': json.dumps({'state': 'finished', 'exit_code': 0, 'seconds': 1}),
                               'result.json': json.dumps(result), 'command.sanitized.log': 'TEST DOUBLE',
                               'smoke-events.jsonl': ''.join(json.dumps(e)+'\n' for e in events)})
        return SimpleNamespace(exit_code=0, stdout='')

    def delete(self):
        self.group.deleted.append(self.sandbox_id)
        self.group.records = [r for r in self.group.records if r.id != self.sandbox_id]

    def get(self):
        if self.sandbox_id in self.group.deleted:
            error = RuntimeError('TEST DOUBLE not found')
            error.status_code = 404
            raise error
        return SimpleNamespace(state='Running', ports=[], connections=[CONNECTION])


class FakeGroup:
    def __init__(self, workflow_error=False, bad_result=False, create_error=False, no_auth=False, no_workflow=False):
        self.records = [SimpleNamespace(id='unrelated', labels={'owner': 'another-app'}, state='Stopped')]
        self.deleted = []
        self.workflow_error, self.bad_result = workflow_error, bad_result
        self.create_error, self.no_auth = create_error, no_auth
        self.no_workflow = no_workflow
        self.sandbox = FakeSandbox(self)
        self.create_calls = []

    def list_public_disk_images(self):
        return [SimpleNamespace(name='copilot', status=SimpleNamespace(state='Ready'))]

    def list_sandboxes(self):
        return self.records

    def begin_create_sandbox(self, **kwargs):
        self.create_calls.append(kwargs)
        self.records.append(SimpleNamespace(id=self.sandbox.sandbox_id, labels=kwargs['labels'], state='Running'))
        if self.create_error:
            raise TimeoutError('TEST DOUBLE lost create response')
        return SimpleNamespace(result=lambda **_: self.sandbox)

    def get_sandbox_client(self, identifier):
        assert identifier == self.sandbox.sandbox_id, 'Never delete unrelated resources'
        return self.sandbox


class SmokeTests(unittest.TestCase):
    def run_fake(self, **kwargs):
        group = FakeGroup(**kwargs)
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(io.StringIO()):
            result = smoke.perform(group, Path(d)/'evidence.json', 'test-scope', CONNECTION)
        self.assertEqual([r.id for r in group.records], ['unrelated'])
        self.assertNotIn('unrelated', group.deleted)
        self.assertEqual(len(group.create_calls), 1)
        self.assertEqual(group.create_calls[0]['connections'], [CONNECTION])
        self.assertEqual(group.create_calls[0]['ports'], [])
        return result

    def test_bound_connection_success_requires_result_and_exact_cleanup(self):
        result = self.run_fake()
        self.assertEqual(result['status'], 'passed')
        self.assertEqual(result['cleanup'], 'deleted_and_exact_id_404_verified')
        self.assertFalse(result['live_progress_observed'])  # Completed fixture is not live evidence.

    def test_workflow_timeout_still_cleans_up(self):
        result = self.run_fake(workflow_error=True)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['cleanup'], 'deleted_and_exact_id_404_verified')

    def test_missing_auth_stops_before_workflow_and_cleans_up(self):
        result = self.run_fake(no_auth=True)
        self.assertEqual(result['status'], 'failed')
        self.assertNotIn('result', result)
        self.assertEqual(result['cleanup'], 'deleted_and_exact_id_404_verified')

    def test_general_help_is_not_workflow_support_even_with_zero_exit(self):
        result = self.run_fake(no_workflow=True)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['error'], 'Experimental direct Dynamic Workflow command not exposed')
        self.assertNotIn('result', result)
        self.assertEqual(result['cleanup'], 'deleted_and_exact_id_404_verified')

    def test_wrong_nonce_rejected(self):
        self.assertEqual(self.run_fake(bad_result=True)['status'], 'failed')

    def test_lost_creation_response_not_claimed_certain(self):
        result = self.run_fake(create_error=True)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['cleanup'], 'unconfirmed')

    def test_cleanup_failure_cannot_pass(self):
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(io.StringIO()), patch.object(smoke, 'cleanup', side_effect=RuntimeError('TEST DOUBLE')):
            result = smoke.perform(FakeGroup(), Path(d)/'evidence.json', 'test-scope', CONNECTION)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['cleanup'], 'unconfirmed')

    def test_partial_event_line_is_ignored_until_complete(self):
        group = FakeGroup()
        _, events = fixture('a'*32)
        group.sandbox.files['smoke-events.jsonl'] = json.dumps(events[0])+'\n'+json.dumps(events[1])[:30]
        self.assertEqual(smoke.read_events(group.sandbox, '/control', 'a'*32), events[:1])
        with self.assertRaises(ValueError):
            smoke.read_events(group.sandbox, '/control', 'a'*32, final=True)

    def test_protected_id_is_never_deleted(self):
        group = FakeGroup()
        with self.assertRaises(RuntimeError):
            smoke.cleanup(group, group.sandbox, {}, True, protected_ids={group.sandbox.sandbox_id})
        self.assertEqual(group.deleted, [])

    def test_mismatched_workflow_event_id_rejected(self):
        result, events = fixture('a'*32)
        events[-1]['workflow_run_id'] = 'another-run'
        with self.assertRaises(ValueError):
            smoke.validate_result(result, 'a'*32, events)

    def test_exact_labels_required_for_orphan_deletion(self):
        group = FakeGroup()
        group.records.append(SimpleNamespace(id='other-run', labels={'owner': smoke.OWNER, 'smoke-run': 'other'}))
        self.assertEqual(smoke.owned_records(group, {'owner': smoke.OWNER, 'smoke-run': 'mine'}), [])

    def args(self):
        return ['--subscription-id', '11111111-1111-1111-1111-111111111111',
                '--tenant-id', '22222222-2222-2222-2222-222222222222',
                '--resource-group', 'rg-test', '--sandbox-group', 'sbg-test', '--region', 'eastus2']

    def test_default_is_inert_without_connection_or_sdk(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = smoke.main(self.args())
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.getvalue())['azure_calls'], 0)

    def test_execute_requires_scope_before_sdk_or_azure(self):
        with self.assertRaisesRegex(ValueError, 'confirm-group'):
            smoke.main(['--execute', *self.args()])

    def test_execute_requires_connection_before_sdk_or_azure(self):
        scope='/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/rg-test/providers/Microsoft.App/sandboxGroups/sbg-test'
        with self.assertRaisesRegex(ValueError, 'credential-connection-id'):
            smoke.main(['--execute', '--confirm-group', scope, *self.args()])


if __name__ == '__main__':
    unittest.main()
