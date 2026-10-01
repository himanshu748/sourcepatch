import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

class CLITests(unittest.TestCase):
    def test_demo_export_is_labeled_and_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            destination=Path(temp)/'demo';command=[sys.executable,'-m','sourcepatch','--demo-export',str(destination)]
            result=subprocess.run(command,capture_output=True,text=True,timeout=5);self.assertEqual(result.returncode,0,result.stderr)
            report=json.loads((destination/'provenance.json').read_text());self.assertEqual(report['mode'],'fixture');self.assertIn('hypothetical',report['approval_context']);self.assertTrue(all(change['approved_by_user'] is False for change in report['changes']))
            before=(destination/'guide.md').read_bytes();result=subprocess.run(command,capture_output=True,text=True,timeout=5)
            self.assertNotEqual(result.returncode,0);self.assertEqual((destination/'guide.md').read_bytes(),before)
    def test_live_mode_requires_real_no_echo_terminal(self):
        result=subprocess.run([sys.executable,'-m','sourcepatch','--mode','live'],input='',capture_output=True,text=True,timeout=5)
        self.assertNotEqual(result.returncode,0);self.assertIn('interactive terminal',result.stderr);self.assertNotIn('Can not control echo',result.stderr)

if __name__=='__main__':unittest.main()
