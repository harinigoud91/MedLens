"""
MedLens - AI-Powered Clinical Information Intelligence
PromptWars x AIMERverse Hackathon MVP
Step 6: Judge-Ready Evidence-First Clinical Dashboard
"""

import os
import json
import re
from typing import Optional, List, Dict, Tuple
import pandas as pd
import streamlit as st
import pymupdf
import dotenv
from google import genai
from google.genai import types


# ==============================================================================
# Page Configuration & Premium Clinical Styling
# ==============================================================================

st.set_page_config(
    page_title="MedLens | Evidence-First Clinical Intelligence",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

CLINICAL_CSS = """
<style>
    /* Main background & typography */
    .main {
        background-color: #f8fafc;
    }
    
    /* Header styling */
    .medlens-title {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        font-size: 2.4rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.15rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .medlens-tagline {
        font-size: 1.15rem;
        font-weight: 600;
        color: #0284c7;
        margin-bottom: 0.4rem;
    }
    .medlens-edition {
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #64748b;
        margin-bottom: 1.2rem;
    }
    
    /* Section container styling */
    .clinical-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }

    /* Summary Bar Header */
    .summary-bar {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-left: 4px solid #0284c7;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    /* Provenance Badges */
    .provenance-tag {
        display: inline-flex;
        align-items: center;
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.22rem 0.65rem;
        border-radius: 9999px;
        margin-bottom: 0.6rem;
    }
    .tag-user {
        background-color: #e0f2fe;
        color: #0369a1;
        border: 1px solid #bae6fd;
    }
    .tag-report {
        background-color: #f1f5f9;
        color: #334155;
        border: 1px solid #cbd5e1;
    }
    .tag-ai {
        background-color: #f3e8ff;
        color: #6b21a8;
        border: 1px solid #d8b4fe;
    }
    
    /* Evidence Snippet Container */
    .evidence-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #0d9488;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    }
    .evidence-snippet {
        font-family: 'Consolas', 'Courier New', monospace;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 0.6rem 0.9rem;
        color: #0f172a;
        font-size: 0.9rem;
        margin-top: 0.4rem;
        word-break: break-word;
    }
    
    /* Empty State Container */
    .empty-state-box {
        text-align: center;
        padding: 2.5rem 1.5rem;
        border: 2px dashed #cbd5e1;
        border-radius: 10px;
        background-color: #f8fafc;
        color: #64748b;
        margin: 1rem 0;
    }
    .empty-state-icon {
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
    }
    .empty-state-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #334155;
        margin-bottom: 0.3rem;
    }
    .empty-state-desc {
        font-size: 0.88rem;
        color: #64748b;
    }

    /* Explanation Container */
    .explanation-box {
        background-color: #ffffff;
        border-left: 4px solid #8b5cf6;
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 1rem 0;
        line-height: 1.65;
        color: #1e293b;
    }
</style>
"""

st.markdown(CLINICAL_CSS, unsafe_allow_html=True)


# ==============================================================================
# Session State Initialization
# ==============================================================================

def init_session_state():
    """Ensure persistent session state keys for user inputs, files, and analysis."""
    if "patient_name" not in st.session_state:
        st.session_state.patient_name = ""
    if "patient_age" not in st.session_state:
        st.session_state.patient_age = 0
    if "patient_sex" not in st.session_state:
        st.session_state.patient_sex = "Select..."
    if "patient_symptoms" not in st.session_state:
        st.session_state.patient_symptoms = ""
    if "patient_conditions" not in st.session_state:
        st.session_state.patient_conditions = ""
    if "patient_allergies" not in st.session_state:
        st.session_state.patient_allergies = ""
    if "patient_medications" not in st.session_state:
        st.session_state.patient_medications = ""
    if "uploaded_pdf_name" not in st.session_state:
        st.session_state.uploaded_pdf_name = None
    if "uploaded_pdf_size" not in st.session_state:
        st.session_state.uploaded_pdf_size = 0
    if "uploaded_pdf_bytes" not in st.session_state:
        st.session_state.uploaded_pdf_bytes = None
    if "extracted_pages" not in st.session_state:
        st.session_state.extracted_pages = None
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "analysis_error" not in st.session_state:
        st.session_state.analysis_error = None
    if "demo_preset_triggered" not in st.session_state:
        st.session_state.demo_preset_triggered = False


# ==============================================================================
# Helper & Utility Functions
# ==============================================================================

def format_file_size(size_in_bytes: int) -> str:
    """Format bytes into readable KB or MB."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"


def format_confidence_badge(confidence: str) -> str:
    """Format extraction confidence with intuitive visual indicators."""
    c_lower = str(confidence).lower()
    if "high" in c_lower:
        return "🟢 High confidence"
    elif "medium" in c_lower:
        return "🟡 Medium confidence"
    elif "low" in c_lower:
        return "⚪ Low confidence"
    else:
        return f"⚪ {confidence}"


def extract_text_from_pdf(pdf_bytes: bytes) -> Tuple[List[Dict], Optional[str]]:
    """
    Extract text page-by-page from a PDF using PyMuPDF.
    Preserves page numbers (1-indexed) and detects scanned/empty documents.
    """
    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        pages = []
        total_text_length = 0
        
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_text = page.get_text("text").strip()
            pages.append({
                "page_number": page_idx + 1,
                "text": page_text
            })
            total_text_length += len(page_text)
            
        doc.close()
        
        if len(pages) == 0:
            return [], "The uploaded document contains no pages."
            
        if total_text_length == 0:
            return [], (
                "Scanned or image-only document detected. No digital text could be extracted "
                "from this PDF. Optical Character Recognition (OCR) is not yet supported in this foundation MVP."
            )
            
        return pages, None
    except Exception as e:
        return [], f"Unable to parse PDF document: {str(e)}"


def find_evidence_snippet(
    test_name: str,
    result: str,
    source_str: str,
    pages: Optional[List[Dict]] = None
) -> str:
    """
    Deterministically locates the verbatim supporting text snippet from the raw extracted PDF pages.
    Guarantees zero invented evidence: returns 'Evidence snippet unavailable' if not located.
    """
    if not pages:
        return "Evidence snippet unavailable"

    # Extract target page number
    target_page = 1
    match = re.search(r"(\d+)", str(source_str))
    if match:
        target_page = int(match.group(1))

    # Look in the designated page first, then all pages
    ordered_pages = []
    for p in pages:
        if p.get("page_number") == target_page:
            ordered_pages.insert(0, p)
        else:
            ordered_pages.append(p)

    clean_test = test_name.lower().strip()
    clean_result = result.lower().strip()

    for p in ordered_pages:
        raw_text = p.get("text", "")
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        
        # Priority 1: Line containing both test name and result
        for line in lines:
            line_lower = line.lower()
            if (clean_test in line_lower or any(word in line_lower for word in clean_test.split() if len(word) > 3)) and clean_result in line_lower:
                return line

        # Priority 2: Line containing test name exactly
        for line in lines:
            line_lower = line.lower()
            if clean_test in line_lower:
                return line

    return "Evidence snippet unavailable"


def get_gemini_client() -> Tuple[Optional[genai.Client], Optional[str]]:
    """
    Initializes the Gemini client using the environment variable GEMINI_API_KEY.
    Does NOT crash if the key is missing; returns (None, reason) instead.
    """
    dotenv.load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    
    if not api_key or api_key == "your_gemini_api_key_here":
        return None, (
            "Gemini API key is not configured. To enable AI-powered analysis, "
            "add your GEMINI_API_KEY to the .env file in the project root directory."
        )
        
    try:
        client = genai.Client(api_key=api_key)
        return client, None
    except Exception as e:
        return None, f"Could not initialize Gemini client: {str(e)}"


def validate_and_format_analysis(
    raw_text: str,
    pages: Optional[List[Dict]] = None
) -> Tuple[Optional[pd.DataFrame], Optional[str], Optional[List[Dict]], Optional[str]]:
    """
    Validates the JSON output from the AI model and formats it into the 7-column schema.
    Extracts and attaches verifiable evidence snippets. Rejects malformed outputs.
    """
    try:
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        data = json.loads(cleaned)
        if not isinstance(data, dict):
            return None, None, None, "AI response was not a valid structured object."
            
        measurements = data.get("measurements", [])
        explanation = data.get("summary_explanation", "")
        
        if not isinstance(measurements, list):
            return None, None, None, "Measurements format in AI response is invalid."
            
        rows = []
        evidence_items = []

        for item in measurements:
            if not isinstance(item, dict):
                continue
            test_name = str(item.get("test_name", "")).strip()
            result = str(item.get("result", "")).strip()
            
            if not test_name or not result:
                continue
                
            unit = str(item.get("unit", "Not specified")).strip() or "Not specified"
            ref_range = str(item.get("reference_range", "Not provided")).strip() or "Not provided"
            status = str(item.get("status", "Not determined")).strip() or "Not determined"
            source = str(item.get("source", "Page 1")).strip() or "Page 1"
            confidence_raw = str(item.get("confidence", "High")).strip() or "High"
            confidence_badge = format_confidence_badge(confidence_raw)

            # Locate authentic supporting snippet from the PDF text
            snippet = find_evidence_snippet(test_name, result, source, pages)

            rows.append({
                "Test / Measurement": test_name,
                "Result": result,
                "Unit": unit,
                "Reference Range": ref_range,
                "Status": status,
                "Source": source,
                "Confidence": confidence_badge
            })

            evidence_items.append({
                "test_name": test_name,
                "result": f"{result} {unit}".strip(),
                "reference_range": ref_range,
                "status": status,
                "source": source,
                "confidence": confidence_badge,
                "snippet": snippet
            })
            
        df = pd.DataFrame(rows, columns=[
            "Test / Measurement",
            "Result",
            "Unit",
            "Reference Range",
            "Status",
            "Source",
            "Confidence"
        ])
        
        return df, explanation, evidence_items, None
    except Exception as e:
        return None, None, None, f"Failed to parse structured intelligence: {str(e)}"


def run_gemini_intelligence_pipeline(
    pdf_bytes: bytes,
    patient_context: dict
) -> Tuple[Optional[pd.DataFrame], Optional[str], Optional[List[Dict]], Optional[str]]:
    """
    Executes the full intelligence pipeline:
    1. Extract text page-by-page.
    2. Check API key.
    3. Query Gemini with strict zero-hallucination prompts.
    4. Validate and structure output with evidence snippets.
    """
    # Step 1: Text extraction
    pages, extract_err = extract_text_from_pdf(pdf_bytes)
    if extract_err:
        return None, None, None, extract_err
        
    st.session_state.extracted_pages = pages

    # Step 2: Client initialization
    client, client_err = get_gemini_client()
    if client_err:
        return None, None, None, client_err

    # Prepare document text with page annotations
    doc_sections = []
    for p in pages:
        doc_sections.append(f"--- PAGE {p['page_number']} ---\n{p['text']}")
    full_document_text = "\n\n".join(doc_sections)

    # Format patient context
    patient_info_str = f"""
    - Name: {patient_context.get('name') or 'Not provided'}
    - Age: {patient_context.get('age') or 'Not provided'}
    - Sex: {patient_context.get('sex') or 'Not provided'}
    - Symptoms: {patient_context.get('symptoms') or 'Not provided'}
    - Pre-existing Conditions: {patient_context.get('conditions') or 'Not provided'}
    - Allergies: {patient_context.get('allergies') or 'Not provided'}
    - Current Medications: {patient_context.get('medications') or 'Not provided'}
    """

    prompt = f"""You are MedLens, an AI clinical information intelligence engine.
Your role is to extract verified clinical measurements from the provided medical report and generate a plain-language explanation for the patient.

STRICT CLINICAL SAFETY RULES:
1. Extract ONLY measurements, laboratory tests, vitals, or diagnostic indicators EXPLICITLY present in the source report.
2. NEVER invent, fabricate, or extrapolate any measurement, result, unit, reference range, status, or source.
3. For "reference_range": Use ONLY the reference range explicitly stated in the source report. If the report does not provide a reference range for a test, you MUST set "reference_range" to "Not provided". NEVER invent reference ranges.
4. For "status":
   - If the report explicitly states a flag or status (e.g. "High", "Low", "Normal", "Critical", "Positive", "Negative"), preserve it.
   - If the report provides an explicit reference range and numeric value, classify accurately as "Normal", "High", or "Low" based STRICTLY on that provided range.
   - If the status cannot be determined with certainty, set "status" to "Not determined".
   - NEVER diagnose a disease or clinical condition.
5. For "source": State the exact page where the measurement appears (e.g., "Page 1", "Page 2").
6. For "confidence": Assign "High" for explicitly labeled tables/rows, or "Medium" for narrative text.

EXPLANATION RULES:
1. Explain medical terminology in simple, reassuring, plain language.
2. Explain what the tests measure in the human body in general.
3. Clearly distinguish facts extracted from the report from general educational context.
4. NEVER diagnose the patient (do NOT state "You have X" or "This indicates disease Y").
5. NEVER recommend treatments, medications, dosages, or emergency procedures.
6. Conclude with a clear statement that all results should be discussed with a qualified physician.

USER-PROVIDED PATIENT CONTEXT:
{patient_info_str}

SOURCE MEDICAL REPORT TEXT:
{full_document_text}

Respond ONLY with a JSON object in this EXACT structure:
{{
  "measurements": [
    {{
      "test_name": "Name of test or analyte",
      "result": "Measured value as reported",
      "unit": "Unit of measurement or 'Not specified'",
      "reference_range": "Normal range from report or 'Not provided'",
      "status": "High / Low / Normal / Positive / Negative / Not determined",
      "source": "Page X",
      "confidence": "High / Medium"
    }}
  ],
  "summary_explanation": "Clear, plain-language explanation explaining the measurements and general bodily functions without diagnosing or recommending treatments.",
  "safety_disclaimer": "This explanation is generated for educational and informational purposes only. It does not constitute medical advice, diagnosis, or treatment. Please consult your physician or healthcare provider for clinical evaluation."
}}
"""

    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    last_error = None

    for model_name in models_to_try:
        try:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            )
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )
            if response and response.text:
                return validate_and_format_analysis(response.text, pages)
        except Exception as e:
            last_error = str(e)
            continue

    return None, None, None, f"AI analysis could not be completed: {last_error or 'No response from model'}"


# ==============================================================================
# UI Sections
# ==============================================================================

def render_header():
    """Section 1: Polish Application Header, Tagline & Responsible-AI Notice."""
    st.markdown('<div class="medlens-title">🩺 MedLens</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="medlens-tagline">AI-powered medical report intelligence with evidence you can verify.</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="medlens-edition">🏆 PromptWars x AIMERverse Hackathon Edition • Evidence-First Architecture</div>',
        unsafe_allow_html=True
    )
    
    # Required Responsible-AI notice
    st.info(
        "🛡️ **Responsible AI Notice:** MedLens organizes and explains medical information. "
        "It does not diagnose conditions or provide treatment recommendations."
    )


def render_dashboard_summary_header():
    """Section 2: Compact Patient + Report Dashboard Header."""
    has_patient = bool(st.session_state.patient_name or st.session_state.patient_symptoms)
    has_report = bool(st.session_state.uploaded_pdf_name)

    if not has_patient and not has_report:
        return

    # Determine analysis status badge
    if st.session_state.analysis_result:
        status_badge = "🟢 Complete • Evidence Verified"
    elif st.session_state.uploaded_pdf_name:
        status_badge = "🟡 Document Staged • Ready for Analysis"
    else:
        status_badge = "⚪ Awaiting Document Upload"

    num_pages = len(st.session_state.extracted_pages) if st.session_state.extracted_pages else "—"

    st.markdown(
        f"""
        <div class="summary-bar">
            <div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 1rem;">
                <div style="flex: 1; min-width: 260px;">
                    <span class="provenance-tag tag-user">👤 Patient Context (User-Provided)</span><br>
                    <strong>Name:</strong> {st.session_state.patient_name or "Not provided"} &nbsp;|&nbsp; 
                    <strong>Age:</strong> {st.session_state.patient_age or "—"} &nbsp;|&nbsp; 
                    <strong>Sex:</strong> {st.session_state.patient_sex}<br>
                    <span style="color: #64748b; font-size: 0.88rem;"><strong>Symptoms:</strong> {st.session_state.patient_symptoms or "None reported"}</span>
                </div>
                <div style="flex: 1; min-width: 260px; border-left: 1px solid #e2e8f0; padding-left: 1rem;">
                    <span class="provenance-tag tag-report">📄 Document Context (Report-Extracted)</span><br>
                    <strong>File:</strong> {st.session_state.uploaded_pdf_name or "No file uploaded"} &nbsp;|&nbsp; 
                    <strong>Pages:</strong> {num_pages}<br>
                    <span style="color: #64748b; font-size: 0.88rem;"><strong>Status:</strong> {status_badge}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_provenance_guide():
    """Section: Clear provenance visual distinction guide."""
    with st.expander("ℹ️ Data Provenance & Source Transparency Guide", expanded=False):
        st.markdown(
            """
            To maintain strict clinical safety and auditability, all data displayed in MedLens is categorized into three provenance tiers:
            
            - <span class="provenance-tag tag-user">👤 User-Provided Information</span>: Patient history and symptoms reported directly by the user.
            - <span class="provenance-tag tag-report">📄 Report-Extracted Information</span>: Unmodified measurements, reference ranges, and observations parsed directly from the uploaded medical document.
            - <span class="provenance-tag tag-ai">🤖 AI-Generated Information</span>: Plain-language explanations and educational summaries synthesized under strict guardrails.
            """,
            unsafe_allow_html=True,
        )


def render_patient_form():
    """Section B: Patient Information Form with session state persistence."""
    st.markdown('<span class="provenance-tag tag-user">👤 User-provided information</span>', unsafe_allow_html=True)
    st.markdown("### Patient Context")
    st.caption("Provide baseline clinical context. All fields are stored in local session state.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.text_input(
            "Patient Name",
            key="patient_name",
            placeholder="e.g. Alex Smith",
            help="Full name of the patient (kept in session memory only)."
        )
    with col2:
        st.number_input(
            "Age",
            min_value=0,
            max_value=130,
            step=1,
            key="patient_age",
            help="Patient age in years."
        )

    st.selectbox(
        "Sex",
        options=["Select...", "Female", "Male", "Other", "Prefer not to say"],
        key="patient_sex",
        help="Biological sex as documented on clinical records."
    )

    st.text_area(
        "Symptoms",
        key="patient_symptoms",
        height=85,
        placeholder="e.g. Persistent mild fatigue, routine health review",
        help="Describe present complaints or reasons for the laboratory test."
    )

    col3, col4 = st.columns(2)
    with col3:
        st.text_area(
            "Existing Conditions",
            key="patient_conditions",
            height=85,
            placeholder="e.g. None known, or Hypertension",
            help="Pre-existing or diagnosed chronic conditions."
        )
    with col4:
        st.text_area(
            "Allergies",
            key="patient_allergies",
            height=85,
            placeholder="e.g. No known drug allergies (NKDA)",
            help="Known pharmaceutical or environmental allergies."
        )

    st.text_area(
        "Current Medications",
        key="patient_medications",
        height=85,
        placeholder="e.g. Daily Multivitamin",
        help="Current prescription or over-the-counter medications."
    )


def render_report_uploader():
    """Section C: Medical Report Upload, Sample Loader, and Analyze Action."""
    st.markdown('<span class="provenance-tag tag-report">📄 Report-extracted information</span>', unsafe_allow_html=True)
    st.markdown("### Medical Report Ingestion")
    st.caption("Upload clinical laboratory results, pathology panels, or diagnostic summaries (PDF only).")

    # Upload or load sample
    c_up1, c_up2 = st.columns([3, 1])
    with c_up1:
        uploaded_file = st.file_uploader(
            "Choose a medical report PDF",
            type=["pdf"],
            accept_multiple_files=False,
            help="Only PDF files are accepted. Maximum size: 200MB.",
        )
    with c_up2:
        st.write("")
        st.write("")
        if st.button("📋 Load Demo Report", help="Instantly load the pre-built synthetic lab report for judging."):
            sample_path = os.path.join(os.path.dirname(__file__), "sample_reports", "synthetic_sample_report.pdf")
            if os.path.exists(sample_path):
                with open(sample_path, "rb") as f:
                    sample_bytes = f.read()
                st.session_state.uploaded_pdf_name = "synthetic_sample_report.pdf"
                st.session_state.uploaded_pdf_size = len(sample_bytes)
                st.session_state.uploaded_pdf_bytes = sample_bytes
                st.session_state.analysis_result = None
                st.session_state.analysis_error = None
                if not st.session_state.patient_name:
                    st.session_state.demo_preset_triggered = True
                st.rerun()

    # Check API key configuration status for user feedback
    dotenv.load_dotenv()
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    has_api_key = bool(gemini_key and gemini_key != "your_gemini_api_key_here")

    if not has_api_key:
        st.warning(
            "⚠️ **Gemini API Key Required for AI Analysis:** "
            "Add your `GEMINI_API_KEY` to the `.env` file in the project folder to enable automated extraction and explanations."
        )

    # Process either manually uploaded file or demo-loaded file
    active_bytes = None
    active_name = None

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        # Security & format verification
        if not uploaded_file.name.lower().endswith(".pdf") or not file_bytes.startswith(b"%PDF"):
            st.error("⚠️ **Invalid File Format:** The uploaded document is not a valid PDF file. Please upload a PDF report.")
            st.session_state.uploaded_pdf_name = None
            st.session_state.uploaded_pdf_size = 0
            st.session_state.uploaded_pdf_bytes = None
            return

        if st.session_state.uploaded_pdf_name != uploaded_file.name:
            st.session_state.analysis_result = None
            st.session_state.analysis_error = None

        st.session_state.uploaded_pdf_name = uploaded_file.name
        st.session_state.uploaded_pdf_size = len(file_bytes)
        st.session_state.uploaded_pdf_bytes = file_bytes
        active_bytes = file_bytes
        active_name = uploaded_file.name
    elif st.session_state.uploaded_pdf_bytes is not None:
        active_bytes = st.session_state.uploaded_pdf_bytes
        active_name = st.session_state.uploaded_pdf_name

    if active_bytes is not None:
        file_size = len(active_bytes)
        st.success(f"✓ **Document Safely Received:** `{active_name}` ({format_file_size(file_size)})")
        
        # File properties card
        with st.container():
            c1, c2, c3 = st.columns(3)
            c1.metric("Filename", active_name)
            c2.metric("File Size", format_file_size(file_size))
            c3.metric("Status", "Ready for Extraction")

        st.write("")
        
        # Primary Action: Analyze Report
        analyze_clicked = st.button(
            "🔍 Analyze Report & Verify Evidence",
            type="primary",
            use_container_width=True,
            help="Extract clinical measurements and trace all evidence back to source pages."
        )

        if analyze_clicked:
            if not has_api_key:
                st.error(
                    "❌ **Cannot proceed with AI analysis:** GEMINI_API_KEY is not configured. "
                    "Please add your Gemini API key to `.env` in the MedLens directory and refresh."
                )
                st.session_state.analysis_error = "GEMINI_API_KEY not configured."
            else:
                patient_ctx = {
                    "name": st.session_state.patient_name,
                    "age": st.session_state.patient_age,
                    "sex": st.session_state.patient_sex,
                    "symptoms": st.session_state.patient_symptoms,
                    "conditions": st.session_state.patient_conditions,
                    "allergies": st.session_state.patient_allergies,
                    "medications": st.session_state.patient_medications,
                }

                with st.status("Running Evidence-First Clinical Pipeline...", expanded=True) as status:
                    st.write("1. Document validated and received.")
                    st.write("2. Extracting report text page-by-page via PyMuPDF...")
                    st.write("3. Querying Gemini clinical intelligence engine...")
                    st.write("4. Identifying clinical measurements & verifying source provenance...")
                    st.write("5. Aligning verbatim evidence snippets from source pages...")
                    st.write("6. Generating educational summary with strict safety guardrails...")
                    
                    df, explanation, evidence_items, err = run_gemini_intelligence_pipeline(active_bytes, patient_ctx)
                    
                    if err:
                        status.update(label="Analysis failed", state="error", expanded=True)
                        st.session_state.analysis_error = err
                        st.session_state.analysis_result = None
                    else:
                        status.update(label="Analysis complete & evidence verified!", state="complete", expanded=False)
                        st.session_state.analysis_result = {
                            "df": df,
                            "explanation": explanation,
                            "evidence_items": evidence_items
                        }
                        st.session_state.analysis_error = None
                        st.rerun()

    else:
        st.caption("No report currently uploaded. Supported format: `.pdf` (or click 'Load Demo Report')")


def render_structured_record_and_evidence():
    """Section 3, 4, 5: Structured Record, Evidence Lens & Educational Explanation."""
    st.markdown('<span class="provenance-tag tag-report">📄 Report-extracted information</span>', unsafe_allow_html=True)
    st.markdown("### Structured Clinical Record")
    
    # Required Safety Design Notice
    st.warning(
        "🔒 **Safety Standard:** Reference ranges are used only when provided by the source report. "
        "MedLens does not invent reference ranges."
    )

    # If there is an error from analysis
    if st.session_state.analysis_error:
        st.error(f"⚠️ **Extraction Notice:** {st.session_state.analysis_error}")

    # Display real extracted data if analysis is complete
    if st.session_state.analysis_result and st.session_state.analysis_result.get("df") is not None:
        df = st.session_state.analysis_result["df"]
        explanation = st.session_state.analysis_result.get("explanation", "")
        evidence_items = st.session_state.analysis_result.get("evidence_items", [])

        if len(df) == 0:
            st.info("ℹ️ No specific quantitative laboratory measurements or test values were identified in this document.")
        else:
            st.success(f"✓ **Structured Record Generated:** {len(df)} verified measurements with provenance citations.")
            
            # Display real extracted DataFrame (all 7 required columns)
            st.dataframe(
                df,
                width="stretch",
                hide_index=True,
                column_config={
                    "Test / Measurement": st.column_config.TextColumn("Test / Measurement", help="Identified laboratory test name"),
                    "Result": st.column_config.TextColumn("Result", help="Reported measurement value"),
                    "Unit": st.column_config.TextColumn("Unit", help="Unit of measurement reported"),
                    "Reference Range": st.column_config.TextColumn("Reference Range", help="Normal biological range provided by the testing lab"),
                    "Status": st.column_config.TextColumn("Status", help="Classification based strictly on source report"),
                    "Source": st.column_config.TextColumn("Source", help="Specific page in source document"),
                    "Confidence": st.column_config.TextColumn("Confidence", help="Extraction confidence"),
                },
            )

            st.caption(
                "ℹ️ **Confidence Notice:** Confidence reflects extraction certainty from the source document text, "
                "not clinical or diagnostic certainty."
            )

        # -------------------------------------------------------------
        # Section 3: Evidence Lens — The Main Differentiator
        # -------------------------------------------------------------
        st.write("---")
        st.markdown('<span class="provenance-tag tag-report">📄 Report-extracted information</span>', unsafe_allow_html=True)
        st.markdown("### 🔬 Evidence Lens — Verifiable Source Audit")
        st.caption(
            "Every clinical value below is traced directly to its location in the source PDF. "
            "No evidence or clinical values are ever invented."
        )

        if evidence_items:
            # Interactive Selector for Quick Inspection
            test_names = [item["test_name"] for item in evidence_items]
            selected_test_name = st.selectbox(
                "Select a measurement to audit its supporting evidence:",
                options=test_names,
                help="Inspect the verbatim source document text from which this result was extracted."
            )

            selected_item = next((item for item in evidence_items if item["test_name"] == selected_test_name), None)

            if selected_item:
                snippet_text = selected_item.get("snippet", "Evidence snippet unavailable")
                is_available = snippet_text != "Evidence snippet unavailable"

                st.markdown(
                    f"""
                    <div class="evidence-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <strong style="font-size: 1.05rem; color: #0f172a;">🧪 {selected_item['test_name']}</strong>
                            <span>{selected_item['confidence']}</span>
                        </div>
                        <div style="font-size: 0.9rem; color: #334155; margin-bottom: 0.6rem;">
                            <strong>Extracted Result:</strong> {selected_item['result']} &nbsp;|&nbsp; 
                            <strong>Reference Range:</strong> {selected_item['reference_range']} &nbsp;|&nbsp; 
                            <strong>Report Status:</strong> {selected_item['status']}
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.3rem;">
                            <span class="provenance-tag tag-report">📄 Extracted from report</span>
                            <span style="font-size: 0.85rem; font-weight: 600; color: #0284c7;">📍 Source: {selected_item['source']}</span>
                        </div>
                        <div style="font-size: 0.82rem; color: #64748b; margin-top: 0.4rem;">
                            {'<strong>Verbatim Document Snippet:</strong>' if is_available else '<strong>Audit Status:</strong>'}
                        </div>
                        <div class="evidence-snippet">
                            {snippet_text}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Expandable full list for complete document audit
            with st.expander("📋 View Complete Evidence Matrix (All Measurements)", expanded=False):
                for item in evidence_items:
                    st.markdown(f"**🧪 {item['test_name']}** — `{item['result']}` ({item['source']}) | {item['confidence']}")
                    st.caption(f"Supporting Text: `{item['snippet']}`")
                    st.markdown("---")

        # -------------------------------------------------------------
        # Section 5: AI Explanation
        # -------------------------------------------------------------
        if explanation:
            st.write("---")
            st.markdown('<span class="provenance-tag tag-ai">🤖 AI-generated information</span>', unsafe_allow_html=True)
            st.markdown("### Clinical Summary & Explanation")
            
            st.info(
                "🛡️ **Educational Scope:** MedLens explains information found in the uploaded report. "
                "It does not diagnose conditions, prescribe treatment, or provide dosage advice."
            )

            st.markdown(f'<div class="explanation-box">{explanation}</div>', unsafe_allow_html=True)
            
            st.caption(
                "⚠️ **Safety Disclaimer:** This explanation is synthesized for informational and educational support only. "
                "Always review medical reports with a certified physician or clinical care team."
            )

    else:
        # Empty State & Schema Preview
        st.markdown(
            """
            <div class="empty-state-box">
                <div class="empty-state-icon">📋</div>
                <div class="empty-state-title">Upload a medical report to extract structured clinical information.</div>
                <div class="empty-state-desc">Once a clinical document is analyzed, verified laboratory measurements and verifiable evidence snippets will appear below.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Structured Schema Specification
        schema_columns = [
            "Test / Measurement",
            "Result",
            "Unit",
            "Reference Range",
            "Status",
            "Source",
            "Confidence",
        ]
        empty_df = pd.DataFrame(columns=schema_columns)
        
        with st.expander("🔍 View Expected Clinical Record Schema (Empty Template)", expanded=False):
            st.caption("This template demonstrates the exact column structure reserved for extracted laboratory panels:")
            st.dataframe(
                empty_df,
                width="stretch",
                hide_index=True,
                column_config={
                    "Test / Measurement": st.column_config.TextColumn("Test / Measurement"),
                    "Result": st.column_config.TextColumn("Result"),
                    "Unit": st.column_config.TextColumn("Unit"),
                    "Reference Range": st.column_config.TextColumn("Reference Range"),
                    "Status": st.column_config.TextColumn("Status"),
                    "Source": st.column_config.TextColumn("Source"),
                    "Confidence": st.column_config.TextColumn("Confidence"),
                },
            )


# ==============================================================================
# Main Application Flow
# ==============================================================================

def main():
    init_session_state()
    
    # Handle demo preset before patient widgets instantiate
    if st.session_state.get("demo_preset_triggered"):
        st.session_state.patient_name = "Synthetic Patient (Demo)"
        st.session_state.patient_age = 42
        st.session_state.patient_sex = "Female"
        st.session_state.patient_symptoms = "Routine annual physical checkup"
        st.session_state.demo_preset_triggered = False

    render_header()
    render_provenance_guide()
    render_dashboard_summary_header()

    st.write("---")

    # Balanced 2-column layout for clinical workspace
    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        render_patient_form()

    with right_col:
        render_report_uploader()
        st.write("---")
        render_structured_record_and_evidence()

    # Footer
    st.write("---")
    st.caption(
        "MedLens • PromptWars x AIMERverse Hackathon • Evidence-First Clinical Intelligence • "
        "Strict Clinical Safety Guardrails Active"
    )


if __name__ == "__main__":
    main()
