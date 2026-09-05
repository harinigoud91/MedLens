# MedLens 🩺

## Evidence-First AI Medical Report Intelligence

MedLens is a Gemini-powered medical report intelligence tool that converts complex medical PDF reports into a structured, readable clinical record.

### Key Features

- PDF medical report upload and text extraction
- Gemini-powered report analysis and summarization
- Patient context: Name, Age, Sex and Symptoms
- Structured clinical record with Test, Result, Unit, Reference Range, Status, Source and Confidence
- Evidence Lens with source-page and evidence-snippet provenance
- Plain-language medical terminology explanations
- Responsible AI guardrails
- No diagnosis, prescriptions or dosage recommendations
- Synthetic demo report for safe demonstration

### Technology

Python • Streamlit • Google Gemini • PyMuPDF

### How It Works

Medical PDF → PyMuPDF extraction → Gemini analysis → Structured clinical record → Evidence matching → Plain-language explanation

### Responsible AI

MedLens is an information and report-understanding tool, not a diagnostic system. AI-generated information is clearly labeled, and extracted values are connected to report evidence where available.

The application does not provide diagnoses, prescriptions, or dosage recommendations.

### Limitation

The current MVP primarily supports text-based PDFs. Scanned/image-only PDFs are detected, but OCR is not currently implemented.

### Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py