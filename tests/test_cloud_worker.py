import json
import tempfile
import unittest
from pathlib import Path
from scripts.cloud_worker import execute, load_request, write_report

def event(body: str, author: str = "AjaneeI") -> dict:
    return {"issue": {"number": 7, "user": {"login": author}, "body": body}}

class WorkerTests(unittest.TestCase):
    def test_mode_a_finishes(self):
        p = load_request(event('{"schema_version":1,"task":"smoke-test","mode":"A"}'))
        r = execute(p, 7)
        self.assertEqual(r["status"], "COMPLETED")
        self.assertTrue(r["test_passed"])
    def test_mode_b_checkpoint(self):
        p = load_request(event('{"schema_version":1,"task":"smoke-test","mode":"B"}'))
        self.assertEqual(execute(p, 7)["status"], "CHECKPOINT_READY")
    def test_mode_c_approval_gate(self):
        p = load_request(event('{"schema_version":1,"task":"smoke-test","mode":"C"}'))
        r = execute(p, 7)
        self.assertEqual(r["status"], "AWAITING_APPROVAL")
        self.assertIsNone(r["test_passed"])
    def test_rejects_unknown_task(self):
        with self.assertRaises(ValueError):
            load_request(event('{"schema_version":1,"task":"shell","mode":"A"}'))
    def test_rejects_untrusted_author(self):
        with self.assertRaises(ValueError):
            load_request(event('{"schema_version":1,"task":"smoke-test","mode":"A"}', "attacker"))
    def test_rejects_extra_input_and_non_json(self):
        for body in ['{"schema_version":1,"task":"smoke-test","mode":"A","command":"rm -rf /"}', "echo hello"]:
            with self.subTest(body=body), self.assertRaises(ValueError):
                load_request(event(body))
    def test_result_files(self):
        with tempfile.TemporaryDirectory() as p:
            report = execute({"task": "smoke-test", "mode": "B"}, 7)
            write_report(report, Path(p))
            self.assertEqual(json.loads((Path(p) / "report.json").read_text())["status"], "CHECKPOINT_READY")
            self.assertIn("No files were changed", (Path(p) / "report.md").read_text())

if __name__ == "__main__":
    unittest.main()
