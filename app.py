import io
import re
import json
import subprocess
import pypdfium2 as pdfium
import urllib.request
import urllib.error
import streamlit as st
import shutil

from pypdf import PdfReader

# Optional libraries
try:
    from docx import Document
except ImportError:
    Document = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import pytesseract
    import os

    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
except ImportError:
    pytesseract = None
TESSERACT_PATH = shutil.which("tesseract")


def extract_scanned_pdf_text(pdf_bytes):
    if not TESSERACT_PATH:
        raise RuntimeError(
            "Tesseract OCR is not installed on the server."
        )

    pdf = pdfium.PdfDocument(pdf_bytes)
    extracted_pages = []

    for page in pdf:
        image = page.render(scale=2).to_pil()

        image_buffer = io.BytesIO()
        image.save(image_buffer, format="PNG")

        result = subprocess.run(
            [
                TESSERACT_PATH,
                "stdin",
                "stdout",
                "-l",
                "eng"
            ],
            input=image_buffer.getvalue(),
            capture_output=True
        )

        if result.returncode != 0:
            raise RuntimeError(
                result.stderr.decode(
                    "utf-8", errors="replace"
                )
            )

        extracted_pages.append(
            result.stdout.decode(
                "utf-8", errors="replace"
            )
        )

    return "\n".join(extracted_pages).strip()
st.set_page_config(
    page_title="SafeHands AI",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ SafeHands AI")
st.caption("Career Intelligence and Job Protection Platform")
st.divider()


SKILLS = [
    "python", "java", "javascript", "react", "node.js",
    "html", "css", "sql", "mysql", "mongodb",
    "machine learning", "deep learning", "data science",
    "artificial intelligence", "ai", "excel",
    "power bi", "tableau", "pandas", "numpy",
    "communication", "problem solving", "statistics",
    "data analysis", "git", "github", "streamlit"
]

JOB_ROLES = {
    "Python Developer": [
        "python", "sql", "git", "problem solving"
    ],
    "Data Analyst": [
        "python", "sql", "excel", "power bi", "statistics"
    ],
    "AI / ML Intern": [
        "python", "machine learning", "data science",
        "pandas", "numpy"
    ],
    "Web Developer": [
        "html", "css", "javascript", "react", "node.js"
    ],
    "Data Science Intern": [
        "python", "statistics", "pandas", "numpy",
        "data analysis"
    ]
}


def extract_pdf_text(data):
    pdf = PdfReader(io.BytesIO(data))

    text = "\n".join(
        page.extract_text() or ""
        for page in pdf.pages
    ).strip()

    if not text:
        text = extract_scanned_pdf_text(data)

    return text.strip()


def extract_resume_text(uploaded_file):
    filename = uploaded_file.name.lower()
    data = uploaded_file.getvalue()

    try:
        if filename.endswith(".pdf"):
            text = extract_pdf_text(data)
            if not text:
                return "", (
                    "No readable text found in this PDF. "
                    "It may be a scanned PDF. OCR is needed."
                )
            return text, None

        elif filename.endswith(".docx"):
            if Document is None:
                return "", "Install DOCX support: py -m pip install python-docx"
            document = Document(io.BytesIO(data))
            text = "\n".join(
                paragraph.text for paragraph in document.paragraphs
            )
            return text.strip(), None

        elif filename.endswith(".txt"):
            return data.decode("utf-8", errors="ignore").strip(), None

        elif filename.endswith((".jpg", ".jpeg", ".png")):
            if Image is None or pytesseract is None:
                return "", (
                    "Image OCR support is not ready. "
                    "Install Pillow and pytesseract."
                )
            image = Image.open(io.BytesIO(data))
            text = pytesseract.image_to_string(image)
            return text.strip(), None

        else:
            return "", "Unsupported file format."

    except Exception as exc:
        return "", f"Could not read the file: {exc}"


def find_skills(text):
    lower_text = text.lower()
    found = []

    for skill in SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, lower_text):
            found.append(skill)

    return found


SCAM_WARNINGS = {
    "registration fee": 20,
    "pay registration": 20,
    "joining fee": 20,
    "security deposit": 20,
    "training fee": 15,
    "pay first": 20,
    "guaranteed job": 10,
    "100% guaranteed": 10,
    "no interview": 8,
    "earn money instantly": 10,
    "captcha": 8,
    "whatsapp only": 8,
    "personal bank account": 15,
    "send otp": 25,
    "share your password": 25,
    "limited seats": 5
}


def analyse_job_offer(text):
    lower_text = text.lower()
    score = 0
    found = []

    for phrase, points in SCAM_WARNINGS.items():
        if phrase in lower_text:
            score += points
            found.append(phrase)

    score = min(score, 100)

    if score >= 50:
        level = "High Risk"
    elif score >= 25:
        level = "Medium Risk"
    else:
        level = "Low Risk"

    return score, level, found


if "resume_skills" not in st.session_state:
    st.session_state.resume_skills = []

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""


st.sidebar.title("SafeHands AI")

page = st.sidebar.radio(
    "Choose a Module",
    [
        "Home",
        "Job Protection",
        "Resume Analyzer",
        "Job Matching",
        "Career AI Assistant"
    ]
)


if page == "Home":
    st.header("Welcome to SafeHands AI 👋")
    st.write(
        "A beginner-friendly platform to help job seekers "
        "identify suspicious job offers and improve career readiness."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🛡️ Job Protection")
        st.write("Check job offers for common warning signs.")

    with col2:
        st.subheader("📄 Resume Analyzer")
        st.write("Extract skills from your resume.")

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("🎯 Job Matching")
        st.write("Compare your resume skills with job roles.")

    with col4:
        st.subheader("🤖 Career Assistant")
        st.write("Get career guidance and learning suggestions.")

    st.info(
        "SafeHands AI is a prototype. Always independently "
        "verify employers and job offers before sharing money "
        "or personal information."
    )


elif page == "Job Protection":
    st.header("🛡️ Job Protection")
    st.write("Paste a job offer or upload a job advertisement.")

    offer_text = st.text_area(
        "Paste Job Offer",
        height=200,
        placeholder="Paste the complete job offer, WhatsApp message or email here..."
    )

    offer_file = st.file_uploader(
        "Upload Job Offer (PDF or TXT)",
        type=["pdf", "txt"],
        key="job_offer_upload"
    )

    if st.button("Analyse Job Offer", type="primary"):
        combined_text = offer_text.strip()

        if offer_file is not None:
            try:
                if offer_file.name.lower().endswith(".txt"):
                    file_text = offer_file.getvalue().decode(
                        "utf-8", errors="ignore"
                    )
                else:
                    file_text = extract_pdf_text(offer_file.getvalue())

                combined_text += "\n" + file_text

            except Exception as exc:
                st.error(f"Could not read offer file: {exc}")
                combined_text = ""

        if not combined_text.strip():
            st.warning("Please paste a job offer or upload a file.")
        else:
            score, level, found = analyse_job_offer(combined_text)

            st.subheader("Analysis Result")
            st.metric("Warning Score", f"{score}/100")

            if level == "High Risk":
                st.error("High Risk: Several warning signs were detected.")
            elif level == "Medium Risk":
                st.warning("Medium Risk: Please verify this offer carefully.")
            else:
                st.success("Low Risk: Few warning signs were detected.")

            if found:
                st.write("**Warning phrases found:**")
                for phrase in found:
                    st.write(f"- {phrase}")
            else:
                st.write("No listed warning phrases were detected.")

            st.subheader("Safety Suggestions")
            st.write("- Never pay money to get a job.")
            st.write("- Verify the company website and official email.")
            st.write("- Never share OTPs or passwords.")
            st.write("- Check the employer independently.")

            st.caption(
                "This score is based on simple keyword rules. "
                "It does not prove that a job is fake or genuine."
            )


elif page == "Resume Analyzer":
    st.header("📄 Resume Analyzer")
    st.write(
        "Upload your resume to extract skills and receive "
        "basic improvement suggestions."
    )

    resume_file = st.file_uploader(
        "Choose your resume",
        type=["pdf", "docx", "txt", "jpg", "jpeg", "png"],
        key="resume_upload"
    )

    if st.button("Analyse My Resume", type="primary"):
        if resume_file is None:
            st.warning("Please upload your resume first.")
        else:
            text, error = extract_resume_text(resume_file)

            if error:
                st.error(error)
            elif not text.strip():
                st.warning("No readable text was found in this file.")
            else:
                skills = find_skills(text)
                st.session_state.resume_text = text
                st.session_state.resume_skills = skills

                st.success("Resume analysed successfully!")
                st.subheader("Extracted Skills")

                if skills:
                    for skill in skills:
                        st.write(f"✅ {skill}")
                else:
                    st.info("No matching skills were detected.")

                st.subheader("Resume Improvement Suggestions")

                if skills:
                    st.write(
                        "Add project details, practical experience "
                        "and measurable achievements wherever applicable."
                    )
                else:
                    st.write(
                        "Mention your technical skills clearly in "
                        "a separate Skills section."
                    )

                st.write(
                    f"**Extracted text length:** {len(text)} characters"
                )


elif page == "Job Matching":
    st.header("🎯 Job Matching")
    st.write(
        "Compare the skills extracted from your resume "
        "with different job roles."
    )

    if not st.session_state.resume_skills:
        st.warning(
            "Please analyse your resume first in the Resume Analyzer module."
        )
    else:
        st.write("**Your detected skills:**")
        st.write(", ".join(st.session_state.resume_skills))
        st.divider()

        for role, required_skills in JOB_ROLES.items():
            matched = [
                skill for skill in required_skills
                if skill in st.session_state.resume_skills
            ]

            missing = [
                skill for skill in required_skills
                if skill not in st.session_state.resume_skills
            ]

            percentage = round(
                len(matched) / len(required_skills) * 100
            )

            st.subheader(role)
            st.progress(percentage / 100)
            st.write(f"**Skill Match: {percentage}%**")
            st.write(
                "**Matched skills:** "
                + (", ".join(matched) if matched else "None")
            )
            st.write(
                "**Skills to learn:** "
                + (", ".join(missing) if missing else "None")
            )
            st.divider()


elif page == "Career AI Assistant":
    st.header("🤖 Career AI Assistant")
    st.write(
        "Get a basic learning roadmap or connect a local "
        "Ollama model for AI-generated guidance."
    )

    question = st.text_area(
        "Ask your career question",
        placeholder="Example: How can I become a Data Analyst?"
    )

    st.subheader("Career Roadmap")

    selected_role = st.selectbox(
        "Choose your target role",
        list(JOB_ROLES.keys())
    )

    if st.button("Show My Learning Roadmap"):
        st.subheader(f"Roadmap: {selected_role}")
        required = JOB_ROLES[selected_role]

        for number, skill in enumerate(required, start=1):
            st.write(f"{number}. Learn and practise {skill}")

        st.write("Next steps:")
        st.write("- Build small practical projects.")
        st.write("- Upload your projects to GitHub.")
        st.write("- Prepare your resume.")
        st.write("- Practise interview questions.")

    st.divider()
    st.subheader("Optional Local AI Assistant")

    st.caption(
        "This feature works only when Ollama is installed, "
        "running and has a model downloaded."
    )

    if st.button("Ask Local AI"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            try:
                payload = {
                    "model": "qwen:4b",
                    "prompt": question,
                    "stream": False
                }

                request = urllib.request.Request(
                    "http://localhost:11434/api/generate",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )

                with urllib.request.urlopen(
                    request, timeout=120
                ) as response:
                    result = json.loads(
                        response.read().decode("utf-8")
                    )

                st.subheader("AI Response")
                st.write(
                    result.get("response", "No response received.")
                )

            except urllib.error.URLError:
                st.error(
                    "Ollama is not running or is not installed. "
                    "Start Ollama and download the qwen3:4b model first."
                )

            except Exception as exc:
                st.error(f"AI Assistant error: {exc}")


st.divider()

st.caption(
    "SafeHands AI Prototype | 2026 | "
    "Use independent verification before sharing personal information."
)
