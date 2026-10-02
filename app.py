import os
import html
from datetime import date

import requests
import streamlit as st

from dotenv import load_dotenv

from backend.services.document_formatter import (
    format_docx,
    format_pdf,
    format_txt,
)


load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8001"
).rstrip("/")


st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        color: #666;
        font-size: 17px;
        margin-top: 0;
    }

    .preview {
        background: #111827;
        color: #F9FAFB;
        border-radius: 14px;
        padding: 24px;
        min-height: 500px;
        max-height: 650px;
        overflow-y: auto;
        white-space: pre-wrap;
        font-family: Georgia, serif;
        line-height: 1.65;
    }

    .notice {
        background: #FFF7ED;
        border-left: 5px solid #F59E0B;
        padding: 12px 16px;
        border-radius: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# HEADER
# -----------------------------

left, center, right = st.columns(
    [1, 3, 1]
)


with center:

    logo = "assets/legalease_logo.png"

    if os.path.exists(logo):

        st.image(
            logo,
            width=130
        )

    st.markdown(
        '<p class="main-title">LegalEase</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="subtitle">'
        'AI-Powered Legal Document Generator'
        '</p>',
        unsafe_allow_html=True
    )


st.markdown(
    '<div class="notice">'
    'LegalEase creates document drafts. '
    'Review the output for your facts and '
    'applicable jurisdiction before signing '
    'or relying on it.'
    '</div>',
    unsafe_allow_html=True
)


st.divider()


# -----------------------------
# SESSION STATE
# -----------------------------

if "document" not in st.session_state:

    st.session_state.document = ""


if "editing" not in st.session_state:

    st.session_state.editing = False


# -----------------------------
# DOCUMENT FORM
# -----------------------------

with st.form("document_form"):

    st.subheader(
        "1. Document details"
    )

    column1, column2 = st.columns(2)


    with column1:

        document_type = st.selectbox(
            "Document type",
            [
                "Employment Contract",
                "Non-Disclosure Agreement (NDA)",
                "Lease Agreement",
                "Freelance Work Contract",
                "Employment Offer Letter",
                "General Agreement",
                "Custom Legal Document",
            ]
        )

        if document_type == "Custom Legal Document":

            document_type = st.text_input(
                "Custom document type",
                "Service Agreement"
            )


    with column2:

        effective_date = st.date_input(
            "Effective date",
            value=date.today()
        )

        effective_date = (
            effective_date.strftime(
                "%B %d, %Y"
            )
        )


    parties = st.text_area(
        "Parties involved",
        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),
        height=100,
    )


    terms = st.text_area(
        "Terms & Conditions — "
        "separate clauses with semicolons",
        placeholder=(
            "Payment within 30 days; "
            "Confidentiality must be maintained; "
            "Either party may terminate with "
            "15 days notice"
        ),
        height=140,
    )


    submitted = st.form_submit_button(
        "✨ Generate Document",
        use_container_width=True
    )


# -----------------------------
# GENERATE
# -----------------------------

if submitted:

    if (
        not parties.strip()
        or not terms.strip()
    ):

        st.error(
            "Please enter the parties and terms."
        )

    else:

        with st.spinner(
            "Generating your document..."
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/generate",

                    json={
                        "document_type": document_type,
                        "parties": parties,
                        "terms": terms,
                        "effective_date": effective_date,
                    },

                    timeout=120,
                )


                if response.ok:

                    data = response.json()

                    st.session_state.document = (
                        data["document"]
                    )

                    st.session_state.model = (
                        data.get("model", "")
                    )

                    st.session_state.mock = (
                        data.get("mock", False)
                    )

                    st.success(
                        "Document generated successfully."
                    )


                else:

                    try:

                        detail = response.json().get(
                            "detail",
                            response.text
                        )

                    except Exception:

                        detail = response.text

                    st.error(
                        f"Backend error: {detail}"
                    )


            except requests.RequestException as exc:

                st.error(
                    "Could not connect to the "
                    "FastAPI backend."
                )

                st.caption(
                    "Start it with: "
                    "`uvicorn backend.main:app "
                    "--reload --port 8000`"
                )

                st.caption(str(exc))


# -----------------------------
# PREVIEW
# -----------------------------

if st.session_state.document:

    st.divider()

    st.subheader(
        "2. Preview & edit"
    )


    if st.session_state.get("mock"):

        st.info(
            "Mock AI mode is active. "
            "This is useful for testing "
            "without Gemini."
        )


    if st.button(
        "✏️ Click to Edit Document"
    ):

        st.session_state.editing = True


    if st.session_state.editing:

        edited = st.text_area(
            "Editable document",
            value=st.session_state.document,
            height=600,
        )


        if st.button(
            "💾 Save Edits"
        ):

            st.session_state.document = edited

            st.session_state.editing = False

            st.rerun()


    preview = html.escape(
        st.session_state.document
    )


    st.markdown(
        f'<div class="preview">{preview}</div>',
        unsafe_allow_html=True
    )


    # -----------------------------
    # DOWNLOAD
    # -----------------------------

    st.subheader(
        "3. Download"
    )


    d1, d2, d3 = st.columns(3)


    txt_bytes = format_txt(
        st.session_state.document
    )


    docx_bytes = format_docx(
        st.session_state.document,
        document_type,
        terms
    )


    pdf_bytes = format_pdf(
        st.session_state.document,
        document_type
    )


    with d1:

        st.download_button(
            "⬇️ Download TXT",
            data=txt_bytes,
            file_name="LegalEase_document.txt",
            mime="text/plain",
            use_container_width=True,
        )


    with d2:

        st.download_button(
            "⬇️ Download DOCX",
            data=docx_bytes,
            file_name="LegalEase_document.docx",
            mime=(
                "application/"
                "vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            use_container_width=True,
        )


    with d3:

        st.download_button(
            "⬇️ Download PDF",
            data=pdf_bytes,
            file_name="LegalEase_document.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


# -----------------------------
# SIDEBAR
# -----------------------------

with st.sidebar:

    st.header("LegalEase")

    st.caption(
        "FastAPI + Streamlit + Gemini"
    )

    st.write(
        f"Backend: `{BACKEND_URL}`"
    )


    try:

        response = requests.get(
            f"{BACKEND_URL}/health",
            timeout=3
        )

        if response.ok:

            st.success(
                "Backend online"
            )

        else:

            st.warning(
                "Backend returned an error"
            )

    except requests.RequestException:

        st.error(
            "Backend offline"
        )


    st.divider()

    st.caption(
        "Supported exports: "
        "TXT • DOCX • PDF"
    )