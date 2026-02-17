import streamlit as st
import json
import time
import urllib.parse
from groq import Groq

# --- CONFIGURAZIONE ---
if "GROQ_API_KEY" in st.secrets:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
else:
    GROQ_KEY = "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"

WA_NUMBER = "393488231234"
B_ORANGE = "#FF6B35"
B_DARK = "#050A14"

st.set_page_config(page_title="Blueberry Travel AI Expert", page_icon="🗾", layout="centered")

def apply_blueberry_ui():
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {B_DARK}; color: #F0F2F6; font-family: 'Inter', sans-serif; }}
        [data-testid="stHeader"], [data-testid="stToolbar"] {{ display: none; }}
        .stChatMessage {{ border-radius: 24px; padding: 1.5rem; margin-bottom: 1rem; border: 1px solid rgba(255,255,255,0.08) !important; background-color: transparent !important; }}
        .stChatMessage[data-testid="stChatMessageAssistant"] {{ background-color: #0B1426 !important; border-left: 4px solid {B_ORANGE} !important; }}
        .travel-card {{ background: #111B2D; border: 1px solid rgba(255,107,53,0.15); border-radius: 22px; overflow: hidden; margin-bottom: 20px; }}
        .card-img {{ width: 100%; height: 180px; object-fit: cover; }}
        .btn-wa {{ text-align: center; background: #25D366; color: white !important; text-decoration: none; padding: 12px; border-radius: 14px; display: block; font-weight: bold; font-size: 13px; }}
        .btn-info {{ text-align: center; background: transparent; border: 1px solid {B_ORANGE}; color: {B_ORANGE} !important; text-decoration: none; padding: 10px; border-radius: 14px; display: block; margin-top: 8px; font-size: 11px; }}
        </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_viaggi():
    try:
        with open('viaggi_full.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

client = Groq(api_key=GROQ_KEY)

def chat_ai(messages):
    try:
        with open("istruzioni.txt", "r", encoding="utf-8") as f:
            sys_prompt = f.read()
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": sys_prompt}] + messages,
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Errore di connessione: {str(e)}"

apply_blueberry_ui()

if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome = "Benvenuto in **Blueberry Travel**. Sono il tuo esperto di viaggi. Vuoi partire per il Giappone o scoprire l'Aurora Boreale?\n\n*Welcome! Ready to discover the world with us?*"
    st.session_state.messages.append({"role": "assistant", "content": welcome})

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Scrivi qui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = chat_ai(st.session_state.messages)
        st.markdown(response)

        db = load_viaggi()
        # Logica di matching migliorata: cerca per titolo, categoria o parole chiave
        matches = []
        p_lower = prompt.lower()
        r_lower = response.lower()
        
        for v in db:
            # Se il nome del tour o la categoria (es. Nord Europa) sono menzionati
            if v['t'].lower() in p_lower or v['cat'].lower() in p_lower or \
               v['t'].lower() in r_lower or v['cat'].lower() in r_lower:
                matches.append(v)
            # Supporto per parole chiave comuni (Giappone, Islanda, ecc.)
            elif "giappone" in p_lower and v['cat'] == "Giappotour":
                matches.append(v)
            elif ("lapponia" in p_lower or "islanda" in p_lower or "aurora" in p_lower) and v['cat'] == "Nord Europa":
                matches.append(v)

        if matches:
            st.markdown("### 🗺️ Tour Consigliati")
            # Rimuove duplicati e limita a 3
            unique_matches = {v['u']: v for v in matches}.values()
            cols = st.columns(len(list(unique_matches)[:3]))
            for i, v in enumerate(list(unique_matches)[:3]):
                with cols[i]:
                    wa_msg = f"Vorrei un preventivo per: {v['t']}"
                    wa_url = f"https://wa.me/{WA_NUMBER}?text={urllib.parse.quote(wa_msg)}"
                    st.markdown(f"""
                        <div class="travel-card">
                            <img src="{v['img']}" class="card-img">
                            <div style="padding:15px;">
                                <div style="color:{B_ORANGE}; font-weight:800; font-size:18px;">€ {v['p']}</div>
                                <div style="font-size:11px; color:#888;">{v['durata']}</div>
                                <div style="font-weight:600; margin:8px 0; height:35px; overflow:hidden; font-size:13px;">{v['t']}</div>
                                <a href="{wa_url}" target="_blank" class="btn-wa">WHATSAPP</a>
                                <a href="{v['u']}" target="_blank" class="btn-info">VEDI TOUR</a>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response})
