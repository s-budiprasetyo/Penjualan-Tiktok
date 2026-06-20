# 📱 Dashboard Analisis TikTok Shop

Dashboard interaktif untuk menganalisis konversi viewer → pembeli dan profil
demografi pembeli di TikTok Shop. Tugas Sistem Informasi Manajemen.
Dibangun dengan [Streamlit](https://streamlit.io).

## ⚠️ Catatan penting soal data
Data dalam aplikasi ini adalah **DATA SIMULASI** yang dibuat otomatis di dalam
kode `app.py`. Data demografi viewer per individu (usia, gender, pekerjaan)
**tidak tersedia publik** dari TikTok karena alasan privasi — TikTok hanya
memberi data agregat & anonim kepada pemilik akun. Untuk keperluan demonstrasi
tugas, data disimulasikan dengan pola yang realistis. Sampaikan hal ini saat
presentasi agar jujur secara akademik.

## ✨ Fitur
- **Data simulasi 1 tahun penuh** (Jan–Des 2025)
- Sidebar lengkap: sumber data, **pemetaan kolom**, dan banyak **filter**
  (produk, rentang tanggal, granularitas, usia, gender, motivasi)
- 5 KPI: total viewer, total pembeli, tingkat konversi, jumlah postingan, rata² durasi tonton
- **Funnel** viewer → pembeli + **tren** viewer & pembeli (harian/mingguan/bulanan)
- **Jumlah pembelian per bulan**
- **Pembeli per segmen usia × gender** (bar + heatmap) — fokus utama
- Profil pembeli berdasarkan **pekerjaan**
- **Produk terlaris**
- Analisis **motivasi pembelian**: Kebutuhan vs Senang/Impulsif
- Filter produk & bulan, plus unduh data CSV

## 📁 Isi repo (3 file inti, semua di luar tanpa folder)
```
app.py            ← aplikasi utama (data simulasi tertanam di sini)
requirements.txt  ← dependensi
README.md         ← file ini
```

## 🚀 Menjalankan lokal
```bash
pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Upload ke GitHub & deploy ke Streamlit (lewat website)
**Tahap 1 — GitHub:** New repository → Public → jangan centang "Add README" →
Create → "uploading an existing file" → seret `app.py`, `requirements.txt`,
`README.md` (TANPA folder) → Commit changes.

**Tahap 2 — Streamlit:** share.streamlit.io → Create app → Repository pilih repo
ini, Branch `main`, Main file path `app.py` → Deploy.

✅ Aplikasi langsung menampilkan grafik dari data simulasi — tanpa error
"file tidak ditemukan", karena data dibuat di dalam `app.py` sendiri.
