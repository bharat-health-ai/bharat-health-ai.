import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from fpdf import FPDF
import io
from datetime import datetime

# --- 1. API CONFIGURATION ---
genai.configure(api_key="AIzaSyChOXbIDzzeLgenvHV3efcX9d2iOLlza-8")
model = genai.GenerativeModel('gemini-pro')

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Bharat Health AI", page_icon="👩‍⚕️", layout="centered")

# --- 3. CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #fffafb; }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.5em; 
        background-color: #d81b60; color: white; font-weight: bold; border: none;
    }
    .report-box { border: 2px solid #d81b60; padding: 20px; border-radius: 15px; background-color: white; }
    </style>
    """, unsafe_allow_html=True)

if 'paid' not in st.session_state:
    st.session_state.paid = False

# --- 4. HEADER ---
st.title("🇮🇳 Bharat Health AI")
st.markdown("#### **Digital Health Assistant** 👩‍⚕️")
st.divider()

# --- 5. PAYMENT SECTION (₹5) ---
if not st.session_state.paid:
    st.info("🙏 Is gareeb kalyan seva ke liye sirf ₹5 ka yogdan dein.")
    your_upi_id = "9546905801@axl"
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={your_upi_id}&pn=BharatHealthAI&am=5.00&cu=INR"
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(qr_url, caption="Scan to Pay ₹5")
    with col2:
        st.write("### Step 2: Unlock")
        if st.button("✅ Maine Payment Kar Diya Hai"):
            st.session_state.paid = True
            st.rerun()

# --- 6. DOCTOR INTERFACE ---
else:
    st.markdown("### 📝 Patient & Medical Details")
    c1, c2 = st.columns(2)
    p_name = c1.text_input("Patient Name:", placeholder="Naam")
    p_age = c2.text_input("Age:", placeholder="Umar")
    p_contact = st.text_input("Contact Number:", placeholder="Mobile")
    user_input = st.text_area("Symptoms (Lakshan):", placeholder="Describe health issue...")

    if st.button("🔍 Generate Professional Report"):
        if user_input and p_name:
            with st.spinner('Doctor Sahiba is preparing your prescription...'):
                current_date = datetime.now().strftime("%d-%m-%Y %H:%M")
                
                # AI Prompt
                prompt = (f"Act as a professional female Indian doctor. Patient: {p_name}, Age: {p_age}. "
                          f"Symptoms: {user_input}. Generate a medical report in Simple English. "
                          f"Include: 1. Primary Impression 2. Suggested Generic Medicine Salts 3. Lifestyle Advice. "
                          f"Disclaimer: This is an AI assistant, consult a real doctor for emergencies.")
                
                response = model.generate_content(prompt)
                report_body = response.text

                # --- DISPLAY REPORT ON SCREEN ---
                st.markdown("---")
                st.markdown(f"**Date:** {current_date}")
                st.code(f"PATIENT: {p_name} | AGE: {p_age}\n\n{report_body}", language=None)

                # --- PROFESSIONAL PDF GENERATION ---
                pdf = FPDF()
                pdf.add_page()
                
                # Header
                pdf.set_font("Arial", 'B', 20)
                pdf.set_text_color(216, 27, 96) # Pinkish color
                pdf.cell(200, 10, txt="BHARAT HEALTH AI", ln=True, align='C')
                pdf.set_font("Arial", 'I', 10)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(200, 10, txt="Your Digital Medical Assistant", ln=True, align='C')
                pdf.ln(5)
                pdf.line(10, 32, 200, 32) # Horizontal line
                
                # Patient Info Table Look
                pdf.ln(10)
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(100, 10, txt=f"Patient: {p_name}")
                pdf.cell(100, 10, txt=f"Date: {current_date}", ln=True, align='R')
                pdf.cell(100, 10, txt=f"Age: {p_age}")
                pdf.cell(100, 10, txt=f"Contact: {p_contact}", ln=True, align='R')
                pdf.ln(10)
                
                # Report Content
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(200, 10, txt="PRESCRIPTION / ADVICE:", ln=True)
                pdf.ln(2)
                pdf.set_font("Arial", size=11)
                pdf.multi_cell(0, 8, txt=report_body)
                
                # Footer Disclaimer
                pdf.ln(20)
                pdf.set_font("Arial", 'I', 8)
                pdf.set_text_color(150, 150, 150)
                pdf.multi_cell(0, 5, txt="Note: This is an AI-generated report for informational purposes. Please visit a registered medical practitioner for a formal diagnosis.")
                
                pdf_output = pdf.output(dest='S').encode('latin-1', 'ignore')
                
                st.download_button(
                    label="📥 Download Professional PDF",
                    data=pdf_output,
                    file_name=f"Prescription_{p_name}.pdf",
                    mime="application/pdf"
                )

                # --- HINDI VOICE ---
                try:
                    # Voice will still explain in Hindi for ease of patient
                    voice_prompt = f"Patient {p_name}, Doctor Sahiba kehti hain: {report_body}"
                    tts = gTTS(text=voice_prompt, lang='hi')
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    st.audio(fp, format='audio/mp3')
                except:
                    pass
        else:
            st.error("Please fill Name and Symptoms!")

    if st.sidebar.button("🔄 New Patient"):
        st.session_state.paid = False
        st.rerun()
                
