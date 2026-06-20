# 📱 Laporan Penjualan TikTok Shop

Dashboard interaktif bergaya **laporan SAP** untuk menganalisis konversi
viewer → pembeli dan profil demografi pembeli di TikTok Shop.
Tugas Sistem Informasi Manajemen. Dibangun dengan [Streamlit](https://streamlit.io).

## ⚠️ Catatan penting soal data
Data dalam aplikasi ini adalah **DATA SIMULASI** yang dibuat otomatis di dalam
kode `app.py`. Data demografi viewer per individu (usia, gender, pekerjaan)
**tidak tersedia publik** dari TikTok karena alasan privasi — TikTok hanya
memberi data agregat & anonim kepada pemilik akun. Untuk keperluan demonstrasi
tugas, data disimulasikan dengan pola yang realistis. Sampaikan hal ini saat
presentasi agar jujur secara akademik.

## 🧾 Pola pemakaian (mengadopsi gaya SAP)
1. Atur **Parameter Laporan** di sidebar.
2. Klik tombol **🔍 LIHAT LAPORAN**.
3. Grafik & analisis diperbarui sesuai parameter yang dipilih.

Saat pertama dibuka, laporan langsung tampil dengan seluruh data (default).

## ✨ Parameter Laporan (sidebar)
- **🗓️ Periode Laporan** — pilih tanggal mulai & selesai
- **📦 Jenis Produk** — pilih semua atau sebagian produk
- **🧑‍🤝‍🧑 Pembeli** — filter Gender & Segmen Usia
- **👁️ Sumber Pembelian** — Dari Postingan vs Dari Toko/Keranjang,
  serta status Like vs Tanpa Like

## 📊 Analisis yang ditampilkan
- KPI: total viewer, total pembeli, tingkat konversi, jumlah postingan
- Funnel viewer → pembeli & tren bulanan
- Jumlah pembelian per bulan
- Profil pembeli per usia × gender (bar + heatmap)
- Sumber pembelian & interaksi like
- Produk terlaris
- Motivasi pembelian: Kebutuhan vs Senang/Impulsif

## 📁 Isi repo (3 file inti, semua di luar tanpa folder)
```
app.py            ← aplikasi utama (data simulasi tertanam di sini)
requirements.txt  ← dependensi (streamlit, pandas, plotly)
README.md         ← file ini
```

## 🚀 Menjalankan lokal
```bash
pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Deploy
Upload ketiga file ke GitHub (tanpa folder), lalu deploy via share.streamlit.io
dengan Main file path `app.py`.
