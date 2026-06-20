"""
Dashboard Analisis Penjualan TikTok Shop — Gaya Laporan (SAP-like)
Tugas Sistem Informasi Manajemen

Pola pemakaian (seperti SAP):
1. Atur PARAMETER LAPORAN di sidebar (periode, produk, pembeli, sumber pembelian).
2. Klik tombol "🔍 LIHAT LAPORAN".
3. Grafik & analisis diperbarui sesuai parameter.

Data: SIMULASI 1 tahun penuh (Jan–Des 2025), dibuat di dalam kode.
Data demografi viewer per individu TIDAK tersedia publik dari TikTok (privasi);
TikTok hanya memberi data agregat. Maka data disimulasikan dengan pola realistis.

Jalankan lokal:  streamlit run app.py
"""

import random
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Laporan Penjualan TikTok Shop", page_icon="📱", layout="wide")
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
GENDER_OPS = ["Perempuan", "Laki-laki"]
SUMBER_OPS = ["Dari Postingan", "Dari Toko/Keranjang"]
LIKE_OPS = ["Like", "Tanpa Like"]


# ──────────────────────────────────────────────────────────────────────────────
# GENERATOR DATA SIMULASI — 1 TAHUN PENUH
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def buat_data_simulasi():
    """
    Hasilkan tabel 'pembeli': satu baris per pembeli (sampel), berisi:
    tanggal, produk, jenis_produk, usia, gender, pekerjaan, motivasi,
    sumber_pembelian (postingan / toko-keranjang), status_like (like / tanpa like).
    Juga tabel 'posts' untuk total viewer & pembeli per postingan.

    LOGIKA (untuk dijelaskan ke dosen):
    - Produk 'basic' (kaos, hijab, kemeja, dalaman): konversi tinggi, KEBUTUHAN,
      usia merata, lebih banyak beli "Dari Toko/Keranjang".
    - Produk 'tren' (aksesoris viral, sneakers, dll): impulsif, SENANG, usia muda,
      lebih banyak beli "Dari Postingan".
    - Pembeli yang datang "Dari Postingan" lebih sering memberi Like.
    - Lonjakan engagement saat tanggal kembar (1.1 ... 12.12). Tren naik sepanjang tahun.
    """
    rnd = random.Random(21)
    PRODUK = {
        "Kaos Polos": "basic", "Hijab Voal": "basic", "Kemeja Formal": "basic",
        "Pakaian Dalam": "basic", "Aksesoris Viral": "tren", "Tas Selempang Trendy": "tren",
        "Sepatu Sneakers": "tren", "Jam Tangan Fashion": "tren", "Kacamata Fashion": "tren",
        "Bucket Hat": "tren",
    }
    PEKERJAAN = ["Pelajar/Mahasiswa", "Karyawan", "Wiraswasta",
                 "Ibu Rumah Tangga", "Freelancer", "Lainnya"]
    bobot_usia = {"basic": [5, 30, 35, 20, 10], "tren": [25, 45, 20, 7, 3]}
    bobot_kerja = {"basic": [30, 30, 15, 15, 5, 5], "tren": [50, 25, 10, 3, 9, 3]}

    posts, pembeli_rows, pid = [], [], 0
    for tgl in pd.date_range("2025-01-01", "2025-12-31", freq="D"):
        faktor = 1 + (tgl.month - 1) * 0.04
        if tgl.day == tgl.month:
            faktor *= 1.8
        for _ in range(rnd.randint(1, 3)):
            pid += 1
            produk = rnd.choice(list(PRODUK))
            jenis = PRODUK[produk]
            viewer = int(rnd.randint(500, 50000) * faktor)
            base_rate = rnd.uniform(0.015, 0.04) if jenis == "basic" else rnd.uniform(0.005, 0.03)
            jml_pembeli = max(0, int(viewer * base_rate))
            posts.append({"tanggal": tgl, "produk": produk, "jenis_produk": jenis,
                          "viewer": viewer, "pembeli": jml_pembeli})

            sampel = max(1, jml_pembeli // 20) if jml_pembeli else 0
            for _ in range(sampel):
                usia = rnd.choices(URUT_USIA, weights=bobot_usia[jenis])[0]
                pekerjaan = rnd.choices(PEKERJAAN, weights=bobot_kerja[jenis])[0]
                if produk in ("Hijab Voal", "Pakaian Dalam"):
                    gender = rnd.choices(GENDER_OPS, weights=[90, 10])[0]
                elif produk in ("Sepatu Sneakers", "Jam Tangan Fashion", "Bucket Hat"):
                    gender = rnd.choices(GENDER_OPS, weights=[40, 60])[0]
                else:
                    gender = rnd.choices(GENDER_OPS, weights=[55, 45])[0]
                motivasi = (rnd.choices(["Kebutuhan", "Senang/Impulsif"], weights=[75, 25])[0]
                            if jenis == "basic"
                            else rnd.choices(["Kebutuhan", "Senang/Impulsif"], weights=[30, 70])[0])
                sumber = (rnd.choices(SUMBER_OPS, weights=[70, 30])[0] if jenis == "tren"
                          else rnd.choices(SUMBER_OPS, weights=[45, 55])[0])
                status_like = (rnd.choices(LIKE_OPS, weights=[65, 35])[0]
                               if sumber == "Dari Postingan"
                               else rnd.choices(LIKE_OPS, weights=[35, 65])[0])
                pembeli_rows.append({
                    "tanggal": tgl, "produk": produk, "jenis_produk": jenis,
                    "usia": usia, "gender": gender, "pekerjaan": pekerjaan,
                    "motivasi": motivasi, "sumber_pembelian": sumber, "status_like": status_like,
                })
    return pd.DataFrame(posts), pd.DataFrame(pembeli_rows)


posts_all, pembeli_all = buat_data_simulasi()
SEMUA_PRODUK = sorted(posts_all["produk"].unique())
TGL_MIN, TGL_MAX = posts_all["tanggal"].min().date(), posts_all["tanggal"].max().date()

# ──────────────────────────────────────────────────────────────────────────────
# State awal: default tampilkan semua data (sebelum tombol diklik)
# ──────────────────────────────────────────────────────────────────────────────
if "param" not in st.session_state:
    st.session_state.param = {
        "tgl_mulai": TGL_MIN, "tgl_selesai": TGL_MAX,
        "produk": "Semua", "gender": "Semua", "usia": "Semua",
        "sumber": "Semua", "like": "Semua",
    }

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR — PARAMETER LAPORAN (gaya SAP, di dalam form + tombol)
# ──────────────────────────────────────────────────────────────────────────────
st.sidebar.title("🧾 Parameter Laporan")
st.sidebar.caption("Atur parameter di bawah, lalu klik **LIHAT LAPORAN** untuk menampilkan hasil.")

with st.sidebar.form("form_parameter"):
    st.markdown("**🗓️ Periode Laporan (Tanggal Transaksi)**")
    c1, c2 = st.columns(2)
    tgl_mulai = c1.date_input("Mulai", value=st.session_state.param["tgl_mulai"],
                              min_value=TGL_MIN, max_value=TGL_MAX)
    tgl_selesai = c2.date_input("Selesai", value=st.session_state.param["tgl_selesai"],
                                min_value=TGL_MIN, max_value=TGL_MAX)

    st.divider()
    st.markdown("**📦 Jenis Produk**")
    produk = st.selectbox("Pilih produk", ["Semua"] + SEMUA_PRODUK,
                          index=0, help="Pilih 'Semua' untuk seluruh produk, atau satu produk tertentu.")

    st.divider()
    st.markdown("**🧑‍🤝‍🧑 Pembeli**")
    gender = st.selectbox("Gender", ["Semua"] + GENDER_OPS, index=0)
    usia = st.selectbox("Segmen Usia", ["Semua"] + URUT_USIA, index=0,
                        help="Pilih 'Semua' atau satu kelompok usia.")

    st.divider()
    st.markdown("**👁️ Sumber Pembelian (Viewer)**")
    sumber = st.selectbox("Sumber", ["Semua"] + SUMBER_OPS, index=0,
                          help="Pembeli datang dari postingan, atau dari kunjungan toko/keranjang.")
    status_like = st.selectbox("Status Like", ["Semua"] + LIKE_OPS, index=0,
                               help="Apakah pembeli memberi like pada produk, atau beli tanpa like.")

    st.divider()
    submit = st.form_submit_button("🔍 LIHAT LAPORAN", use_container_width=True, type="primary")

if submit:
    st.session_state.param = {
        "tgl_mulai": tgl_mulai, "tgl_selesai": tgl_selesai, "produk": produk,
        "gender": gender, "usia": usia, "sumber": sumber, "like": status_like,
    }

P = st.session_state.param  # parameter aktif

# Bantu: ubah pilihan "Semua" menjadi daftar lengkap untuk filter
def daftar(pilihan, semua_opsi):
    """Jika pengguna memilih 'Semua', kembalikan seluruh opsi; jika tidak, satu pilihan."""
    return semua_opsi if pilihan == "Semua" else [pilihan]

f_produk = daftar(P["produk"], SEMUA_PRODUK)
f_gender = daftar(P["gender"], GENDER_OPS)
f_usia = daftar(P["usia"], URUT_USIA)
f_sumber = daftar(P["sumber"], SUMBER_OPS)
f_like = daftar(P["like"], LIKE_OPS)

# ──────────────────────────────────────────────────────────────────────────────
# Terapkan parameter ke data
# ──────────────────────────────────────────────────────────────────────────────
mp = (posts_all["produk"].isin(f_produk)
      & (posts_all["tanggal"].dt.date >= P["tgl_mulai"])
      & (posts_all["tanggal"].dt.date <= P["tgl_selesai"]))
mb = (pembeli_all["produk"].isin(f_produk)
      & pembeli_all["gender"].isin(f_gender)
      & pembeli_all["usia"].isin(f_usia)
      & pembeli_all["sumber_pembelian"].isin(f_sumber)
      & pembeli_all["status_like"].isin(f_like)
      & (pembeli_all["tanggal"].dt.date >= P["tgl_mulai"])
      & (pembeli_all["tanggal"].dt.date <= P["tgl_selesai"]))
posts_f, pembeli_f = posts_all[mp], pembeli_all[mb]

# ──────────────────────────────────────────────────────────────────────────────
# Header laporan
# ──────────────────────────────────────────────────────────────────────────────
st.title("📱 Laporan Penjualan TikTok Shop")
produk_label = "Semua produk" if P["produk"] == "Semua" else P["produk"]
st.caption(f"Periode **{P['tgl_mulai']:%d %b %Y} – {P['tgl_selesai']:%d %b %Y}** · "
           f"{produk_label} · Data simulasi")

if posts_f.empty or pembeli_f.empty:
    st.warning("⚠️ Tidak ada data untuk parameter ini. Longgarkan filter di sidebar, "
               "lalu klik **LIHAT LAPORAN** lagi.")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# KPI
# ──────────────────────────────────────────────────────────────────────────────
total_viewer = posts_f["viewer"].sum()
total_pembeli = posts_f["pembeli"].sum()
konversi = (total_pembeli / total_viewer * 100) if total_viewer else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Viewer", f"{total_viewer:,.0f}")
k2.metric("Total Pembeli", f"{total_pembeli:,.0f}")
k3.metric("Tingkat Konversi", f"{konversi:.2f}%")
k4.metric("Jumlah Postingan", f"{len(posts_f):,}")

st.divider()

# ──────────────────────────────────────────────────────────────────────────────
# Funnel + Tren
# ──────────────────────────────────────────────────────────────────────────────
cc1, cc2 = st.columns([1, 1.3])
with cc1:
    st.subheader("🔻 Funnel Viewer → Pembeli")
    fdf = pd.DataFrame({"Tahap": ["Viewer", "Pembeli"], "Jumlah": [total_viewer, total_pembeli]})
    figf = px.funnel(fdf, x="Jumlah", y="Tahap")
    figf.update_traces(marker_color=["#25F4EE", "#FE2C55"])
    figf.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300)
    st.plotly_chart(figf, use_container_width=True)
with cc2:
    st.subheader("📈 Tren Viewer & Pembeli per Bulan")
    tren = (posts_f.set_index("tanggal").resample("MS")
            .agg(viewer=("viewer", "sum"), pembeli=("pembeli", "sum")).reset_index())
    figt = px.line(tren, x="tanggal", y=["viewer", "pembeli"], markers=True,
                   labels={"value": "Jumlah", "tanggal": "Bulan", "variable": "Metrik"},
                   color_discrete_sequence=["#25F4EE", "#FE2C55"])
    figt.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300, legend_title="")
    st.plotly_chart(figt, use_container_width=True)

st.divider()

# ──────────────────────────────────────────────────────────────────────────────
# Pembelian per bulan
# ──────────────────────────────────────────────────────────────────────────────
st.subheader("📅 Jumlah Pembelian per Bulan")
per_bulan = (posts_f.assign(bulan=posts_f["tanggal"].dt.to_period("M").astype(str))
             .groupby("bulan").agg(pembeli=("pembeli", "sum")).reset_index())
figb = px.bar(per_bulan, x="bulan", y="pembeli", text_auto=True,
              labels={"bulan": "Bulan", "pembeli": "Jumlah Pembeli"})
figb.update_traces(marker_color="#FE2C55")
figb.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=320)
st.plotly_chart(figb, use_container_width=True)

st.divider()

# ──────────────────────────────────────────────────────────────────────────────
# Profil pembeli: usia x gender (bar + heatmap)
# ──────────────────────────────────────────────────────────────────────────────
st.subheader("🎯 Profil Pembeli per Usia & Gender")
st.caption("Angka demografi berbasis sampel — fokus pada PROPORSI antar-segmen.")
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

st.divider()

# ──────────────────────────────────────────────────────────────────────────────
# Sumber pembelian & status like (poin 6)
# ──────────────────────────────────────────────────────────────────────────────
st.subheader("👁️ Sumber Pembelian & Interaksi Like")
cl1, cl2 = st.columns(2)
with cl1:
    sb = pembeli_f.groupby("sumber_pembelian").size().reset_index(name="jumlah")
    figs = px.pie(sb, names="sumber_pembelian", values="jumlah", hole=0.45,
                  color_discrete_sequence=["#FE2C55", "#7C5CFC"])
    figs.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=320,
                       title="Beli dari Postingan vs Toko/Keranjang")
    st.plotly_chart(figs, use_container_width=True)
with cl2:
    lk = pembeli_f.groupby(["sumber_pembelian", "status_like"]).size().reset_index(name="jumlah")
    figl = px.bar(lk, x="sumber_pembelian", y="jumlah", color="status_like", barmode="group",
                  labels={"sumber_pembelian": "Sumber", "jumlah": "Pembeli", "status_like": "Like"},
                  color_discrete_sequence=["#25F4EE", "#FFB347"])
    figl.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=320, title="Like vs Tanpa Like")
    st.plotly_chart(figl, use_container_width=True)

st.divider()

# ──────────────────────────────────────────────────────────────────────────────
# Produk terlaris + Motivasi
# ──────────────────────────────────────────────────────────────────────────────
cpm1, cpm2 = st.columns(2)
with cpm1:
    st.subheader("🏆 Produk Terlaris")
    top = (posts_f.groupby("produk").agg(pembeli=("pembeli", "sum"))
           .sort_values("pembeli").reset_index())
    figp = px.bar(top, x="pembeli", y="produk", orientation="h",
                  labels={"pembeli": "Jumlah Pembeli", "produk": "Produk"})
    figp.update_traces(marker_color="#FE2C55")
    figp.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=380)
    st.plotly_chart(figp, use_container_width=True)
with cpm2:
    st.subheader("🧠 Motivasi Pembelian")
    st.caption("Basic → KEBUTUHAN; tren → SENANG/impulsif.")
    mot = pembeli_f.groupby("motivasi").size().reset_index(name="jumlah")
    figm = px.pie(mot, names="motivasi", values="jumlah", hole=0.45,
                  color_discrete_sequence=["#2DD4BF", "#FFB347"])
    figm.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=380)
    st.plotly_chart(figm, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# Data mentah & unduh
# ──────────────────────────────────────────────────────────────────────────────
with st.expander("🔍 Lihat data pembeli (sesuai parameter)"):
    st.dataframe(pembeli_f, use_container_width=True)
    st.download_button("⬇️ Unduh CSV", pembeli_f.to_csv(index=False).encode("utf-8"),
                       file_name="laporan_pembeli_tiktok.csv", mime="text/csv")

st.caption(f"Laporan dibuat {datetime.now():%d %b %Y %H:%M} · Data simulasi 1 tahun · Tugas SIM")
