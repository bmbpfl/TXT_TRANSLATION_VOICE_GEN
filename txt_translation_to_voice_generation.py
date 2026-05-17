import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import io
import base64
from docx import Document
from PyPDF2 import PdfReader

st.write("Text Translation & Voice Generation")

LANG_MAP = {
    "tamil": "ta",
    "hindi": "hi",
    "telugu": "te",
    "malayalam": "ml",
    "kannada": "kn",
    "marathi": "mr",
    "gujarati": "gu",
    "bengali": "bn",
    "urdu": "ur",
    "english": "en"
}

target_language = st.selectbox(
    "Select the target language:",
    list(LANG_MAP.keys())
)

uploaded_file = st.file_uploader(
    "Upload your English Text/PDF/DOCX file",
    type=["txt", "pdf", "docx"]
)

# -----------------------------
# Helper Functions
# -----------------------------

def extract_text_from_txt(file):
    
    return file.read().decode("utf-8")


def extract_text_from_docx(file):
    
    doc = Document(file)
    text = []

    for para in doc.paragraphs:
        text.append(para.text)

    return "\n".join(text)

def extract_text_from_pdf(file):
    
    pdf_reader = PdfReader(file)
    text = ""

    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    return text


# Initialize session state

if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""

if uploaded_file:

    file_type = uploaded_file.name.split(".")[-1].lower()

    try:

        # Read based on file type

        if file_type == "txt":
            english_content = extract_text_from_txt(uploaded_file)

        elif file_type == "docx":
            english_content = extract_text_from_docx(uploaded_file)

        elif file_type == "pdf":
            english_content = extract_text_from_pdf(uploaded_file)

        else:
            english_content = ""

        st.subheader("Original Text")
        st.text_area(
            "Extracted Content",
            english_content,
            height=250
        )

        if st.button("Translate Now"):
            try:
                translator = GoogleTranslator(
                    source="auto",
                    target=LANG_MAP[target_language]
                )

                st.session_state.translated_text = translator.translate(
                    english_content
                )

            except Exception as e:
                st.error(f"Translation error: {e}")

    except Exception as e:
        st.error(f"File reading error: {e}")

# -----------------------------
# Show translated text
# -----------------------------

if st.session_state.translated_text:

    st.subheader(
        f"Translated Text ({target_language.capitalize()})"
    )

    st.text_area(
        "Result",
        st.session_state.translated_text,
        height=250
    )

    # Download translated text

    st.download_button(
        label="Download Translation",
        data=st.session_state.translated_text,
        file_name=f"translated_{target_language}.txt",
        mime="text/plain"
    )

    # Copy button
    b64_text = base64.b64encode(
        st.session_state.translated_text.encode()
    ).decode()

    st.markdown(
        f"""
        <button onclick="navigator.clipboard.writeText(atob('{b64_text}'))">
            📋 Copy Translated Text
        </button>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # -----------------------------
    # TEXT TO SPEECH
    # -----------------------------

    file_name = st.text_input("Audio File Name")

    if file_name:
        file_name = file_name + ".mp3"

    if st.button("Generate Voice Output"):
        try:
            tts = gTTS(
                text=st.session_state.translated_text,
                lang=LANG_MAP[target_language],
                slow=False
            )

            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            st.audio(audio_buffer, format="audio/mp3")

            st.download_button(
                label="Download Audio",
                data=audio_buffer,
                file_name=file_name,
                mime="audio/mpeg"
            )

            st.success("Audio generated successfully.")

        except Exception as e:
            st.error(f"Audio generation failed: {e}")