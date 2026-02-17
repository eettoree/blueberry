import streamlit as st
import json
import time
import urllib.parse
import pandas as pd
from groq import Groq

# --- CONFIGURAZIONE SICUREZZA API ---
# Accediamo alla chiave usando il nome della variabile impostata nei Secrets di Streamlit
if "GROQ_API_KEY" in st.secrets:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
else:
    # Fallback per test locale (se non usi i secrets locali)
    GROQ_KEY = "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"

# --- CONFIGURAZIONE BRAND BLUEBERRY ---
WA_NUMBER = "393488231234" 
B_BLUE = "#004085"
B_ORANGE = "#FF6B35"
B_DARK = "#050A14"

st.set_page_config(
    page_title="Blueberry Travel AI Expert", 
    page_icon="🗾", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- UI CUSTOM (GEMINI PRO STYLE - BLUEBERRY EDITION) ---
def apply_blueberry_ui():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
        
        .stApp {{ background-color: {B_DARK}; color: #F0F2F6; font-family: 'Inter', sans-serif; }}
        [data-testid="stHeader"], [data-testid="stToolbar"] {{ display: none; }}
        
        /* Chat Bubbles */
        .stChatMessage {{ 
            border-radius: 24px; 
            padding: 1.5rem; 
            margin-bottom: 1rem; 
            border: 1px solid rgba(255,255,255,0.08) !important;
            background-color: transparent !important;
        }}
        .stChatMessage[data-testid="stChatMessageAssistant"] {{ 
            background-color: #0B1426 !important; 
            border-left: 4px solid {B_ORANGE} !important; 
        }}

        /* Skeleton Animation */
        @keyframes shimmer {{ 0% {{ opacity: 0.3; }} 50% {{ opacity: 0.6; }} 100% {{ opacity: 0.3; }} }}
        .skeleton {{ height: 16px; background: #1E232B; border-radius: 8px; margin: 12px 0; animation: shimmer 2s infinite; }}

        /* Travel Cards */
        .travel-card {{ 
            background: #111B2D; 
            border: 1px solid rgba(255,107,53,0.15); 
            border-radius: 22px; 
            overflow: hidden; 
            margin-bottom: 20px;
            transition: 0.4s ease;
        }}
        .travel-card:hover {{ border-color: {B_ORANGE}; transform: translateY(-5px); }}
        .card-img {{ width: 100%; height: 190px; object-fit: cover; }}
        .card-body {{ padding: 22px; }}
        .card-price {{ color: {B_ORANGE}; font-size: 24px; font-weight: 800; }}
        .card-meta {{ color: #888; font-size: 11px; text-transform: uppercase; letter-spacing: 1.2px; }}
        
        /* Buttons */
        .btn-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 18px; }}
        .btn-wa {{ text-align: center; background: #25D366; color: white !important; text-decoration: none; padding: 12px; border-radius: 14px; font-size: 12px; font-weight: bold; display: flex; align-items: center; justify-content: center; gap: 6px; }}
        .btn-info {{ text-align: center; background: transparent; border: 1px solid {B_ORANGE}; color: {B_ORANGE} !important; text-decoration: none; padding: 12px; border-radius: 14px; font-size: 12px; font-weight: 600; }}
        
        /* Table Style */
        .stTable {{ background-color: #111B2D; border-radius: 15px; overflow: hidden; }}
        </style>
    """, unsafe_allow_html=True)

# --- LOGICA DATI ---
@st.cache_data
def load_viaggi():
    try:
        with open('viaggi_full.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def mostra_comparazione(tour_list):
    if len(tour_list) < 2: return
    st.markdown("### 📊 Confronto Analitico Itinerari")
    data = {
        "Dettaglio": ["Prezzo Base", "Durata", "Categoria"],
        **{t['t']: [f"€ {t['p']}", t['durata'], t['cat']] for t in tour_list}
    }
    df = pd.DataFrame(data)
    st.table(df)

# --- LOGICA AI ---
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
        return "Spiacente, il servizio di assistenza digitale è momentaneamente non disponibile. Contatta info@blueberrytravel.it."

# --- ESECUZIONE APP ---
apply_blueberry_ui()

if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome_text = (
        "Ciao! Sono l'esperto di viaggi di **Blueberry Travel**. 🗾\n\n"
        "Posso aiutarti a scegliere il tuo **Giappotour** ideale o un viaggio in tutto il mondo. "
        "Sei pronto a partire?\n\n"
        "*Hello! I am your **Blueberry Travel** expert. Ready to discover your next adventure?*"
    )
    st.session_state.messages.append({"role": "assistant", "content": welcome_text})

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Scrivi qui le tue domande sul Giappone..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown('<div class="skeleton"></div><div class="skeleton" style="width:70%"></div>', unsafe_allow_html=True)
        
        response = chat_ai(st.session_state.messages)
        placeholder.empty()

        # Typing Effect
        full_typed = ""
        type_area = st.empty()
        for word in response.split():
            full_typed += word + " "
            type_area.markdown(full_typed + "▌")
            time.sleep(0.02)
        type_area.markdown(response)

        # Analisi del Database per Cards e Comparazione
        db = load_viaggi()
        # Cerchiamo i tour menzionati nel prompt o nella risposta
        matches = [v for v in db if v['t'].lower() in prompt.lower() or v['t'].lower() in response.lower()]
        
        # Se non trova match esatti, prova con parole chiave significative
        if not matches:
            keywords = [w for w in prompt.lower().split() if len(w) > 4]
            matches = [v for v in db if any(k in v['t'].lower() for k in keywords)]

        # Funzione di Comparazione (se più di un tour trovato)
        if len(matches) >= 2:
            mostra_comparazione(matches[:3])

        # Visualizzazione Cards
        if matches:
            st.markdown("### 🗺️ Itinerari Selezionati")
            cols = st.columns(len(matches[:3]))
            for i, v in enumerate(matches[:3]):
                with cols[i]:
                    wa_msg = f"Vorrei un preventivo per il tour: {v['t']} ({v['u']})"
                    wa_url = f"https://wa.me/{WA_NUMBER}?text={urllib.parse.quote(wa_msg)}"
                    st.markdown(f"""
                        <div class="travel-card">
                            <img src="{v['img']}" class="card-img">
                            <div class="card-body">
                                <div class="card-price">€ {v['p']}</div>
                                <div class="card-meta">{v['durata']} | {v['cat']}</div>
                                <div style="font-weight:600; margin:12px 0; height:45px; overflow:hidden; font-size:14px; color:white;">{v['t']}</div>
                                <div class="btn-grid">
                                    <a href="{wa_url}" target="_blank" class="btn-wa">WHATSAPP</a>
                                    <a href="{v['u']}" target="_blank" class="btn-info">DETTAGLI</a>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response})
