import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Konfigurasi halaman
st.set_page_config(
    page_title="Water Pollution Index (WPI) Calculator",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fungsi menghitung indeks pencemaran
def calculate_wpi(params):
    """Menghitung Water Pollution Index berdasarkan parameter input"""
    # Bobot parameter (sesuai Kepmen LH No. 115/2003)
    weights = {
        'TDS': 0.17,
        'pH': 0.11,
        'DO': 0.17,
        'BOD': 0.22,
        'COD': 0.19,
        'Nitrat': 0.14
    }
    
    # Normalisasi parameter
    normalized = {}
    normalized['TDS'] = min(max((params['TDS'] - 400)/(1000 - 400), 0), 1)
    normalized['pH'] = min(max(abs(params['pH'] - 7)/2.5, 0), 1)
    normalized['DO'] = 1 - min(max(params['DO']/8, 0), 1)
    normalized['BOD'] = min(max((params['BOD'] - 3)/(12 - 3), 0), 1)
    normalized['COD'] = min(max((params['COD'] - 10)/(40 - 10), 0), 1)
    normalized['Nitrat'] = min(max((params['Nitrat'] - 5)/(20 - 5), 0), 1)
    
    # Hitung WPI
    wpi = sum(weights[p] * normalized[p] for p in weights)
    return wpi, weights, normalized

# Klasifikasi WPI
def classify_wpi(wpi):
    """Mengklasifikasikan status pencemaran berdasarkan WPI"""
    if wpi < 0.25:
        return "Sangat baik", "#2ECC71"
    elif 0.25 <= wpi < 0.5:
        return "Baik", "#3498DB"
    elif 0.5 <= wpi < 0.75:
        return "Cemar ringan", "#F1C40F"
    else:
        return "Cemar berat", "#E74C3C"

# UI Aplikasi
st.title("💧 Kalkulator Indeks Pencemaran Air (WPI)")
st.markdown("""
Aplikasi ini menghitung **Indeks Pencemaran Air** berdasarkan parameter kualitas air sesuai 
**Keputusan Menteri Lingkungan Hidup No. 115 Tahun 2003** tentang Pedoman Penentuan Status Mutu Air
""")

# Sidebar input parameter
with st.sidebar:
    st.header("📋 Parameter Input")
    st.subheader("Parameter Fisika-Kimia")
    
    tds = st.slider("Total Padatan Terlarut (TDS) [mg/L]", 0, 2000, 500)
    ph = st.slider("pH", 0.0, 14.0, 7.0, 0.1)
    do = st.slider("Oksigen Terlarut (DO) [mg/L]", 0.0, 15.0, 6.0, 0.1)
    
    st.subheader("Parameter Organik")
    bod = st.slider("Biochemical Oxygen Demand (BOD) [mg/L]", 0.0, 50.0, 5.0, 0.1)
    cod = st.slider("Chemical Oxygen Demand (COD) [mg/L]", 0.0, 100.0, 15.0, 0.1)
    
    st.subheader("Parameter Nutrien")
    nitrate = st.slider("Nitrat (NO3-) [mg/L]", 0.0, 50.0, 10.0, 0.1)

# Membuat dictionary parameter
water_params = {
    'TDS': tds,
    'pH': ph,
    'DO': do,
    'BOD': bod,
    'COD': cod,
    'Nitrat': nitrate
}

# Perhitungan saat tombol ditekan
if st.button("🔄 Hitung Indeks Pencemaran Air"):
    with st.spinner("Menghitung WPI..."):
        wpi, weights, normalized = calculate_wpi(water_params)
        status, color = classify_wpi(wpi)
        
        # Tampilkan hasil utama
        cols = st.columns([1, 2])
        
        with cols[0]:
            st.metric("Indeks Pencemaran Air (WPI)", f"{wpi:.3f}")
            
            # Display status dengan warna
            st.markdown(f"""
            <div style='border-radius: 10px; padding: 15px; background-color: {color}; color: white; text-align: center'>
                <h3>Status: {status}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[1]:
            # Grafik radar parameter
            categories = list(weights.keys())
            values = [normalized[p] for p in categories]
            weights_values = [weights[p] for p in categories]
            
            angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
            values += values[:1]
            weights_values += weights_values[:1]
            angles += angles[:1]
            
            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
            ax.fill(angles, values, 'r', alpha=0.25, label='Normalized Value')
            ax.plot(angles, weights_values, 'g', label='Bobot Parameter')
            ax.set_yticklabels([])
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            ax.legend(loc='upper right')
            st.pyplot(fig)
        
        # Tabel detail parameter
        st.subheader("📊 Detail Parameter")
        
        param_data = {
            "Parameter": list(water_params.keys()),
            "Nilai": list(water_params.values()),
            "Satuan": ["mg/L", "-", "mg/L", "mg/L", "mg/L", "mg/L"],
            "Nilai Normalisasi": [f"{normalized[p]:.3f}" for p in water_params],
            "Bobot Parameter": [weights[p] for p in water_params]
        }
        
        st.dataframe(pd.DataFrame(param_data), use_container_width=True, hide_index=True)
        
        # Interpretasi hasil
        st.subheader("📝 Interpretasi Hasil")
        if wpi < 0.25:
            st.success("""
            **Kualitas Air Sangat Baik**: 
            - Memenuhi semua baku mutu air 
            - Aman untuk semua keperluan (air minum, perikanan, pertanian)
            - Tingkat polusi sangat rendah
            """)
        elif 0.25 <= wpi < 0.5:
            st.info("""
            **Kualitas Air Baik**: 
            - Masih memenuhi baku mutu untuk sebagian besar parameter 
            - Aman untuk keperluan tertentu dengan pengolahan minimal
            - Tingkat polusi rendah
            """)
        elif 0.5 <= wpi < 0.75:
            st.warning("""
            **Pencemaran Ringan**:
            - Beberapa parameter melebihi baku mutu
            - Membutuhkan pengolahan sebelum digunakan
            - Tidak disarankan untuk air minum langsung
            - Ancaman ekologis tingkat sedang
            """)
        else:
            st.error("""
            **Pencemaran Berat**:
            - Mayoritas parameter melebihi baku mutu
            - Berbahaya untuk kesehatan manusia dan ekosistem
            - Membutuhkan pengolahan intensif sebelum penggunaan
            - Ancaman ekologis serius
            """)

# Informasi standar baku mutu
with st.expander("📚 Baku Mutu Air Bersih (Kepmen LH No. 115/2003)"):
    st.table(pd.DataFrame({
        "Parameter": ["TDS", "pH", "DO", "BOD", "COD", "Nitrat"],
        "Satuan": ["mg/L", "-", "mg/L", "mg/L", "mg/L", "mg/L"],
        "Kelas I (Air Minum)": [500, "6-9", "6", "2", "10", "10"],
        "Kelas II (Pertanian)": [1000, "6-9", "4", "6", "25", "20"],
        "Kelas III (Perikanan)": [1000, "6-9", "4", "3", "20", "10"],
    }))

# Tampilkan informasi tambahan
st.sidebar.markdown("---")
st.sidebar.info("""
**Catatan**:
- Perhitungan berdasarkan metode **Water Pollution Index (WPI)**
- Bobot parameter mengacu pada studi:
  - Sutrisno (2019) - Analisis Kualitas Air
  - Kepmen LH No. 115 Tahun 2003
""")
