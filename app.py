"""
Dashboard Analisis Penjualan TikTok Shop (versi lengkap)
Tugas Sistem Informasi Manajemen

Menganalisis (1 tahun penuh, Jan–Des 2025):
- Funnel viewer -> pembeli (tingkat konversi)
- Tren pembelian, viewer, & konversi per bulan/minggu/hari
- Profil demografi pembeli: usia, gender, pekerjaan
- Pembeli per segmen usia x gender (heatmap + bar)
- Produk terlaris
- Motivasi pembelian: Kebutuhan vs Senang/Impulsif

CATATAN (untuk presentasi):
Data adalah SIMULASI yang dibuat otomatis di dalam kode. Data demografi viewer
per individu TIDAK tersedia publik dari TikTok karena privasi -- TikTok hanya
memberi data agregat & anonim. Maka data disimulasikan dengan pola realistis.

Jalankan lokal:  streamlit run app.py
"""

import io
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

URUT_USIA = ["13-17", "18-24", "25-34", "35-44", "45+"]


# ──────────────────────────────────────────────────────────────────────────────
# GENERATOR DATA SIMULASI — 1 TAHUN PENUH (tertanam di kode)
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def buat_data_simulasi():
    """
    posts   : ringkasan tiap postingan (viewer, pembeli, like, durasi tonton)
    pembeli : satu baris per pembeli (sampel), lengkap profil demografi

    LOGIKA SIMULASI (bisa dijelaskan ke dosen):
    - Produk 'basic' (kaos, hijab, kemeja, dalaman) -> konversi lebih tinggi,
      dibeli lebih karena KEBUTUHAN, peminat merata di semua usia.
    - Produk 'tren' (aksesoris viral, sneakers, dll) -> lebih impulsif,
      dibeli lebih karena SENANG, peminat condong usia muda (13-24).
    - Lonjakan engagement saat tanggal kembar (1.1 ... 12.12) ala event TikTok.
    - Tren naik perlahan sepanjang tahun (akun makin besar).
    """
    rnd = random.Random(21)

    PRODUK = {
        "Kaos Polos": "basic",
        "Hijab Voal": "basic",
        "Kemeja Formal": "basic",
        "Pakaian Dalam": "basic",
        "Aksesoris Viral": "tren",
        "Tas Selempang Trendy": "tren",
        "Sepatu Sneakers": "tren",
        "Jam Tangan Fashion": "tren",
        "Kacamata Fashion": "tren",
        "Bucket Hat": "tren",
    }
    GENDER = ["Perempuan", "Laki-laki"]
    PEKERJAAN = ["Pelajar/Mahasiswa", "Karyawan", "Wiraswasta",
                 "Ibu Rumah Tangga", "Freelancer", "Lainnya"]
    bobot_usia = {"basic": [5, 30, 35, 20, 10], "tren": [25, 45, 20, 7, 3]}
    bobot_kerja = {"basic": [30, 30, 15, 15, 5, 5], "tren": [50, 25, 10, 3, 9, 3]}

    posts, pembeli_rows, pid = [], [], 0

    for tgl in pd.date_range("2025-01-01", "2025-12-31", freq="D"):
        faktor = 1 + (tgl.month - 1) * 0.04      # tren naik sepanjang tahun
        if tgl.day == tgl.month:                  # lonjakan tanggal kembar
            faktor *= 1.8

        for _ in range(rnd.randint(1, 3)):
            pid += 1
            produk = rnd.choice(list(PRODUK))
            jenis = PRODUK[produk]
            viewer = int(rnd.randint(500, 50000) * faktor)
            durasi = round(rnd.uniform(3, 35), 1)
            like = int(viewer * rnd.uniform(0.03, 0.12))

            base_rate = rnd.uniform(0.015, 0.04) if jenis == "basic" else rnd.uniform(0.005, 0.03)
            jml_pembeli = max(0, int(viewer * base_rate))

            posts.append({
                "post_id": pid, "tanggal": tgl, "produk": produk, "jenis_produk": jenis,
                "viewer": viewer, "pembeli": jml_pembeli, "like": like,
                "durasi_tonton": durasi,
            })

            sampel = max(1, jml_pembeli // 20) if jml_pembeli else 0
            for _ in range(sampel):
                usia = rnd.choices(URUT_USIA, weights=bobot_usia[jenis])[0]
                pekerjaan = rnd.choices(PEKERJAAN, weights=bobot_kerja[jenis])[0]
                if produk in ("Hijab Voal", "Pakaian Dalam"):
                    gender = rnd.choices(GENDER, weights=[90, 10])[0]
                elif produk in ("Sepatu Sneakers", "Jam Tangan Fashion", "Bucket Hat"):
                    gender = rnd.choices(GENDER, weights=[40, 60])[0]
                else:
                    gender = rnd.choices(GENDER, weights=[55, 45])[0]
                motivasi = (rnd.choices(["Kebutuhan", "Senang/Impulsif"], weights=[75, 25])[0]
                            if jenis == "basic"
                            else rnd.choices(["Kebutuhan", "Senang/Impulsif"], weights=[30, 70])[0])
                pembeli_rows.append({
                    "post_id": pid, "tanggal": tgl, "produk": produk, "jenis_produk": jenis,
                    "usia": usia, "gender": gender, "pekerjaan": pekerjaan, "motivasi": motivasi,
                })

    return pd.DataFrame(posts), pd.DataFrame(pembeli_rows)


@st.cache_data(show_spinner=False)
def baca_html(file_bytes: bytes):
    return pd.read_html(io.BytesIO(file_bytes))


# ──────────────────────────────────────────────────────────────────────────────
posts_all, pembeli_all = buat_data_simulasi()

st.title("📱 Dashboard Analisis TikTok Shop")
st.caption("Analisis konversi viewer → pembeli & profil demografi · Data simulasi 1 tahun (2025)")

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
st.sidebar.title("🛒 Sumber Data")
st.sidebar.caption("Pakai data simulasi, atau upload file HTML hasil scrape TikTok.")
uploaded = st.sidebar.file_uploader("Upload file HTML (opsional)", type=["html", "htm"])
pakai_simulasi = st.sidebar.checkbox("Pakai data simulasi", value=True)

posts, pembeli = posts_all.copy(), pembeli_all.copy()
if uploaded is not None:
    try:
        tabel = baca_html(uploaded.read())
        if tabel:
            st.sidebar.success(f"{len(tabel)} tabel terbaca dari HTML.")
            st.sidebar.caption("Catatan: analisis demografi tetap memakai data simulasi, "
                               "karena file scrape umumnya tak memuat demografi viewer.")
    except Exception as e:  # noqa: BLE001
        st.sidebar.error(f"Gagal membaca HTML: {e}")

st.sidebar.divider()
st.sidebar.subheader("🔧 Pemetaan Kolom")
st.sidebar.caption("Kolom sudah dipetakan otomatis & dikunci agar tidak salah. "
                   "(Pada data hasil upload, pemetaan ini bisa diaktifkan untuk disesuaikan.)")

# Nilai pemetaan dikunci ke nama kolom yang benar.
col_tanggal, col_produk, col_viewer, col_pembeli = "tanggal", "produk", "viewer", "pembeli"

# Ditampilkan sebagai dropdown yang DINONAKTIFKAN (disabled) — terlihat tapi tak bisa salah.
st.sidebar.selectbox("Kolom Tanggal", [col_tanggal], index=0, disabled=True)
st.sidebar.selectbox("Kolom Produk", [col_produk], index=0, disabled=True)
st.sidebar.selectbox("Kolom Viewer", [col_viewer], index=0, disabled=True)
st.sidebar.selectbox("Kolom Pembeli", [col_pembeli], index=0, disabled=True)

st.sidebar.divider()
st.sidebar.subheader("🎚️ Filter Data")
produk_pilih = st.sidebar.multiselect("Produk", sorted(posts[col_produk].unique()),
                                      default=sorted(posts[col_produk].unique()))
tgl_min, tgl_max = posts[col_tanggal].min(), posts[col_tanggal].max()
rentang = st.sidebar.date_input("Rentang Tanggal", value=(tgl_min.date(), tgl_max.date()),
                                min_value=tgl_min.date(), max_value=tgl_max.date())
granularitas = st.sidebar.radio("Granularitas", ["Harian", "Mingguan", "Bulanan"], index=2)
freq = {"Harian": "D", "Mingguan": "W", "Bulanan": "MS"}[granularitas]
usia_pilih = st.sidebar.multiselect("Segmen Usia", URUT_USIA, default=URUT_USIA)
gender_pilih = st.sidebar.multiselect("Gender", ["Perempuan", "Laki-laki"],
                                      default=["Perempuan", "Laki-laki"])
motivasi_pilih = st.sidebar.multiselect("Motivasi", ["Kebutuhan", "Senang/Impulsif"],
                                        default=["Kebutuhan", "Senang/Impulsif"])

# Terapkan filter
mp = posts[col_produk].isin(produk_pilih)
mb = (pembeli["produk"].isin(produk_pilih) & pembeli["usia"].isin(usia_pilih)
      & pembeli["gender"].isin(gender_pilih) & pembeli["motivasi"].isin(motivasi_pilih))
if isinstance(rentang, (list, tuple)) and len(rentang) == 2:
    mp &= (posts[col_tanggal].dt.date >= rentang[0]) & (posts[col_tanggal].dt.date <= rentang[1])
    mb &= (pembeli["tanggal"].dt.date >= rentang[0]) & (pembeli["tanggal"].dt.date <= rentang[1])
posts_f, pembeli_f = posts[mp], pembeli[mb]

if posts_f.empty:
    st.warning("Tidak ada data untuk filter ini. Longgarkan filter di sidebar.")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# KPI
# ──────────────────────────────────────────────────────────────────────────────
total_viewer = posts_f[col_viewer].sum()
total_pembeli = posts_f[col_pembeli].sum()
konversi = (total_pembeli / total_viewer * 100) if total_viewer else 0
durasi_avg = posts_f["durasi_tonton"].mean()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Viewer", f"{total_viewer:,.0f}")
k2.metric("Total Pembeli", f"{total_pembeli:,.0f}")
k3.metric("Tingkat Konversi", f"{konversi:.2f}%")
k4.metric("Jumlah Postingan", f"{len(posts_f):,}")
k5.metric("Rata² Durasi Tonton", f"{durasi_avg:.1f} dtk")

st.divider()

# Funnel + Tren
c1, c2 = st.columns([1, 1.3])
with c1:
    st.subheader("🔻 Funnel Viewer → Pembeli")
    fdf = pd.DataFrame({"Tahap": ["Viewer", "Pembeli"], "Jumlah": [total_viewer, total_pembeli]})
    figf = px.funnel(fdf, x="Jumlah", y="Tahap")
    figf.update_traces(marker_color=["#25F4EE", "#FE2C55"])
    figf.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300)
    st.plotly_chart(figf, use_container_width=True)
with c2:
    st.subheader("📈 Tren Viewer & Pembeli")
    tren = (posts_f.set_index(col_tanggal).resample(freq)
            .agg(viewer=(col_viewer, "sum"), pembeli=(col_pembeli, "sum")).reset_index())
    figt = px.line(tren, x=col_tanggal, y=["viewer", "pembeli"], markers=True,
                   labels={"value": "Jumlah", col_tanggal: "Periode", "variable": "Metrik"},
                   color_discrete_sequence=["#25F4EE", "#FE2C55"])
    figt.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300, legend_title="")
    st.plotly_chart(figt, use_container_width=True)

st.divider()

# Pembelian per bulan
st.subheader("📅 Jumlah Pembelian per Bulan")
per_bulan = (posts_f.assign(bulan=posts_f[col_tanggal].dt.to_period("M").astype(str))
             .groupby("bulan").agg(pembeli=(col_pembeli, "sum")).reset_index())
figb = px.bar(per_bulan, x="bulan", y="pembeli", text_auto=True,
              labels={"bulan": "Bulan", "pembeli": "Jumlah Pembeli"})
figb.update_traces(marker_color="#FE2C55")
figb.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=320)
st.plotly_chart(figb, use_container_width=True)

st.divider()

# Segmen usia x gender
st.subheader("🎯 Pembeli per Segmen Usia × Gender")
st.caption("Fokus analisis. Angka demografi berbasis sampel — yang relevan PROPORSI antar-segmen.")
cs1, cs2 = st.columns(2)
with cs1:
    seg = pembeli_f.groupby(["usia", "gender"]).size().reset_index(name="jumlah")
    figu = px.bar(seg, x="usia", y="jumlah", color="gender", barmode="group",
                  category_orders={"usia": URUT_USIA},
                  labels={"usia": "Usia", "jumlah": "Pembeli (sampel)", "gender": "Gender"},
                  color_discrete_sequence=["#FE2C55", "#25F4EE"])
    figu.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=340, title="Bar: Usia × Gender")
    st.plotly_chart(figu, use_container_width=True)
with cs2:
    pivot = (pembeli_f.groupby(["usia", "gender"]).size().reset_index(name="jumlah")
             .pivot(index="usia", columns="gender", values="jumlah").reindex(URUT_USIA).fillna(0))
    figh = px.imshow(pivot, text_auto=True, aspect="auto", color_continuous_scale="Reds",
                     labels=dict(x="Gender", y="Usia", color="Pembeli"))
    figh.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=340, title="Heatmap: Usia × Gender")
    st.plotly_chart(figh, use_container_width=True)

# Pekerjaan
st.subheader("💼 Pembeli berdasarkan Pekerjaan")
seg_kerja = pembeli_f.groupby("pekerjaan").size().reset_index(name="jumlah").sort_values("jumlah")
figk = px.bar(seg_kerja, x="jumlah", y="pekerjaan", orientation="h",
              labels={"jumlah": "Pembeli (sampel)", "pekerjaan": "Pekerjaan"})
figk.update_traces(marker_color="#7C5CFC")
figk.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300)
st.plotly_chart(figk, use_container_width=True)

st.divider()

# Produk terlaris
st.subheader("🏆 Produk Terlaris (jumlah pembeli)")
top_prod = (posts_f.groupby(col_produk).agg(pembeli=(col_pembeli, "sum"))
            .sort_values("pembeli").reset_index())
figp = px.bar(top_prod, x="pembeli", y=col_produk, orientation="h",
              labels={"pembeli": "Jumlah Pembeli", col_produk: "Produk"})
figp.update_traces(marker_color="#FE2C55")
figp.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=380)
st.plotly_chart(figp, use_container_width=True)

st.divider()

# Motivasi
st.subheader("🧠 Motivasi Pembelian: Kebutuhan vs Senang/Impulsif")
st.caption("Produk basic (kaos, hijab, kemeja, dalaman) → cenderung KEBUTUHAN; "
           "produk tren (aksesoris viral, sneakers, dll) → cenderung SENANG/impulsif.")
cm1, cm2 = st.columns(2)
with cm1:
    mot = pembeli_f.groupby("motivasi").size().reset_index(name="jumlah")
    figm = px.pie(mot, names="motivasi", values="jumlah", hole=0.45,
                  color_discrete_sequence=["#2DD4BF", "#FFB347"])
    figm.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=320, title="Proporsi Motivasi")
    st.plotly_chart(figm, use_container_width=True)
with cm2:
    mp2 = pembeli_f.groupby(["produk", "motivasi"]).size().reset_index(name="jumlah")
    figmp = px.bar(mp2, x="produk", y="jumlah", color="motivasi", barmode="stack",
                   labels={"produk": "Produk", "jumlah": "Pembeli", "motivasi": "Motivasi"},
                   color_discrete_sequence=["#2DD4BF", "#FFB347"])
    figmp.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=320,
                        title="Motivasi per Produk", xaxis_tickangle=-40)
    st.plotly_chart(figmp, use_container_width=True)

# Data mentah
with st.expander("🔍 Lihat data postingan & pembeli (simulasi)"):
    st.write("**Ringkasan per postingan**")
    st.dataframe(posts_f, use_container_width=True)
    st.write("**Detail pembeli (sampel)**")
    st.dataframe(pembeli_f, use_container_width=True)
    st.download_button("⬇️ Unduh CSV data pembeli",
                       pembeli_f.to_csv(index=False).encode("utf-8"),
                       file_name="pembeli_tiktok_simulasi.csv", mime="text/csv")

st.caption(f"Dashboard di-render {datetime.now():%d %b %Y %H:%M} · Data simulasi 1 tahun · Tugas SIM")
