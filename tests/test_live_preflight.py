import importlib.util
import json
from pathlib import Path
import unittest
from sourcepatch.network import FetchResult, NetworkError
spec=importlib.util.spec_from_file_location('live_proof',Path(__file__).resolve().parent.parent/'scripts/live-proof.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class AllowanceTests(unittest.TestCase):
    def test_allowlist_only_and_no_redirects(self):
        seen=[]
        def fetch(url,**kw):
            seen.append(kw)
            return FetchResult(200,url,json.dumps({'account_status':'Active','plan_searches_left':5,'api_key':'fake-secret','email':'private@example.org'}).encode())
        receipt=module.allowance('fake-secret',fetch)
        self.assertEqual(receipt['plan_searches_left'],5)
        self.assertEqual(seen[0]['max_redirects'],0)
        self.assertNotIn('fake-secret',json.dumps(receipt));self.assertNotIn('private',json.dumps(receipt))
    def test_inactive_missing_and_empty_allowance_fail_closed(self):
        for data in [{},{'account_status':'Active','plan_searches_left':0},{'account_status':'Inactive','plan_searches_left':5},{'account_status':'Active','plan_searches_left':True}]:
            with self.subTest(data=data),self.assertRaises(NetworkError):
                module.allowance('fake-secret',lambda url,**kw:FetchResult(200,url,json.dumps(data).encode()))
