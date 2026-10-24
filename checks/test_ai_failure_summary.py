"""Offline checks only: no real LLM calls or credentials."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from ai_failure_summary import main


class SummaryHelperTests(unittest.TestCase):
    def test_missing_key_skips_without_reading_or_sending(self):
        with patch.dict(os.environ, {}, clear=True), patch("sys.argv", ["helper", "missing.log"]), patch("urllib.request.urlopen") as send:
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(), 0)
            self.assertIn("SKIPPED", output.getvalue())
            send.assert_not_called()

    def test_success_uses_redacted_log_and_saves_text(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "failure.log"
            output = Path(directory) / "summary.txt"
            log.write_text("Expected 44.18, actual 43.18; sk-fake-example-only", encoding="utf-8")
            response = io.StringIO(json.dumps({"output": [{"type": "message", "content": [{"type": "output_text", "text": "The expected total is wrong."}]}]}))
            with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-fake-example-only", "OPENAI_MODEL": "mock-model"}, clear=True), patch("sys.argv", ["helper", str(log), "--output", str(output)]), patch("urllib.request.urlopen", return_value=response) as send:
                self.assertEqual(main(), 0)
            request = send.call_args.args[0]
            payload = json.loads(request.data)
            self.assertNotIn("sk-fake-example-only", payload["input"])
            self.assertIn("[REDACTED]", payload["input"])
            self.assertFalse(payload["store"])
            self.assertEqual(output.read_text(encoding="utf-8"), "The expected total is wrong.\n")

    def test_api_error_does_not_print_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "failure.log"
            log.write_text("AssertionError", encoding="utf-8")
            error = urllib.error.HTTPError("https://api.openai.com/v1/responses", 401, "Unauthorized", {}, None)
            with patch.dict(os.environ, {"OPENAI_API_KEY": "fake-private-key", "OPENAI_MODEL": "mock-model"}, clear=True), patch("sys.argv", ["helper", str(log)]), patch("urllib.request.urlopen", side_effect=error), contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(), 1)
            self.assertIn("HTTP 401", output.getvalue())
            self.assertNotIn("fake-private-key", output.getvalue())


if __name__ == "__main__":
    unittest.main()
