"""Offline behavior tests; no endpoint, browser, downloads or external writes."""
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


layout = load('layout_check')
receiver = load('receiver')
katex = load('vendor_katex')


class LayoutTests(unittest.TestCase):
    def run_checker(self, name):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/layout_check.py'),
                               str(ROOT / 'fixtures' / name)], capture_output=True, text=True)

    def test_clean_fixture(self):
        result = self.run_checker('scene-clean.json')
        self.assertEqual((result.returncode, result.stdout.strip()), (0, 'CLEAN'))

    def test_stacked_titles_and_bodies(self):
        result = self.run_checker('scene-overlap.json')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.count('100% (identical origin)'), 6)
        self.assertTrue(result.stdout.endswith('6 findings\n'))

    def test_nontext_bounds(self):
        result = self.run_checker('scene-outside.json')
        self.assertEqual(result.returncode, 1)
        self.assertIn('outside canvas', result.stdout)

    def test_threshold_and_touching_edges(self):
        def box(name, x):
            return dict(id=name, type='text', left=x, top=0, width=100, height=100)
        self.assertEqual(len(layout.check([box('a', 0), box('b', 80)])), 1)
        self.assertEqual(layout.check([box('a', 0), box('b', 81)]), [])
        self.assertEqual(layout.check([box('a', 0), box('b', 100)]), [])

    def test_skip_non_slide(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            path = Path(folder) / 'quiz.json'
            path.write_text('{"content":{"type":"quiz"}}')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/layout_check.py'), str(path)],
                                    capture_output=True, text=True)
            self.assertEqual((result.returncode, result.stdout.strip()), (0, 'CLEAN'))


class ReceiverTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.handler = receiver.handler_for(self.folder / 'output', 'http://localhost:3000')

    def request(self, path, body=b'{}', method='POST', length=None):
        handler = object.__new__(self.handler)
        handler.path = path
        handler.headers = {'Content-Length': str(len(body)) if length is None else length}
        handler.rfile = io.BytesIO(body)
        handler.wfile = io.BytesIO()
        handler.send_response = mock.Mock()
        handler.send_header = mock.Mock()
        handler.end_headers = mock.Mock()
        getattr(handler, 'do_' + method)()
        return handler

    def test_exact_body_and_safe_response(self):
        handler = self.request('/test', b'{"synthetic": true}')
        self.assertEqual((self.folder / 'output/test.json').read_bytes(), b'{"synthetic": true}')
        handler.send_response.assert_called_once_with(200)
        self.assertEqual(json.loads(handler.wfile.getvalue())['saved'], 'test.json')
        handler.send_header.assert_any_call('Access-Control-Allow-Origin', 'http://localhost:3000')

    def test_reject_traversal_and_encoded_names(self):
        for path in ('/../escape', '/a/b', '//escape', '/%2e%2e', '/a?b', '/a.json', '/'):
            with self.subTest(path=path):
                self.request(path).send_response.assert_called_once_with(400)
        self.assertEqual(list((self.folder / 'output').iterdir()), [])

    def test_reject_symlink_destination(self):
        target = self.folder / 'keep.json'
        target.write_text('keep')
        (self.folder / 'output/link.json').symlink_to(target)
        self.request('/link').send_response.assert_called_once_with(400)
        self.assertEqual(target.read_text(), 'keep')

    def test_invalid_length(self):
        for value in ('-1', 'invalid'):
            self.request('/test', length=value).send_response.assert_called_once_with(400)

    def test_options_and_loopback_bind(self):
        self.request('/test', method='OPTIONS').send_response.assert_called_once_with(204)
        with mock.patch.object(sys, 'argv', ['receiver.py', '--output', str(self.folder)]), \
             mock.patch.object(receiver.http.server, 'HTTPServer') as server:
            receiver.main()
        self.assertEqual(server.call_args.args[0], ('127.0.0.1', 9977))
        server.return_value.__enter__.return_value.serve_forever.assert_called_once()


class KatexTests(unittest.TestCase):
    def test_all_assets_and_unrelated_url_preserved(self):
        text = (ROOT / 'fixtures/interactive.html').read_text() + '\nhttps://example.invalid/unrelated\n'
        result, count = katex.rewrite(text, './vendor/katex')
        self.assertEqual(count, 3)
        self.assertNotIn(katex.CDN, result)
        self.assertIn('./vendor/katex/contrib/auto-render.min.js', result)
        self.assertIn('https://example.invalid/unrelated', result)
        self.assertEqual(katex.rewrite(result, './vendor/katex'), (result, 0))

    def test_json_remains_json(self):
        original = json.dumps({'html': (ROOT / 'fixtures/interactive.html').read_text()})
        rewritten, count = katex.rewrite(original, '/vendor/katex')
        self.assertEqual(count, 3)
        self.assertIn('/vendor/katex/katex.min.css', json.loads(rewritten)['html'])

    def test_reject_remote_prefix(self):
        for prefix in ('https://example.invalid', '//example.invalid', 'data:placeholder', ''):
            with self.assertRaises(ValueError):
                katex.rewrite('', prefix)

    def test_cli_writes_separate_output(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            target = Path(folder) / 'rewritten.html'
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/vendor_katex.py'),
                                     str(ROOT / 'fixtures/interactive.html'), str(target)],
                                    capture_output=True, text=True)
            self.assertEqual((result.returncode, result.stdout.strip()), (0, 'rewrote 3 URLs'))
            self.assertNotIn(katex.CDN, target.read_text())


class ShellTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.log = self.folder / 'synthetic dev.log'
        self.log.write_text('synthetic error word without application severity\n')
        self.env = dict(os.environ, PATH=str(self.folder) + os.pathsep + os.environ['PATH'],
                        VLLM_URL='http://127.0.0.1:9977', MODEL='fixture-model', DEV_LOG=str(self.log),
                        FIXTURE_ROOT=str(ROOT / 'fixtures'), MOCK_STATE=str(self.folder / 'ticks'),
                        MOCK_METRICS='idle', MOCK_DATE_STEP='0')
        self.command('curl', '''import json,os,sys
url = next(value for value in sys.argv[1:] if value.startswith('http://'))
if url.endswith('/metrics'):
    print(open(os.path.join(os.environ['FIXTURE_ROOT'],'metrics',os.environ['MOCK_METRICS']+'.prom')).read(),end='')
elif url.endswith('/v1/models'):
    print(json.dumps({'data':[{'id':'fixture-model'}]}))
elif url.endswith('/v1/chat/completions'):
    body=json.loads(sys.argv[sys.argv.index('-d')+1])
    assert body['model']=='fixture-model' and body['max_tokens']==16
    print(json.dumps({'choices':[{'message':{'content':'Synthetic acknowledgement.'}}]}))
else:
    raise SystemExit('Unexpected URL')
''')
        self.command('sleep', 'pass\n')
        self.command('date', '''import os
from pathlib import Path
p=Path(os.environ['MOCK_STATE'])
tick=int(p.read_text()) if p.exists() else 0
print(tick*int(os.environ['MOCK_DATE_STEP']))
p.write_text(str(tick+1))
''')

    def command(self, name, code):
        path = self.folder / name
        path.write_text('#!' + sys.executable + '\n' + code)
        path.chmod(0o755)

    def run_script(self, name):
        result = subprocess.run(['bash', str(ROOT / 'scripts' / name)], env=self.env,
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return result.stdout

    def test_endpoint_smoke(self):
        result = self.run_script('endpoint-smoke.sh')
        self.assertIn('fixture-model', result)
        self.assertIn('Synthetic acknowledgement.', result)

    def test_metrics_probe(self):
        result = self.run_script('vllm-metrics-probe.sh')
        self.assertIn('vllm:num_requests_running', result)
        self.assertIn('synthetic error word', result)

    def test_progress_baseline_and_stall(self):
        result = self.run_script('progress-monitor.sh')
        self.assertIn('tok_delta=2890', result.splitlines()[0])
        self.assertIn('STALL_3x_NO_TOKEN_NO_RUNNING', result)
        self.assertNotIn('ERROR_SIGNAL', result)

    def test_progress_error(self):
        self.log.write_text('[ERROR] Synthetic failure\n')
        self.assertIn('ERROR_SIGNAL', self.run_script('progress-monitor.sh'))

    def test_progress_done(self):
        self.log.write_text('[INFO] Synthetic course complete\n')
        self.assertIn('DONE_SIGNAL', self.run_script('progress-monitor.sh'))

    def test_progress_timeout(self):
        self.env.update(MOCK_METRICS='running', MOCK_DATE_STEP='1800')
        self.assertIn('TIMEOUT_30m', self.run_script('progress-monitor.sh'))

    def test_wait_until_idle(self):
        self.assertIn('DONE: vLLM idle 3x(90s)', self.run_script('wait-until-idle.sh'))

    def test_wait_error(self):
        self.log.write_text('[ERROR] Synthetic failure\n')
        self.assertIn('ERROR in log', self.run_script('wait-until-idle.sh'))

    def test_wait_timeout(self):
        self.env.update(MOCK_METRICS='running', MOCK_DATE_STEP='2401')
        self.assertIn('TIMEOUT 40m', self.run_script('wait-until-idle.sh'))

    def test_missing_configuration_fails(self):
        self.env.pop('VLLM_URL')
        result = subprocess.run(['bash', str(ROOT / 'scripts/endpoint-smoke.sh')],
                                env=self.env, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Set VLLM_URL', result.stderr)


if __name__ == '__main__':
    unittest.main()
