import streamlit as st
import base64
import os
from dotenv import load_dotenv
from openai import OpenAI
import tempfile

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
client = OpenAI()

sample_prompt = """
You are a medical practitioner and an expert in analyzing medical-related images working for a reputed hospital.
You will be provided with images, and you need to identify any anomalies, diseases, or health issues.
Generate a detailed report covering:
- All findings
- Recommended next steps
- Recommendations
- Additional observations if relevant

Always include a disclaimer: "Consult with a doctor before making any decisions."

If certain aspects cannot be determined from the image, state: "Unable to determine based on the provided image."
"""

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_gpt4_model_for_analysis(filename: str, sample_prompt=sample_prompt):
    base64_image = encode_image(filename)
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": sample_prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "high"}}
            ]
        }
    ]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1500
    )
    return response.choices[0].message.content

def ask_gpt(prompt):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=1000
    )
    return response.choices[0].message.content

# Streamlit UI configurations
st.set_page_config(page_title="Medical Image Diagnostic App", page_icon="🩺", layout="wide")

# Custom CSS styling
st.markdown("""
    <style>
    .top-ribbon {
        background-color: #2E86AB;
        color: white;
        padding: 0.8rem;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        border-radius: 0 0 10px 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .sidebar .sidebar-content {
        background-color: #F4F6F7;
        padding: 20px;
        border-radius: 10px;
    }
    .stButton > button {
        background-color: #2E86AB;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
    }
    .stButton > button:hover {
        background-color: #1B4F72;
    }
    .main-content {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    .main-title {
        font-size: 36px;
        font-weight: bold;
        color: #2E86AB;
        margin-bottom: 0.3rem;
    }
    .subheader {
        font-size: 18px;
        color: #555;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Top Ribbon
st.markdown('<div class="top-ribbon">🩺 Medical Image Diagnostic App</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    #st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Medical_Caduceus.svg/200px-Medical_Caduceus.svg.png", width=80)
    st.markdown("## 🔎 Quick Links")
    st.markdown("""
        - **Upload Image**: Choose your medical image file.
        - **Analyze**: Get AI analysis.
        - **ELI5 Explanation**: Simplified explanation.
        - **Disclaimer**: For informational purposes only.
    """)
    st.markdown("---")
    st.markdown("© 2025 HealthAI Diagnostics")

# Main Content
#st.markdown('<div class="main-content">', unsafe_allow_html=True)

#st.markdown('<div class="main-title">Medical Image Diagnostic Tool</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Analyze medical images using GPT-4 for AI-powered diagnostic insights.</div>', unsafe_allow_html=True)

with st.expander("ℹ️ About this App"):
    st.write("""
        This application leverages OpenAI's GPT-4 model to analyze medical images and provide detailed diagnostic reports.
        **Important**: This is for informational purposes only and does not replace professional medical advice.
    """)

uploaded_file = st.file_uploader("📤 Upload an Image (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        st.session_state['filename'] = tmp_file.name

    st.image(uploaded_file, caption="🖼️ Uploaded Image", width=400)
    st.success("Image uploaded successfully! Click 'Analyze Image' to get the report.")

if st.button('🔎 Analyze Image'):
    if 'filename' in st.session_state and os.path.exists(st.session_state['filename']):
        with st.spinner("Analyzing image, please wait..."):
            result = call_gpt4_model_for_analysis(st.session_state['filename'])
            st.session_state['result'] = result
            st.markdown(f"### 📝 Diagnostic Report\n{result}", unsafe_allow_html=True)
        os.unlink(st.session_state['filename'])

if 'result' in st.session_state and st.session_state['result']:
    st.markdown("---")
    st.markdown("### 💡 Additional Insights")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("🔎 Possible Causes"):
            with st.spinner("Fetching possible causes..."):
                prompt = f"Based on the following diagnostic report, list the possible causes of the disease:\n\n{st.session_state['result']}"
                causes = ask_gpt(prompt)
                st.markdown(f"**Possible Causes:**\n\n{causes}", unsafe_allow_html=True)

    with col2:
        if st.button("🛡️ Precautions"):
            with st.spinner("Fetching precautions..."):
                prompt = f"Based on the following diagnostic report, list the recommended precautions:\n\n{st.session_state['result']}"
                precautions = ask_gpt(prompt)
                st.markdown(f"**Precautions:**\n\n{precautions}", unsafe_allow_html=True)

    with col3:
        if st.button("💊 Future Medications"):
            with st.spinner("Fetching future medications..."):
                prompt = f"Based on the following diagnostic report, suggest possible future medications:\n\n{st.session_state['result']}"
                meds = ask_gpt(prompt)
                st.markdown(f"**Future Medications:**\n\n{meds}", unsafe_allow_html=True)

    with col4:
        if st.button("💡 ELI5 Explanation"):
            with st.spinner("Generating simplified explanation..."):
                prompt = f"Explain the following diagnostic report in simple terms for a 5-year-old:\n\n{st.session_state['result']}"
                eli5 = ask_gpt(prompt)
                st.markdown(f"**Simplified Explanation:**\n\n{eli5}", unsafe_allow_html=True)

    with col5:
        if st.button("💊 Medications Overview"):
            with st.spinner("Fetching medication suggestions..."):
                prompt = (
                    f"Based on the following diagnostic report, suggest a detailed list of possible medications including "
                    f"tablets, ointments, and other required medications that might help a doctor quickly analyze "
                    f"potential treatments. Include dosage recommendations if possible:\n\n{st.session_state['result']}"
                )
                med_overview = ask_gpt(prompt)
                st.markdown(f"**Medication Suggestions:**\n\n{med_overview}", unsafe_allow_html=True)

# Close Main Content
st.markdown('</div>', unsafe_allow_html=True)
