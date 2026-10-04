import json
from contextlib import redirect_stderr
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

class CLITests(unittest.TestCase):
    def test_search_budget_rejects_invalid_arguments_before_key_input(self):
        from sourcepatch.__main__ import main
        for value in ['0', '-1', '9', '1.5', 'eight', '']:
            with self.subTest(value=value):
                stderr = io.StringIO()
                with patch('sys.argv', ['sourcepatch', '--mode', 'live', '--max-searches', value]), \
                        patch('sys.stdin.isatty') as terminal, \
                        patch('sourcepatch.__main__.getpass.getpass') as key_input, \
                        patch('sourcepatch.__main__.make_server') as server, redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as error:
                        main()
                self.assertEqual(error.exception.code, 2)
                self.assertIn('integer from 1 through 8', stderr.getvalue())
                terminal.assert_not_called()
                key_input.assert_not_called()
                server.assert_not_called()

    def test_live_search_budget_reaches_provider_server_and_disclosure(self):
        from sourcepatch.__main__ import main
        for budget in [1, 8, None]:
            with self.subTest(budget=budget):
                arguments = ['sourcepatch', '--mode', 'live']
                if budget is not None:
                    arguments.extend(['--max-searches', str(budget)])
                expected = 8 if budget is None else budget
                server = Mock(server_port=8765)
                with patch('sys.argv', arguments), patch('sys.stdin.isatty', return_value=True), \
                        patch('sourcepatch.__main__.getpass.getpass', return_value='fake-test-key'), \
                        patch('sourcepatch.__main__.SerpApiSearch') as provider, \
                        patch('sourcepatch.__main__.make_server', return_value=server) as make_server, \
                        patch('builtins.print') as output:
                    main()
                provider.assert_called_once_with('fake-test-key', max_searches=expected)
                make_server.assert_called_once_with(port=8765, mode='live', search=provider.return_value.search,
                                                    process_search_budget=expected)
                self.assertTrue(any(f'At most {expected} attempted SerpApi calls per process' in str(call)
                                    for call in output.call_args_list))
                server.server_close.assert_called_once()

    def test_demo_export_is_labeled_and_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            destination=Path(temp)/'demo';command=[sys.executable,'-m','sourcepatch','--demo-export',str(destination)]
            # Bound subprocess supervision, not interpreter startup performance.
            result=subprocess.run(command,capture_output=True,text=True,timeout=30);self.assertEqual(result.returncode,0,result.stderr)
            report=json.loads((destination/'provenance.json').read_text());self.assertEqual(report['mode'],'fixture');self.assertIn('hypothetical',report['approval_context']);self.assertTrue(all(change['approved_by_user'] is False for change in report['changes']))
            before=(destination/'guide.md').read_bytes();result=subprocess.run(command,capture_output=True,text=True,timeout=30)
            self.assertNotEqual(result.returncode,0);self.assertEqual((destination/'guide.md').read_bytes(),before)
    def test_live_mode_requires_real_no_echo_terminal(self):
        result=subprocess.run([sys.executable,'-m','sourcepatch','--mode','live'],input='',capture_output=True,text=True,timeout=30)
        self.assertNotEqual(result.returncode,0);self.assertIn('interactive terminal',result.stderr);self.assertNotIn('Can not control echo',result.stderr)

if __name__=='__main__':unittest.main()
