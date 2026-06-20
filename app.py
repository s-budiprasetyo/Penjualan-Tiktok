"""
Dashboard Analisis Penjualan TikTok Shop
Tugas Sistem Informasi Manajemen

Menganalisis:
- Funnel: viewer postingan -> pembeli (tingkat konversi)
- Pembelian per bulan
- Profil demografi pembeli (usia, gender, pekerjaan)
- Konversi per segmen usia & gender
- Motivasi pembelian: KEBUTUHAN vs SENANG/IMPULSIF

CATATAN PENTING (untuk presentasi):
Data di aplikasi ini adalah DATA SIMULASI yang dibuat otomatis di dalam kode.
Data demografi viewer per individu (usia/gender/pekerjaan) TIDAK tersedia publik
dari TikTok karena alasan privasi -- TikTok hanya memberi data agregat & anonim
ke pemilik akun. Maka untuk demonstrasi, data ini disimulasikan dengan pola yang
realistis. Logika simulasi dijelaskan di fungsi buat_data_simulasi() di bawah.

Jalankan lokal:  streamlit run app.py
"""

import random
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Dashboard TikTok Shop", page_icon="📱", layout="wide")

st.markdown(
    """
    <style>
      [data-testid="stMetricValue"] { color: #FE2C55; font-weight: 700; }
      h1, h2, h3 { letter-spacing: -0.5px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Palet warna TikTok: merah-pink #FE2C55, cyan #25F4EE, hitam
WARNA = ["#FE2C55", "#25F4EE", "#FFB347", "#7C5CFC", "#2DD4BF", "#F472B6"]


# ──────────────────────────────────────────────────────────────────────────────
# GENERATOR DATA SIMULASI (tertanam di kode, tanpa file eksternal)
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def buat_data_simulasi():
    """
    Hasilkan dua tabel:
      1) posts  : ringkasan tiap postingan (viewer & jumlah pembeli)
      2) pembeli: satu baris per pembeli, lengkap dengan profil demografi

    LOGIKA SIMULASI (bisa dijelaskan ke dosen):
    - Produk 'basic' (kaos, hijab, kemeja) -> konversi lebih tinggi & cenderung
      dibeli karena KEBUTUHAN, peminat lebih merata di semua usia.
    - Produk 'tren' (aksesoris viral, sneakers) -> konversi lebih impulsif &
      cenderung dibeli karena SENANG, peminat condong ke usia muda (13-24).
    - Gender & pekerjaan diberi distribusi berbeda per produk agar segmentasi
      terlihat (mis. hijab dominan perempuan).
    """
    rnd = random.Random(21)

    PRODUK = {
        "Kaos Polos": "basic",
        "Hijab Voal": "basic",
        "Kemeja Formal": "basic",
        "Aksesoris Viral": "tren",
        "Tas Selempang Trendy": "tren",
        "Sepatu Sneakers": "tren",
        "Jam Tangan Fashion": "tren",
        "Kacamata Fashion": "tren",
    }
    USIA = ["13-17", "18-24", "25-34", "35-44", "45+"]
    GENDER = ["Perempuan", "Laki-laki"]
    PEKERJAAN = ["Pelajar/Mahasiswa", "Karyawan", "Wiraswasta",
                 "Ibu Rumah Tangga", "Freelancer", "Lainnya"]

    # bobot distribusi usia berbeda untuk produk basic vs tren
    bobot_usia = {
        "basic": [5, 30, 35, 20, 10],
        "tren": [25, 45, 20, 7, 3],
    }
    bobot_pekerjaan = {
        "basic": [30, 30, 15, 15, 5, 5],
        "tren": [50, 25, 10, 3, 9, 3],
    }

    posts = []
    pembeli_rows = []
    post_id = 0

    for tgl in pd.date_range("2025-01-01", "2025-06-30", freq="D"):
        for _ in range(rnd.randint(1, 3)):
            post_id += 1
            produk = rnd.choice(list(PRODUK))
            jenis = PRODUK[produk]
            viewer = rnd.randint(500, 50000)

            # konversi: produk basic sedikit lebih tinggi
            base_rate = rnd.uniform(0.015, 0.04) if jenis == "basic" else rnd.uniform(0.005, 0.03)
            jml_pembeli = max(0, int(viewer * base_rate))

            posts.append({
                "post_id": post_id, "tanggal": tgl, "produk": produk,
                "jenis_produk": jenis, "viewer": viewer, "pembeli": jml_pembeli,
            })

            # Untuk tabel profil demografi, ambil sampel pembeli (1 dari 20) agar
            # tetap ringan di Streamlit Cloud. Proporsi tiap segmen tetap terjaga.
            sampel = max(1, jml_pembeli // 20) if jml_pembeli else 0
            for _ in range(sampel):
                usia = rnd.choices(USIA, weights=bobot_usia[jenis])[0]
                pekerjaan = rnd.choices(PEKERJAAN, weights=bobot_pekerjaan[jenis])[0]
                # gender: hijab & ibu rumah tangga dominan perempuan
                if produk == "Hijab Voal":
                    gender = rnd.choices(GENDER, weights=[95, 5])[0]
                elif produk in ("Sepatu Sneakers", "Jam Tangan Fashion"):
                    gender = rnd.choices(GENDER, weights=[40, 60])[0]
                else:
                    gender = rnd.choices(GENDER, weights=[55, 45])[0]

                # motivasi: basic -> kebutuhan, tren -> senang (dengan sedikit variasi)
                if jenis == "basic":
                    motivasi = rnd.choices(["Kebutuhan", "Senang/Impulsif"], weights=[75, 25])[0]
                else:
                    motivasi = rnd.choices(["Kebutuhan", "Senang/Impulsif"], weights=[30, 70])[0]

                pembeli_rows.append({
                    "post_id": post_id, "tanggal": tgl, "produk": produk,
                    "jenis_produk": jenis, "usia": usia, "gender": gender,
                    "pekerjaan": pekerjaan, "motivasi": motivasi,
                })

    return pd.DataFrame(posts), pd.DataFrame(pembeli_rows)


# ──────────────────────────────────────────────────────────────────────────────
posts, pembeli = buat_data_simulasi()

st.title("📱 Dashboard Analisis TikTok Shop")
st.caption("Analisis konversi viewer → pembeli & profil demografi · Data simulasi untuk demonstrasi")

# ──────────────────────────────────────────────────────────────────────────────
# Sidebar filter
# ──────────────────────────────────────────────────────────────────────────────
st.sidebar.title("🎚️ Filter")
st.sidebar.info("Data ini adalah **simulasi** untuk keperluan demonstrasi tugas.")

produk_pilih = st.sidebar.multiselect(
    "Filter Produk", sorted(posts["produk"].unique()),
    default=sorted(posts["produk"].unique()),
)
bulan_opsi = ["Semua"] + [f"{b:02d}" for b in sorted(posts["tanggal"].dt.month.unique())]
bulan_pilih = st.sidebar.selectbox("Filter Bulan", bulan_opsi)

# Terapkan filter
mask_p = posts["produk"].isin(produk_pilih)
mask_b = pembeli["produk"].isin(produk_pilih)
if bulan_pilih != "Semua":
    mask_p &= posts["tanggal"].dt.month == int(bulan_pilih)
    mask_b &= pembeli["tanggal"].dt.month == int(bulan_pilih)
posts_f = posts[mask_p]
pembeli_f = pembeli[mask_b]

if posts_f.empty:
    st.warning("Tidak ada data untuk filter ini. Ubah filter di sidebar.")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# KPI
# ──────────────────────────────────────────────────────────────────────────────
total_viewer = posts_f["viewer"].sum()
total_pembeli = posts_f["pembeli"].sum()
konversi = (total_pembeli / total_viewer * 100) if total_viewer else 0
n_post = len(posts_f)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Viewer", f"{total_viewer:,.0f}")
k2.metric("Total Pembeli", f"{total_pembeli:,.0f}")
k3.metric("Tingkat Konversi", f"{konversi:.2f}%")
k4.metric("Jumlah Postingan", f"{n_post:,}")

st.divider()

# ──────────────────────────────────────────────────────────────────────────────
# 1) FUNNEL viewer -> pembeli
# ──────────────────────────────────────────────────────────────────────────────
st.subheader("🔻 Funnel: Viewer → Pembeli")
funnel_df = pd.DataFrame({
    "Tahap": ["Melihat Postingan (Viewer)", "Membeli Produk (Pembeli)"],
    "Jumlah": [total_viewer, total_pembeli],
})
figf = px.funnel(funnel_df, x="Jumlah", y="Tahap")
figf.update_traces(marker_color=["#25F4EE", "#FE2C55"])
figf.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=240)
st.plotly_chart(figf, use_container_width=True)

st.divider()

# ──────────────────────────────────────────────────────────────────────────────
# 2) Pembelian per bulan
# ──────────────────────────────────────────────────────────────────────────────
st.subheader("📅 Jumlah Pembelian per Bulan")
per_bulan = (
    posts_f.assign(bulan=posts_f["tanggal"].dt.to_period("M").astype(str))
    .groupby("bulan")
    .agg(viewer=("viewer", "sum"), pembeli=("pembeli", "sum"))
    .reset_index()
)
figb = px.bar(per_bulan, x="bulan", y="pembeli",
              labels={"bulan": "Bulan", "pembeli": "Jumlah Pembeli"}, text_auto=True)
figb.update_traces(marker_color="#FE2C55")
figb.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=320)
st.plotly_chart(figb, use_container_width=True)

st.divider()

# ──────────────────────────────────────────────────────────────────────────────
# 3) KONVERSI PER SEGMEN USIA & GENDER  (fokus utama)
# ──────────────────────────────────────────────────────────────────────────────
st.subheader("🎯 Profil Pembeli per Segmen Usia & Gender")
st.caption(
    "Fokus analisis: kelompok mana yang paling banyak membeli. "
    "Angka demografi berbasis sampel pembeli, sehingga yang relevan adalah "
    "PROPORSI antar-segmen (bukan angka absolutnya)."
)

cseg1, cseg2 = st.columns(2)
with cseg1:
    seg_usia = pembeli_f.groupby(["usia", "gender"]).size().reset_index(name="jumlah")
    urut_usia = ["13-17", "18-24", "25-34", "35-44", "45+"]
    figu = px.bar(seg_usia, x="usia", y="jumlah", color="gender", barmode="group",
                  category_orders={"usia": urut_usia},
                  labels={"usia": "Kelompok Usia", "jumlah": "Jumlah Pembeli", "gender": "Gender"},
                  color_discrete_sequence=["#FE2C55", "#25F4EE"])
    figu.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=340, title="Pembeli per Usia & Gender")
    st.plotly_chart(figu, use_container_width=True)

with cseg2:
    seg_gender = pembeli_f.groupby("gender").size().reset_index(name="jumlah")
    figg = px.pie(seg_gender, names="gender", values="jumlah", hole=0.45,
                  color_discrete_sequence=["#FE2C55", "#25F4EE"])
    figg.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=340, title="Proporsi Gender Pembeli")
    st.plotly_chart(figg, use_container_width=True)

# Pekerjaan
st.subheader("💼 Pembeli berdasarkan Pekerjaan")
seg_kerja = pembeli_f.groupby("pekerjaan").size().reset_index(name="jumlah").sort_values("jumlah")
figk = px.bar(seg_kerja, x="jumlah", y="pekerjaan", orientation="h",
              labels={"jumlah": "Jumlah Pembeli", "pekerjaan": "Pekerjaan"})
figk.update_traces(marker_color="#7C5CFC")
figk.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300)
st.plotly_chart(figk, use_container_width=True)

st.divider()

# ──────────────────────────────────────────────────────────────────────────────
# 4) MOTIVASI: Kebutuhan vs Senang/Impulsif
# ──────────────────────────────────────────────────────────────────────────────
st.subheader("🧠 Motivasi Pembelian: Kebutuhan vs Senang/Impulsif")
st.caption(
    "Label simulasi berdasarkan jenis produk: produk basic (kaos, hijab, kemeja) "
    "cenderung dibeli karena KEBUTUHAN; produk tren (aksesoris viral, sneakers) "
    "cenderung dibeli karena SENANG/impulsif."
)
cmot1, cmot2 = st.columns(2)
with cmot1:
    mot = pembeli_f.groupby("motivasi").size().reset_index(name="jumlah")
    figm = px.pie(mot, names="motivasi", values="jumlah", hole=0.45,
                  color_discrete_sequence=["#2DD4BF", "#FFB347"])
    figm.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=320, title="Proporsi Motivasi")
    st.plotly_chart(figm, use_container_width=True)
with cmot2:
    mot_produk = pembeli_f.groupby(["produk", "motivasi"]).size().reset_index(name="jumlah")
    figmp = px.bar(mot_produk, x="produk", y="jumlah", color="motivasi", barmode="stack",
                   labels={"produk": "Produk", "jumlah": "Pembeli", "motivasi": "Motivasi"},
                   color_discrete_sequence=["#2DD4BF", "#FFB347"])
    figmp.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=320,
                        title="Motivasi per Produk", xaxis_tickangle=-40)
    st.plotly_chart(figmp, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# Data mentah & unduh
# ──────────────────────────────────────────────────────────────────────────────
with st.expander("🔍 Lihat data pembeli (simulasi)"):
    st.dataframe(pembeli_f, use_container_width=True)
    st.download_button(
        "⬇️ Unduh CSV data pembeli",
        pembeli_f.to_csv(index=False).encode("utf-8"),
        file_name="pembeli_tiktok_simulasi.csv",
        mime="text/csv",
    )

st.caption(f"Dashboard di-render {datetime.now():%d %b %Y %H:%M} · Data simulasi · Tugas SIM")
