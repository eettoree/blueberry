import streamlit as st
import json
import time
import urllib.parse
import pandas as pd
from groq import Groq

# --- CONFIGURAZIONE SICUREZZA API ---
# Su Streamlit Cloud devi impostare GROQ_API_KEY nei Secrets
if "GROQ_API_KEY" in st.secrets:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
else:
    GROQ_KEY = "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"

# --- CONFIGURAZIONE BRAND BLUEBERRY ---
WA_NUMBER = "393488231234" 
B_ORANGE = "#FF6B35"
B_DARK = "#050A14"

st.set_page_config(page_title="Blueberry Travel AI Expert", page_icon="🗾", layout="centered")

def apply_blueberry_ui():
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {B_DARK}; color: #F0F2F6; font-family: 'Inter', sans-serif; }}
        .stChatMessage {{ border-radius: 24px; padding: 1.5rem; margin-bottom: 1rem; border: 1px solid rgba(255,255,255,0.08) !important; }}
        .stChatMessage[data-testid="stChatMessageAssistant"] {{ background-color: #0B1426 !important; border-left: 4px solid {B_ORANGE} !important; }}
        .skeleton {{ height: 16px; background: #1E232B; border-radius: 8px; margin: 12px 0; animation: shimmer 2s infinite; }}
        @keyframes shimmer {{ 0% {{ opacity: 0.3; }} 50% {{ opacity: 0.6; }} 100% {{ opacity: 0.3; }} }}
        .travel-card {{ background: #111B2D; border: 1px solid rgba(255,107,53,0.15); border-radius: 22px; overflow: hidden; margin-bottom: 20px; }}
        .card-img {{ width: 100%; height: 190px; object-fit: cover; }}
        .btn-wa {{ text-align: center; background: #25D366; color: white !important; text-decoration: none; padding: 12px; border-radius: 14px; display: block; font-weight: bold; }}
        </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_viaggi():
    try:
        # Nota: nello screenshot il tuo file si chiama immobili_full.json
        # Per Blueberry deve chiamarsi viaggi_full.json o devi cambiare questo nome qui sotto
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
        # QUESTA RIGA TI DIRÀ L'ERRORE REALE NELLA CHAT
        return f"ERRORE TECNICO: {str(e)}"

apply_blueberry_ui()

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Ciao! Sono l'esperto di **Blueberry Travel**. Come posso aiutarti oggi?"})

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Scrivi qui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown('<div class="skeleton"></div>', unsafe_allow_html=True)
        response = chat_ai(st.session_state.messages)
        placeholder.markdown(response)

        db = load_viaggi()
        matches = [v for v in db if v['t'].lower() in prompt.lower() or v['t'].lower() in response.lower()]
        if matches:
            cols = st.columns(len(matches[:3]))
            for i, v in enumerate(matches[:3]):
                with cols[i]:
                    st.markdown(f"""
                        <div class="travel-card">
                            <img src="{v['img']}" class="card-img">
                            <div style="padding:15px;">
                                <div style="color:{B_ORANGE}; font-weight:800;">€ {v['p']}</div>
                                <div style="font-size:13px; margin:10px 0;">{v['t']}</div>
                                <a href="https://wa.me/{WA_NUMBER}" class="btn-wa">WHATSAPP</a>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response})
