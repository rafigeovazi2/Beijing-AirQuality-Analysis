import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ===========
# PAGE CONFIG
# ===========
st.set_page_config(
    page_title="Dashboard Kualitas Udara Beijing",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========
# CUSTOM CSS
# ==========
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6c757d;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 0.85rem;
        opacity: 0.85;
    }
    .stSelectbox > div > div {border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

# =========
# LOAD DATA
# =========
@st.cache_data
def load_data():
    """Load and prepare the main dataset."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "main_data.csv")
    df = pd.read_csv(csv_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Pastikan file `main_data.csv` ada di folder dashboard. Jalankan notebook terlebih dahulu.")
    st.stop()

# ===============
# SIDEBAR FILTERS
# ===============
st.sidebar.image("https://img.icons8.com/fluency/96/air-quality.png", width=80)
st.sidebar.title("🌫️ Filter Data")

# Date range
min_date = df['datetime'].min().date()
max_date = df['datetime'].max().date()
date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Station filter
all_stations = sorted(df['station'].unique().tolist())
selected_stations = st.sidebar.multiselect(
    "Pilih Stasiun",
    options=all_stations,
    default=all_stations
)

# Pollutant selector
pollutant = st.sidebar.selectbox(
    "Pilih Polutan",
    options=['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3'],
    index=0
)

# Apply filters
if len(date_range) == 2:
    mask = (
        (df['datetime'].dt.date >= date_range[0]) &
        (df['datetime'].dt.date <= date_range[1]) &
        (df['station'].isin(selected_stations))
    )
else:
    mask = df['station'].isin(selected_stations)

filtered_df = df[mask].copy()

if filtered_df.empty:
    st.warning("⚠️ Tidak ada data yang sesuai dengan filter. Silakan ubah filter di sidebar.")
    st.stop()

# ============
# MAIN CONTENT
# ============
st.markdown(
    '<p style="color: #2E86C1; font-size: 24px; font-weight: bold; text-align: center; margin: 0">🍃 DASHBOARD KUALITAS UDARA DI BEIJING</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Analisis Data Polusi Udara dari 12 Stasiun Pemantauan (2013-2017)</p>', unsafe_allow_html=True)

# --- Metric Cards ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_pm25 = filtered_df['PM2.5'].mean()
    st.metric("Rata-rata PM2.5", f"{avg_pm25:.1f} µg/m³")

with col2:
    avg_pm10 = filtered_df['PM10'].mean()
    st.metric("Rata-rata PM10", f"{avg_pm10:.1f} µg/m³")

with col3:
    avg_temp = filtered_df['TEMP'].mean()
    st.metric("Rata-rata Suhu", f"{avg_temp:.1f} °C")

with col4:
    n_records = len(filtered_df)
    st.metric("Jumlah Record", f"{n_records:,}")

st.divider()

# ==========
# TAB LAYOUT
# ==========
tab1, tab2, tab3 = st.tabs([
    "📈 Tren PM2.5 Bulanan",
    "📊 Perbandingan Stasiun",
    "🔬 Clustering Stasiun"
])

# - TAB 1: Tren PM2.5 Bulanan -
with tab1:
    st.subheader("Pertanyaan 1: Bagaimana tren konsentrasi PM2.5 bulanan?")

    # Monthly trend
    monthly_data = filtered_df.set_index('datetime').resample('ME')[pollutant].mean()

    fig1, ax1 = plt.subplots(figsize=(14, 5))
    ax1.plot(monthly_data.index, monthly_data.values, color='#e74c3c', linewidth=2, alpha=0.85)
    ax1.fill_between(monthly_data.index, monthly_data.values, alpha=0.15, color='#e74c3c')
    overall_mean = monthly_data.mean()
    ax1.axhline(y=overall_mean, color='#2c3e50', linestyle='--', alpha=0.6,
                label=f'Rata-rata: {overall_mean:.1f}')
    if pollutant == 'PM2.5':
        ax1.axhline(y=75, color='#27ae60', linestyle=':', alpha=0.6, label='Standar Nasional (75)')
    ax1.set_title(f'Tren {pollutant} Bulanan', fontsize=14, fontweight='bold')
    ax1.set_ylabel(f'{pollutant} (µg/m³)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig1)

    # Calendar month average
    st.subheader(f"Rata-rata {pollutant} per Bulan Kalender")
    month_names = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des']
    monthly_cal = filtered_df.groupby('month')[pollutant].mean().reindex(range(1, 13), fill_value=0)

    fig2, ax2 = plt.subplots(figsize=(12, 5))
    threshold = 75 if pollutant == 'PM2.5' else monthly_cal.mean()
    colors = ['#e74c3c' if v > threshold else '#3498db' for v in monthly_cal.values]
    bars = ax2.bar(month_names, monthly_cal.values, color=colors, edgecolor='white', linewidth=0.5)
    for bar, val in zip(bars, monthly_cal.values):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                 f'{val:.0f}', ha='center', va='bottom', fontsize=9)
    ax2.set_title(f'Rata-rata {pollutant} per Bulan Kalender', fontsize=14, fontweight='bold')
    ax2.set_ylabel(f'{pollutant} (µg/m³)')
    ax2.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    st.pyplot(fig2)

    with st.expander("📝 Insight"):
        st.markdown("""
        - PM2.5 menunjukkan **pola musiman yang jelas**: tinggi di musim dingin (Des-Feb) dan rendah di musim panas (Jun-Agu).
        - **Januari dan Desember** konsisten menjadi bulan dengan polusi tertinggi, dipengaruhi oleh penggunaan pemanas berbahan bakar fosil dan kondisi meteorologi (inversi suhu).
        - Tren tahunan menunjukkan sedikit perbaikan dari 2013 ke 2017.
        """)

# - TAB 2: Perbandingan Stasiun -
with tab2:
    st.subheader("Pertanyaan 2: Stasiun mana dengan PM2.5 tertinggi dan terendah?")

    station_stats = filtered_df.groupby('station')[pollutant].agg(['mean','median','std']).round(1)
    station_stats = station_stats.sort_values('mean', ascending=True)

    col_a, col_b = st.columns(2)

    with col_a:
        fig3, ax3 = plt.subplots(figsize=(8, 7))
        colors_bar = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(station_stats)))[::-1]
        bars3 = ax3.barh(station_stats.index, station_stats['mean'].values, color=colors_bar, edgecolor='white')
        ax3.axvline(x=station_stats['mean'].mean(), color='#e74c3c', linestyle='--', alpha=0.7,
                    label=f'Mean: {station_stats["mean"].mean():.1f}')
        for bar, val in zip(bars3, station_stats['mean'].values):
            ax3.text(val + 0.3, bar.get_y() + bar.get_height()/2., f'{val:.1f}',
                     ha='left', va='center', fontsize=9)
        ax3.set_xlabel(f'Rata-rata {pollutant} (µg/m³)')
        ax3.set_title(f'Rata-rata {pollutant} per Stasiun', fontsize=13, fontweight='bold')
        ax3.legend()
        plt.tight_layout()
        st.pyplot(fig3)

    with col_b:
        fig4, ax4 = plt.subplots(figsize=(8, 7))
        order = filtered_df.groupby('station')[pollutant].mean().sort_values(ascending=False).index
        sns.boxplot(data=filtered_df, y='station', x=pollutant, order=order, ax=ax4,
                    hue='station', palette='RdYlGn', legend=False, showfliers=False)
        ax4.set_xlabel(f'{pollutant} (µg/m³)')
        ax4.set_ylabel('')
        ax4.set_title(f'Distribusi {pollutant} per Stasiun', fontsize=13, fontweight='bold')
        if pollutant in ['PM2.5', 'PM10']:
            ax4.set_xlim(0, 400)
        plt.tight_layout()
        st.pyplot(fig4)

    # Table
    st.subheader("📋 Tabel Statistik per Stasiun")
    display_stats = station_stats.sort_values('mean', ascending=False).reset_index()
    display_stats.columns = ['Stasiun', 'Mean', 'Median', 'Std Dev']
    st.dataframe(display_stats, use_container_width=True, hide_index=True)

    with st.expander("📝 Insight"):
        if len(station_stats) > 0:
            best = station_stats.index[0]
            worst = station_stats.index[-1]
            st.markdown(f"""
            - Stasiun dengan {pollutant} **terendah**: **{best}** ({station_stats.loc[best, 'mean']:.1f} µg/m³)
            - Stasiun dengan {pollutant} **tertinggi**: **{worst}** ({station_stats.loc[worst, 'mean']:.1f} µg/m³)
            - Stasiun di area urban cenderung memiliki polusi lebih tinggi dibanding area suburban.
            """)
        else:
            st.info("Pilih minimal 1 stasiun untuk melihat insight.")

# - TAB 3: Clustering -
with tab3:
    st.subheader("Analisis Lanjutan: Clustering Stasiun (Binning)")

    station_poll = filtered_df.groupby('station')[['PM2.5','PM10','SO2','NO2']].mean().round(2)

    bins = [0, 60, 80, 100, float('inf')]
    labels_cat = ['Baik (<60)', 'Sedang (60-80)', 'Buruk (80-100)', 'Sangat Buruk (>100)']
    station_poll['Kategori'] = pd.cut(station_poll['PM2.5'], bins=bins, labels=labels_cat)

    col_x, col_y = st.columns(2)

    with col_x:
        # Heatmap
        fig5, ax5 = plt.subplots(figsize=(8, 7))
        hm_data = station_poll[['PM2.5','PM10','SO2','NO2']].sort_values('PM2.5', ascending=False)
        sns.heatmap(hm_data, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax5, linewidths=0.5)
        ax5.set_title('Heatmap Rata-rata Polutan per Stasiun', fontsize=13, fontweight='bold')
        ax5.set_ylabel('')
        plt.tight_layout()
        st.pyplot(fig5)

    with col_y:
        # Scatter clustering
        fig6, ax6 = plt.subplots(figsize=(8, 7))
        cmap = {'Baik (<60)':'#27ae60', 'Sedang (60-80)':'#f39c12',
                'Buruk (80-100)':'#e67e22', 'Sangat Buruk (>100)':'#e74c3c'}
        for cat in labels_cat:
            sub = station_poll[station_poll['Kategori'] == cat]
            if len(sub) > 0:
                ax6.scatter(sub['PM2.5'], sub['NO2'], c=cmap[cat], s=150, label=cat,
                           edgecolors='white', linewidth=1.5, zorder=5)
                for idx, row in sub.iterrows():
                    ax6.annotate(idx, (row['PM2.5'], row['NO2']),
                               textcoords='offset points', xytext=(5,5), fontsize=8)
        ax6.set_xlabel('Rata-rata PM2.5 (µg/m³)')
        ax6.set_ylabel('Rata-rata NO2 (µg/m³)')
        ax6.set_title('Clustering: PM2.5 vs NO2', fontsize=13, fontweight='bold')
        ax6.legend(title='Kategori', fontsize=9)
        ax6.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig6)

    # Clustering table
    st.subheader("📋 Hasil Pengelompokan Stasiun")
    cluster_display = station_poll.sort_values('PM2.5', ascending=False).reset_index()
    cluster_display.columns = ['Stasiun', 'PM2.5', 'PM10', 'SO2', 'NO2', 'Kategori']
    st.dataframe(cluster_display, use_container_width=True, hide_index=True)

    with st.expander("📝 Insight"):
        st.markdown("""
        - Clustering menggunakan **binning** pada rata-rata PM2.5 berhasil mengelompokkan stasiun ke dalam kategori kualitas udara.
        - Terdapat korelasi positif antara PM2.5 dan NO2, menunjukkan sumber polusi yang serupa (emisi kendaraan bermotor).
        - Stasiun di area urban padat masuk kategori "Buruk" hingga "Sangat Buruk".
        """)

# ======
# FOOTER
# ======
st.divider()
st.markdown("""
<div style="text-align:center; color:#6c757d; font-size:0.85rem;">
    <p>Dashboard Kualitas Udara Beijing | Data: PRSA Dataset (2013-2017) | By Rafi Geovazi</p>
</div>
""", unsafe_allow_html=True)
