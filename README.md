# Proyek Analisis Data: Beijing Air Quality Analysis By Rafi Geovazi 🍃

## Deskripsi

Proyek analisis data kualitas udara di Beijing menggunakan dataset PRSA dari 12 stasiun pemantauan (Maret 2013 - Februari 2017). Proyek ini mencakup Data Wrangling, EDA, Visualisasi, Analisis Lanjutan (Clustering), serta Conclusion & Recommendation.

## Struktur Direktori

```
AirQuality/
├── dashboard/
│   ├── dashboard.py        # Streamlit dashboard
│   └── main_data.csv       # Data bersih untuk dashboard
├── data/
│   └── *.csv               # 12 file data stasiun pemantauan
├── notebook.ipynb           # Notebook analisis data
├── requirements.txt         # Dependencies
├── url.txt                  # URL deployment
└── README.md
```

## Setup Environment - Conda

```bash
conda create --name airquality-ds python=3.12
conda activate airquality-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal

```bash
mkdir airquality_project
cd airquality_project
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Setup Environment - Venv (Windows)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Setup Environment - Venv (macOS/Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Notebook

1. Pastikan environment sudah aktif
2. Buka `notebook.ipynb` di Jupyter Notebook / Google Colab
3. Jalankan semua cell secara berurutan dari atas ke bawah
4. File `dashboard/main_data.csv` akan otomatis ter-generate dari cell terakhir

## Run Streamlit Dashboard

```bash
cd dashboard
streamlit run dashboard.py
```

Dashboard akan terbuka otomatis di browser pada alamat `http://localhost:8501`.

## Pertanyaan Bisnis

1. **Tren PM2.5 Bulanan:** Bagaimana tren konsentrasi PM2.5 dan pada bulan apa polusi mencapai puncaknya?
2. **Perbandingan Stasiun:** Stasiun mana yang memiliki tingkat polusi tertinggi dan terendah?
3. **Clustering (Analisis Lanjutan):** Bagaimana pengelompokan stasiun berdasarkan tingkat polutan menggunakan binning?
