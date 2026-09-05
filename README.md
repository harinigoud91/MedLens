# MedLens 🩺

MedLens is an AI-powered medical report assistant designed to help patients and everyday users understand complex medical reports, lab results, and health documents by translating medical jargon into clear, accessible explanations.

> **Status:** 🚧 Foundation Stage  
> The project foundation and environment configuration are established. Core features (document processing, Gemini AI integration, and user interface workflows) will be built in upcoming stages.

---

## Project Structure

```text
MedLens/
├── app.py              # Streamlit application entry point (placeholder)
├── requirements.txt    # Essential dependencies for the planned MVP
├── README.md           # Project documentation and setup guide
├── .gitignore          # Rules to exclude sensitive files, caches, and environments
└── .env.example        # Template for environment variables (API keys)
```

---

## Planned MVP Features

- **Document Ingestion:** Upload PDF reports and image scans.
- **AI Simplification:** Gemini-powered translation of technical medical terminology into plain language.
- **Key Findings Extraction:** Clear summary of critical metrics and doctor consultation talking points.
- **Interactive Q&A:** Safe, conversational follow-up questions for report clarification.

---

## Getting Started

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Setup Virtual Environment (Recommended)
```bash
python -m venv venv
```

Activate the environment:
- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Windows (Command Prompt):**
  ```cmd
  venv\Scripts\activate.bat
  ```
- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
Add your Google Gemini API key inside `.env`.

### 5. Run the Application
```bash
streamlit run app.py
```
