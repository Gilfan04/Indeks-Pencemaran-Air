import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Indeks Pencemaran Air (WQI)", layout="centered")
st.title("💧 Aplikasi Penentu Indeks Kualitas Air (WQI)")

st.markdown("""
Aplikasi ini menghitung *Water Quality Index (WQI)* berdasarkan parameter kimia:
- pH
- DO (Dissolved Oxygen)
- BOD
- COD
- TSS
- Nitrat (NO₃⁻)
- Fosfat (PO₄³⁻)
""")

# --- Input parameter air ---
with st.form("wqi_form"):
    st.subheader("🔢 Masukkan Nilai Parameter")
    pH = st.number_input("pH", min_value=0.0, max_value=14.0, value=7.0)
    do = st.number_input("DO (mg/L)", min_value=0.0, max_value=20.0, value=6.0)
    bod = st.number_input("BOD (mg/L)", min_value=0.0, value=2.0)
    cod = st.number_input("COD (mg/L)", min_value=0.0, value=10.0)
    tss = st.number_input("TSS (mg/L)", min_value=0.0, value=20.0)
    nitrat = st.number_input("Nitrat (mg/L)", min_value=0.0, value=3.0)
    fosfat = st.number_input("Fosfat (mg/L)", min_value=0.0, value=0.5)
    submitted = st.form_submit_button("Hitung WQI")

# --- Fungsi Skor (semakin tinggi, semakin buruk) ---
def normalize(val, ideal, max_val):
    """Normalisasi berdasarkan deviasi dari nilai ideal"""
    return max(0, 100 - abs(val - ideal) / (max_val - ideal) * 100)

def wqi_score():
    nilai = {
        "pH": normalize(pH, 7.0, 9.0),
        "DO": normalize(do, 7.0, 0.0),  # semakin kecil DO → makin buruk
        "BOD": normalize(bod, 1.0, 10.0),
        "COD": normalize(cod, 10.0, 80.0),
        "TSS": normalize(tss, 10.0, 200.0),
        "Nitrat": normalize(nitrat, 0.5, 10.0),
        "Fosfat": normalize(fosfat, 0.1, 5.0)
    }
    return nilai

def get_kategori(wqi):
    if wqi >= 80:
        return "Sangat Baik"
    elif wqi >= 65:
        return "Baik"
    elif wqi >= 45:
        return "Tercemar Ringan"
    elif wqi >= 25:
        return "Tercemar Sedang"
    else:
        return "Tercemar Berat"

# --- Output ---
if submitted:
    skor = wqi_score()
    df = pd.DataFrame(skor.items(), columns=["Parameter", "Skor (%)"])
    total_wqi = np.mean(list(skor.values()))
    kategori = get_kategori(total_wqi)

    st.subheader("📊 Hasil Perhitungan WQI")
    st.metric("Water Quality Index (WQI)", f"{total_wqi:.2f}")
    st.metric("Kategori Kualitas Air", kategori)
    st.dataframe(df.set_index("Parameter"), use_container_width=True)

    # Radar Chart
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=list(skor.values()),
        theta=list(skor.keys()),
        fill='toself',
        name='Skor Parameter'
    ))
    fig.update_layout(
      polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
      showlegend=False,
      title="Visualisasi Radar Skor Parameter"
    )
    st.plotly_chart(fig, use_container_width=True)
