import streamlit as st
import google.generativeai as genai
import qrcode
from io import BytesIO

# --- AAPKI DETAILS ---
# Maine aapki API Key yahan add kar di hai
API_KEY = "AIzaSyChOXbIDzzeLgenvHV3efcX9d2iOLlza-8" 
UPI_ID = "9546905801@axl" 

# Gemini Setup
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Bharat Health AI", page_icon="🇮🇳")

# Payment Session State
if 'paid' not in st.session_state:
    st.session_state.paid = False

# Header
st.markdown("<h1 style='text-align: center; color: #FF9933;'>🇮🇳 Bharat Health AI</h1>", unsafe_allow_all_html=True)
st.markdown("<p style='text-align: center;'>Har Bharatiya ke liye Sasta aur Sahi Nidaan</p>", unsafe_allow_all_html=True)

# --- PAYMENT SECTION ---
if not st.session_state.paid:
    st.info("🙏 Is seva ko chalane ke liye sirf ₹1 ka yogdan dein.")
    
    # QR Generator
    upi_link = f"upi://pay?pa={UPI_ID}&pn=BharatHealthAI&am=1&cu=INR"
    qr = qrcode.make(upi_link)
    buf = BytesIO()
    qr.save(buf)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(buf, width=250, caption="PhonePe/GPay se Scan Karein")
        if st.button("✅ Maine ₹1 bhej diya hai (Unlock)"):
            st.session_state.paid = True
            st.rerun()

# --- AI DOCTOR SECTION ---
else:
    st.success("✅ AI Doctor Active Hai!")
    symptoms = st.text_area("Apni takleef (Symptoms) batayein:", placeholder="Dard kahan hai? Kabse hai?")
    
    if st.button("Nidaan Dekhein"):
        if symptoms:
            with st.spinner('AI Physician soch raha hai...'):
                prompt = f"Analyze these symptoms in Hindi: {symptoms}. Suggest: 1. Diagnosis 2. Generic medicine salt 3. Home remedies."
                response = model.generate_content(prompt)
                st.markdown("### 📋 Aapki Report:")
                st.write(response.text)
        else:
            st.warning("Kripya apni takleef likhein.")
