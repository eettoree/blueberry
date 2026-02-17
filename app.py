import streamlit as st
import json
import time
import urllib.parse
import pandas as pd
from groq import Groq

# --- CONFIGURAZIONE BRAND BLUEBERRY ---
if "GROQ_API_KEY" in st.secrets:
    GROQ_KEY = st.secrets["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"]
else:
    GROQ_KEY = "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"

WA_NUMBER = "393488231234" 
B_BLUE = "#004085"
B_ORANGE = "#FF6B35"
B_DARK = "#050A14"

st.set_page_config(page_title="Blueberry Travel AI Expert", page_icon="🗾", layout="centered")

def apply_blueberry_ui():
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {B_DARK}; color: #F0F2F6; font-family: 'Inter', sans-serif; }}
        [data-testid="stHeader"], [data-testid="stToolbar"] {{ display: none; }}
        .stChatMessage {{ border-radius: 20px; padding: 1.5rem; margin-bottom: 1rem; border: 1px solid rgba(255,255,255,0.1) !important; }}
        .stChatMessage[data-testid="stChatMessageAssistant"] {{ background-color: #0B1426 !important; border-left: 4px solid {B_ORANGE} !important; }}
        
        /* Travel Cards */
        .travel-card {{ background: #111B2D; border-radius: 18px; overflow: hidden; border: 1px solid rgba(255,107,53,0.2); margin-bottom: 20px; }}
        .card-img {{ width: 100%; height: 180px; object-fit: cover; }}
        .card-body {{ padding: 20px; }}
        .card-price {{ color: {B_ORANGE}; font-size: 22px; font-weight: 800; }}
        
        /* Comparison Table */
        .comp-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: #111B2D; border-radius: 10px; overflow: hidden; font-size: 14px; }}
        .comp-table th {{ background: {B_BLUE}; color: white; padding: 12px; text-align: left; }}
        .comp-table td {{ padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        
        /* Buttons */
        .btn-wa {{ display: block; text-align: center; background: #25D366; color: white !important; text-decoration: none; padding: 12px; border-radius: 10px; font-weight: bold; margin-top: 10px; }}
        .btn-info {{ display: block; text-align: center; background: transparent; border: 1px solid {B_ORANGE}; color: {B_ORANGE} !important; text-decoration: none; padding: 10px; border-radius: 10px; margin-top: 5px; font-size: 13px; }}
        </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_viaggi():
    try:
        with open('viaggi_full.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def mostra_comparazione(tour_list):
    if len(tour_list) < 2: return
    st.markdown("### 📊 Confronto Itinerari")
    data = {
        "Caratteristica": ["Prezzo Base", "Durata", "Categoria", "Link"],
        **{t['t']: [f"€ {t['p']}", t['durata'], t['cat'], f"[Dettagli]({t['u']})"] for t in tour_list}
    }
    df = pd.DataFrame(data)
    st.table(df)

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
    except Exception:
        return "Servizio momentaneamente non disponibile. Contatta l'assistenza Blueberry Travel."

apply_blueberry_ui()

# Session State Init
if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome = """Ciao! Sono l'esperto di **Blueberry Travel**. 🗾
    
Posso aiutarti a scegliere il tuo **Giappotour** o un viaggio in qualsiasi parte del mondo. Se hai dubbi tra due tour, chiedimi pure un confronto!"""
    st.session_state.messages.append({"role": "assistant", "content": welcome})

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Confronta Giappo-Easy e Gran Tour..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("🔍 *Elaborazione confronto e itinerari...*")
        
        response = chat_ai(st.session_state.messages)
        placeholder.markdown(response)

        db = load_viaggi()
        # Logica di matching per trovare i tour menzionati
        matches = [v for v in db if v['t'].lower() in prompt.lower() or any(word in prompt.lower() for word in v['t'].lower().split() if len(word) > 4)]
        
        # Se l'utente chiede un confronto o menziona più tour
        if len(matches) >= 2:
            mostra_comparazione(matches[:3])
        
        # Mostra comunque le Cards singole
        if matches:
            st.markdown("### 🗺️ Tour Selezionati")
            cols = st.columns(len(matches[:3]))
            for i, v in enumerate(matches[:3]):
                with cols[i]:
                    wa_msg = f"Ciao, vorrei un preventivo per: {v['t']}"
                    wa_url = f"https://wa.me/{WA_NUMBER}?text={urllib.parse.quote(wa_msg)}"
                    st.markdown(f"""
                        <div class="travel-card">
                            <img src="{v['img']}" class="card-img">
                            <div class="card-body">
                                <div class="card-price">€ {v['p']}</div>
                                <div style="font-size:12px; color:#888;">{v['durata']}</div>
                                <div style="font-weight:700; margin:10px 0; height:40px; overflow:hidden;">{v['t']}</div>
                                <a href="{wa_url}" target="_blank" class="btn-wa">PREVENTIVO</a>
                                <a href="{v['u']}" target="_blank" class="btn-info">VEDI TOUR</a>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response})