#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import yfinance as yf
import pandas as pd

# ========== Barèmes ==========
POINTS = {0: 0.6, 1: 1.3, 2: 1.9, 3: 2.5}
CATEGORIES = {0: "Chocolate", 1: "Bronze", 2: "Silver", 3: "Gold"}

def score_ebitda(x):
    if x < 10: return 0
    elif x < 20: return 1
    elif x < 35: return 2
    else: return 3

def score_margin(x):
    if x < 8: return 0
    elif x < 15: return 1
    elif x < 25: return 2
    else: return 3

def score_de_ratio(x):
    if x > 1: return 0
    elif x > 0.5: return 1
    elif x > 0.25: return 2
    else: return 3

def score_current(x):
    if x < 1.2: return 0
    elif x < 1.5: return 1
    elif x < 3: return 2
    else: return 3

def score_quick(x):
    if x < 1: return 0
    elif x < 1.5: return 1
    elif x < 3: return 2
    else: return 3

def score_roa(x):
    if x < 5: return 0
    elif x < 8: return 1
    elif x < 12: return 2
    else: return 3

def score_roe(x):
    if x < 10: return 0
    elif x < 15: return 1
    elif x < 25: return 2
    else: return 3

def score_analyst(x):
    if x > 3.5: return 0
    elif x > 2.5: return 1
    elif x > 1.5: return 2
    else: return 3

def safe_extract(info, key, default=None):
    return info.get(key, default)

def analyze_ticker(ticker):
    info = yf.Ticker(ticker).info
    d = {
        "EBITDA": safe_extract(info, "ebitdaMargins", 0)*100,
        "Marge nette": safe_extract(info, "profitMargins", 0)*100,
        "D/E ratio": safe_extract(info, "debtToEquity", 0)/100,
        "Current ratio": safe_extract(info, "currentRatio", 0),
        "Quick ratio": safe_extract(info, "quickRatio", 0),
        "ROA": safe_extract(info, "returnOnAssets", 0)*100,
        "ROE": safe_extract(info, "returnOnEquity", 0)*100,
        "Analystes": safe_extract(info, "recommendationMean", 3),
    }
    if d["D/E ratio"] == 0:
        d["D/E ratio"] = safe_extract(info, "debtToEquity", 0)
    scores = [
        score_ebitda(d["EBITDA"]),
        score_margin(d["Marge nette"]),
        score_de_ratio(d["D/E ratio"]),
        score_current(d["Current ratio"]),
        score_quick(d["Quick ratio"]),
        score_roa(d["ROA"]),
        score_roe(d["ROE"]),
        score_analyst(d["Analystes"])
    ]
    labels = ["EBITDA", "Marge nette", "D/E ratio", "Current ratio", "Quick ratio", "ROA", "ROE", "Analystes"]
    points = [POINTS[s] for s in scores]
    cats = [CATEGORIES[s] for s in scores]
    note = sum(points)
    df_detail = pd.DataFrame({
        "Critère": labels,
        "Valeur": [d[k] for k in labels],
        "Score": cats,
        "Points": points,
    })
    return df_detail, note

def get_note_only(ticker):
    try:
        _, note = analyze_ticker(ticker)
        return note
    except Exception:
        return None

# ========== FRONTEND STREAMLIT ==========

st.set_page_config(layout="wide")
st.title("📊 Classement de tickers US (scoring auto)")
st.caption("Ajoutez vos tickers manuellement, comparez-les et classez-les automatiquement selon leur note.")

# Gérer la session Streamlit pour stocker la liste des tickers
if "tickers" not in st.session_state:
    st.session_state["tickers"] = []

with st.form(key="add_ticker_form"):
    ticker = st.text_input("Entrez un ticker US (ex: AAPL)").upper()
    col1, col2 = st.columns([1,1])
    with col1:
        add_btn = st.form_submit_button("Ajouter")
    with col2:
        clear_btn = st.form_submit_button("Clear")

if add_btn and ticker and ticker not in st.session_state["tickers"]:
    st.session_state["tickers"].append(ticker)
if clear_btn:
    st.session_state["tickers"] = []

if st.session_state["tickers"]:
    notes_data = []
    for t in st.session_state["tickers"]:
        note = get_note_only(t)
        if note is not None:
            notes_data.append({"Entreprise": t, "Note sur 20": round(note, 2)})
        else:
            notes_data.append({"Entreprise": t, "Note sur 20": "Erreur données"})
    # Classement du meilleur au moins bon
    df_notes = pd.DataFrame(notes_data)
    df_notes = df_notes.sort_values(by="Note sur 20", ascending=False)
    st.markdown("### Classement des entreprises")
    st.dataframe(df_notes, use_container_width=True)

    st.caption("Vous pouvez cliquer sur Clear pour effacer la liste.")

    # Détail pour le dernier ticker ajouté (optionnel)
    dernier = st.session_state["tickers"][-1]
    try:
        df_detail, note_principal = analyze_ticker(dernier)
        st.markdown(f"#### Détail des scores pour : {dernier}")
        st.dataframe(df_detail, use_container_width=True)
    except Exception:
        st.warning("Impossible de récupérer les données détaillées.")

else:
    st.info("Ajoutez un ou plusieurs tickers pour commencer la comparaison.")


