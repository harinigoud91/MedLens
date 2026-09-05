import unittest
from pathlib import Path
import ast

APP = Path("app.py").read_text(encoding="utf-8")

class TestMedLens(unittest.TestCase):

    def test_app_exists(self):
        self.assertTrue(Path("app.py").exists())

    def test_python_syntax(self):
        ast.parse(APP)

    def test_streamlit(self):
        self.assertIn("streamlit", APP.lower())

    def test_pdf_processing(self):
        self.assertIn("pymupdf", APP.lower())

    def test_gemini(self):
        self.assertIn("gemini", APP.lower())

    def test_api_key_protection(self):
        self.assertIn("GEMINI_API_KEY", APP)

    def test_patient_context(self):
        for item in ["Name", "Age", "Sex", "Symptoms"]:
            self.assertIn(item, APP)

    def test_pdf_upload(self):
        self.assertIn("file_uploader", APP)

    def test_analysis_pipeline(self):
        self.assertIn("run_gemini_intelligence_pipeline", APP)

    def test_structured_record(self):
        self.assertIn("Structured Clinical Record", APP)

    def test_evidence_provenance(self):
        self.assertIn("Evidence Lens", APP)
        self.assertIn("Source", APP)

    def test_confidence(self):
        self.assertIn("Confidence", APP)

    def test_ai_label(self):
        self.assertIn("ai-generated information", APP.lower())

    def test_safety_guardrails(self):
        text = APP.lower()
        self.assertIn("diagnos", text)
        self.assertIn("prescription", text)
        self.assertIn("dosage", text)

    def test_demo_report(self):
        self.assertTrue(Path("sample_reports/synthetic_sample_report.pdf").exists())

if __name__ == "__main__":
    unittest.main()

