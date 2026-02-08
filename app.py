import streamlit as st
import requests
import json

# --- 1. AYARLAR ---
API_KEY = "AIzaSyA97Onyv13VTD-mMYyMLkAML8WymEWnVMk".strip()
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

# --- 2. PREMIUM KESTEL TASARIMI (CSS) ---
st.set_page_config(page_title="Kestel Belediyesi Asistanı", page_icon="🏢", layout="centered")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .main-title { color: #0056b3; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; text-align: center; }
    
    div.stButton > button {
        border-radius: 15px; border: none; background: white; color: #0056b3;
        font-weight: 600; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease; height: 3.5em; width: 100%;
    }
    div.stButton > button:hover { background: #1E5631; color: white; transform: translateY(-2px); }
    
    .info-box { background-color: #0056b3; color: white; padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
    .developer-footer { text-align: center; color: #555; font-size: 14px; margin-top: 50px; padding: 20px; font-family: 'Courier New', monospace; border-top: 1px solid #bdc3c7; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BİLGİ BANKASI ---
KESTEL_REHBERI = {
    "eczane": "💊 **Nöbetçi Eczaneler:** Kestel'deki bugünkü nöbetçi eczane listesine ulaşmak için [BURAYA TIKLAYIN](https://www.aeo.org.tr/NobetciEczaneler). (Bursa Eczacı Odası Resmi Sayfası)",
    "telefoncu": "📱 **Kestel Murat Telekom:** Türkcell, Vodafone ve Türk Telekom bayi işlemleri, fatura ödeme ve her türlü telefon aksesuarı için Kestel merkezdeki en güvenilir noktadır.",
    "metro_ulasim": "🚌 **Kestel Metro Çıkışı:** 2-K ve D-11 hatları istasyondan kalkar. Hem **Kestel Merkez** hem de **Belediye**'ye gider. (D-11: Toplukonut / 2-K: TOKİ)",
    "1k_ulasim": "🚌 **1-K Hattı:** Metroya girmez! Gürsu/Arabayatağı yönünden gelip Meydan ve Belediye'ye gider.",
    "pazar": "📅 **Cuma Pazarı:** Kestel Kapalı Pazar Alanı'nda kurulmaktadır.",
    "belediye_tel": "0224 372 10 01"
}

# --- 4. ANA ARAYÜZ ---
st.markdown("<h1 class='main-title'>🏢 KESTEL BELEDİYESİ</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #444; font-weight: 500;'>Dijital Vatandaş ve Yerel Rehber Asistanı</p>", unsafe_allow_html=True)

st.markdown(f"""
<div class="info-box">
    📢 <b>Hizmet Hattı:</b> Belediyemize <b>{KESTEL_REHBERI['belediye_tel']}</b> numarasından ulaşabilirsiniz.
</div>
""", unsafe_allow_html=True)

# Hızlı Soru Kartları
col1, col2 = st.columns(2)
with col1:
    if st.button("🚌 Ulaşım / Metro"): st.session_state.p = "Metrodan merkeze nasıl giderim?"
    if st.button("💊 Nöbetçi Eczaneler"): st.session_state.p = "Bugün hangi eczane nöbetçi?"
with col2:
    if st.button("📅 Cuma Pazarı"): st.session_state.p = "Pazar ne zaman kuruluyor?"
    if st.button("🍓 Kestel'in Nesi Meşhur?"): st.session_state.p = "Kestel'in nesi meşhur?"

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. SOHBET MOTORU ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Mesajınızı yazın...")
if hasattr(st.session_state, 'p'):
    user_input = st.session_state.p
    del st.session_state.p

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        soru = user_input.lower()
        cevap = ""

        # Yerel Hafıza
        if "eczane" in soru or "nöbetçi" in soru: cevap = KESTEL_REHBERI["eczane"]
        elif any(x in soru for x in ["telefoncu", "turkcell", "vodafone", "telekom", "murat"]): cevap = KESTEL_REHBERI["telefoncu"]
        elif any(x in soru for x in ["metro", "2-k", "d11"]): cevap = KESTEL_REHBERI["metro_ulasim"]
        elif "1-k" in soru or "1k" in soru: cevap = KESTEL_REHBERI["1k_ulasim"]
        elif "pazar" in soru: cevap = KESTEL_REHBERI["pazar"]
        elif "meşhur" in soru or "çilek" in soru: cevap = "🍓 Kestel'in tescilli **sanayi çileği** ve **deveci armudu** meşhurdur!"

        # API Sorgusu
        if not cevap:
            try:
                payload = {"contents": [{"parts": [{"text": f"Kestel Belediyesi asistanısın. Soru: {user_input}"}]}]}
                res = requests.post(URL, json=payload, timeout=5)
                if res.status_code == 200:
                    cevap = res.json()['candidates'][0]['content']['parts'][0]['text']
                else:
                    cevap = f"Üzgünüm, detaylı bilgi için **{KESTEL_REHBERI['belediye_tel']}** numarasından belediyemizi arayınız."
            except:
                cevap = f"Bağlantı hatası. Lütfen **{KESTEL_REHBERI['belediye_tel']}** hattımızı arayınız."

        st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})

# --- 6. GELİŞTİRİCİ İMZASI ---
st.markdown(f"""
<div class="developer-footer">
    👨‍💻 Geliştirici: <b>Yiğit Hamza Yılmaz</b>
</div>

""", unsafe_allow_html=True)
