import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from fpdf import FPDF  # ya fpdf2 install karke from fpdf2 import FPDF
import io
from datetime import datetime

# ─── 1. API CONFIG ───
genai.configure(api_key="AIzaSyBHKEo_9oFgO3FTYjuuJ2zeiiNMkG3eOQI")

try:
    # Best current model Feb 2026: fast, cheap, powerful
    model = genai.GenerativeModel("gemini-2.5-flash")
    # Agar powerful chahiye (thoda costly): "gemini-2.5-pro"
except Exception as e:
    st.error(f"Model load nahi hua: {e}\nAPI key check karo ya Google AI Studio mein quota dekho.")
    st.stop()

# Note: Old SDK (google-generativeai) deprecated ho raha hai → future mein google-genai SDK pe migrate kar lena
# pip install --upgrade google-genai

# ─── 2. PAGE SETUP ───
st.set_page_config(page_title="Bharat Health AI", page_icon="👩‍⚕️", layout="centered")

# ─── 3. CUSTOM CSS ───
st.markdown("""
    <style>
    .main { background-color: #fffafb; }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.5em; 
        background-color: #d81b60; color: white; font-weight: bold; border: none;
        font-size: 1.1rem;
    }
    .report-box { 
        border: 2px solid #d81b60; padding: 20px; border-radius: 15px; 
        background-color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

if 'paid' not in st.session_state:
    st.session_state.paid = False

# ─── 4. HEADER ───
st.title("🇮🇳 Bharat Health AI")
st.markdown("#### **Apka Digital Doctor Sahayak** 👩‍⚕️")
st.divider()

# ─── 5. PAYMENT (₹5 UPI) ───
if not st.session_state.paid:
    st.info("🙏 Gareeb kalyan ke liye sirf **₹5** donate karein. Bahut shukriya Patna walo! ❤️")
    your_upi_id = "9546905801@axl"
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={your_upi_id}&pn=BharatHealthAI&am=5.00&cu=INR"
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(qr_url, caption="QR Scan karke ₹5 bhejein")
    with col2:
        st.markdown("### Unlock Karein")
        if st.button("✅ Payment Ho Gaya Hai", type="primary"):
            st.session_state.paid = True
            st.rerun()

# ─── 6. MAIN DOCTOR SECTION ───
else:
    st.markdown("### 📝 Patient Ki Jankari Bharein")
    c1, c2 = st.columns(2)
    p_name    = c1.text_input("Patient Ka Naam", placeholder="Pura naam likhein")
    p_age     = c2.text_input("Umar (Age)", placeholder="Saal mein")
    p_contact = st.text_input("Mobile Number", placeholder="10 digit number (optional)")
    symptoms  = st.text_area("Lakshan Bataiye", 
                             placeholder="Jaise: 3 din se bukhar, khansi, gale mein dard...",
                             height=130)

    if st.button("🔍 Report Banayein – Doctor Sahiba Taiyar!", type="primary"):
        if p_name.strip() and symptoms.strip():
            with st.spinner("Doctor Sahiba report likh rahi hain..."):
                current_date = datetime.now().strftime("%d-%m-%Y %H:%M IST")
                
                prompt = (
                    f"Ek experienced female Indian MBBS doctor ban kar jawab do. "
                    f"Bolne ka style: simple, polite, Hindi-English mix (easy samajh aaye). "
                    f"Patient: {p_name}, Umar: {p_age or 'N/A'}, Contact: {p_contact or 'N/A'}. "
                    f"Main lakshan: {symptoms}. "
                    f"Report English mein banao, lekin zarurat pade to Hindi shabd use karo. "
                    f"Structure yeh rakho:\n"
                    f"1. Sambhavit Samasya (Primary Impression)\n"
                    f"2. Generic Dawai ke Salts / Suggestions (brand name nahi)\n"
                    f"3. Khurak aur Kitne Din (Dosage & Duration)\n"
                    f"4. Ghar ke Upay aur Lifestyle Salah\n"
                    f"5. Kab Turant Doctor ke Paas Jaana Hai\n\n"
                    f"End mein bold disclaimer: **Yeh AI dwara banaya gaya salah hai sirf jaankari ke liye. Emergency mein ya sahi ilaaj ke liye registered doctor se milein.**"
                )
                
                try:
                    response = model.generate_content(prompt)
                    report_text = response.text.strip()
                except Exception as e:
                    st.error(f"AI se report nahi bana: {str(e)}\nAPI key quota check karo ya thodi der baad try karo.")
                    st.stop()

                # ─── SHOW REPORT ───
                st.markdown("---")
                st.subheader(f"Report Taiyar – {current_date}")
                st.markdown(f"**Patient:** {p_name} | **Umar:** {p_age or 'N/A'}")
                st.markdown(report_text)

                # ─── PDF BANAO ───
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 20)
                pdf.set_text_color(216, 27, 96)
                pdf.cell(200, 10, txt="BHARAT HEALTH AI", ln=True, align='C')
                pdf.set_font("Arial", 'I', 10)
                pdf.set_text_color(0)
                pdf.cell(200, 10, txt="Digital Health Sahayak", ln=True, align='C')
                pdf.ln(5)
                pdf.line(10, 32, 200, 32)

                pdf.ln(10)
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(100, 10, txt=f"Patient: {p_name}")
                pdf.cell(100, 10, txt=f"Date: {current_date}", ln=True, align='R')
                pdf.cell(100, 10, txt=f"Age: {p_age or 'N/A'}")
                pdf.cell(100, 10, txt=f"Contact: {p_contact or 'N/A'}", ln=True, align='R')
                pdf.ln(15)

                pdf.set_font("Arial", 'B', 14)
                pdf.cell(200, 10, txt="SALAH / PRESCRIPTION:", ln=True)
                pdf.ln(5)
                pdf.set_font("Arial", size=11)
                
                # Unicode safe
                try:
                    pdf.multi_cell(0, 8, report_text)
                except:
                    safe_text = report_text.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 8, safe_text)

                pdf.ln(15)
                pdf.set_font("Arial", 'I', 8)
                pdf.set_text_color(120, 120, 120)
                pdf.multi_cell(0, 5, "Note: Yeh AI generated report sirf informational hai. "
                                    "Emergency ya sahi diagnosis ke liye turant doctor se sampark karein.")

                pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='replace')

                st.download_button(
                    "📥 PDF Download Karein",
                    data=pdf_bytes,
                    file_name=f"BharatHealth_{p_name.replace(' ', '_')}_{current_date.replace(':', '-')}.pdf",
                    mime="application/pdf"
                )

                # ─── HINDI VOICE ───
                try:
                    voice_msg = f"Namaste {p_name} ji. Doctor Sahiba keh rahi hain: {report_text[:600]} ... aur aaram se rest karein."
                    tts = gTTS(voice_msg, lang='hi', slow=False)
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    audio_fp.seek(0)
                    st.audio(audio_fp, format='audio/mp3')
                    st.caption("🔊 Hindi mein suniye – Doctor ki awaaz")
                except Exception as e:
                    st.warning(f"Voice nahi bani: {e} (internet check karo)")

        else:
            st.warning("Naam aur lakshan dono bhariye pehle!")

    # Sidebar
    with st.sidebar:
        st.markdown("### Controls")
        if st.button("🔄 Naya Patient"):
            st.session_state.paid = False
            st.rerun()

st.markdown("---")
st.caption("Made with ❤️ in Patna, Bihar | AI se salah lekin doctor se milna na bhoolen!")
