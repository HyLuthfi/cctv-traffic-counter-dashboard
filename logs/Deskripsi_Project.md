# 🚦 TrafficVision — Project Plan
### Sistem Penghitung Kendaraan Berbasis Computer Vision dengan Dashboard Interaktif

---

## 📌 Ringkasan Proyek

**TrafficVision** adalah sistem pemantauan lalu lintas real-time yang mengambil feed dari CCTV publik, memprosesnya dengan computer vision untuk menghitung dan mengklasifikasikan kendaraan, lalu menampilkan hasilnya melalui web dashboard interaktif yang dilengkapi peta Leaflet — memungkinkan pengguna mengklik titik CCTV di peta dan langsung melihat live cam, hasil counting, dan analitik historis.

---

## 🗂️ Arsitektur Sistem (High-Level)

```
[ CCTV Publik (RTSP/HTTP Stream) ]
            │
            ▼
[ Capture Service ] ─── ambil frame per detik
            │
            ▼
[ CV Processing Engine ] ─── YOLOv8 / ByteTrack
   • Deteksi kendaraan
   • Klasifikasi (motor, mobil, truk, bus)
   • Object tracking (anti double-count)
            │
            ▼
[ Counting & Aggregator ] ─── hitung per menit/jam/hari
            │
       ┌────┴────┐
       ▼         ▼
[ Database ]  [ WebSocket Server ]
 (PostgreSQL)   (live push ke frontend)
       │
       ▼
[ REST API (FastAPI) ]
       │
       ▼
[ Web Dashboard (React + Leaflet) ]
   • Peta titik CCTV
   • Klik titik → panel detail
   • Live cam stream
   • Live counter + chart
   • Histori harian/mingguan
```

---

## 🧩 Komponen & Teknologi

### 1. Backend — CV Engine
| Komponen | Teknologi | Keterangan |
|---|---|---|
| Bahasa | Python 3.11 | |
| Deteksi objek | YOLOv8 (Ultralytics) | Pre-trained COCO, fine-tune jika perlu |
| Tracking | ByteTrack / SORT | Cegah double-counting satu kendaraan |
| Stream capture | OpenCV + FFmpeg | Ambil RTSP/HTTP dari CCTV |
| Manajemen proses | Celery + Redis | Jalankan tiap kamera secara async |
| Counting logic | Virtual line crossing | Garis virtual di frame → hitung yang melintasi |

### 2. Backend — API & Database
| Komponen | Teknologi | Keterangan |
|---|---|---|
| API framework | FastAPI | REST + WebSocket |
| Database utama | PostgreSQL | Data historis counting |
| Cache / queue | Redis | Celery broker + live data cache |
| ORM | SQLAlchemy | |
| Real-time push | WebSocket (FastAPI) | Live update ke frontend |

### 3. Frontend — Web Dashboard
| Komponen | Teknologi | Keterangan |
|---|---|---|
| Framework | React + Vite | |
| Peta interaktif | Leaflet.js + React-Leaflet | Titik kamera di peta |
| Live cam player | HLS.js / Video.js | Stream video ke browser |
| Chart | Recharts / Chart.js | Grafik kendaraan per jam/hari |
| State management | Zustand | |
| Styling | Tailwind CSS | |
| Real-time | WebSocket hook | Subscribe live count tiap kamera |

### 4. Infrastructure
| Komponen | Keterangan |
|---|---|
| Deployment | Docker + Docker Compose |
| Reverse proxy | Nginx |
| OS target | Ubuntu Server (VPS/local server) |
| GPU (opsional) | CUDA support untuk inferensi lebih cepat |

---

## 🗃️ Struktur Database

### Tabel `cameras`
```sql
id            UUID PRIMARY KEY
name          TEXT          -- "Simpang Sudirman"
location      TEXT          -- deskripsi lokasi
lat           FLOAT         -- koordinat latitude
lng           FLOAT         -- koordinat longitude
stream_url    TEXT          -- RTSP/HTTP URL CCTV
is_active     BOOLEAN
line_config   JSONB         -- konfigurasi virtual line per kamera
created_at    TIMESTAMP
```

### Tabel `vehicle_counts`
```sql
id            UUID PRIMARY KEY
camera_id     UUID REFERENCES cameras(id)
timestamp     TIMESTAMP
vehicle_type  ENUM('motorcycle', 'car', 'truck', 'bus', 'other')
count         INTEGER
direction     ENUM('in', 'out', 'unknown')
```

### Tabel `hourly_summary`
```sql
id            UUID PRIMARY KEY
camera_id     UUID
hour_bucket   TIMESTAMP     -- dibulatkan ke jam
motorcycle    INTEGER
car           INTEGER
truck         INTEGER
bus           INTEGER
total         INTEGER
```

### Tabel `daily_summary`
```sql
id            UUID PRIMARY KEY
camera_id     UUID
date          DATE
peak_hour     TIME
motorcycle    INTEGER
car           INTEGER
truck         INTEGER
bus           INTEGER
total         INTEGER
```

---

## 🖥️ Fitur Web Dashboard

### 🗺️ Halaman Utama — Peta Interaktif
- Peta fullscreen menggunakan Leaflet (basemap: OpenStreetMap / ESRI Satellite)
- Marker tiap titik CCTV aktif dengan status warna:
  - 🟢 Online & streaming
  - 🟡 Online, tidak ada kendaraan
  - 🔴 Offline / koneksi gagal
- Klik marker → sidebar/panel muncul dari kanan

### 📹 Panel Detail Kamera (saat marker diklik)
```
┌─────────────────────────────────┐
│ 📍 Simpang Sudirman - Cam #03   │
├─────────────────────────────────┤
│ [ Live Video Stream ]           │
│                                 │
│  ══════ Virtual Line ══════     │
│                                 │
├─────────────────────────────────┤
│ 🔴 LIVE COUNT — Hari ini        │
│  🏍 Motor     : 1.243           │
│  🚗 Mobil     : 487             │
│  🚛 Truk      : 54              │
│  🚌 Bus       : 21              │
│  ─────────────                  │
│  Total        : 1.805           │
├─────────────────────────────────┤
│ 📈 Grafik Per Jam               │
│  [ Bar chart 00:00 - sekarang ] │
├─────────────────────────────────┤
│ 📅 Histori 7 Hari               │
│  [ Line chart tren mingguan ]   │
├─────────────────────────────────┤
│ ℹ️ Info Kamera                   │
│  Status: Online | FPS: 15       │
│  Resolusi: 1280x720             │
│  Terakhir update: 14:32:01      │
└─────────────────────────────────┘
```

### 📊 Halaman Analytics
- Perbandingan volume antar kamera
- Heatmap kepadatan per jam dalam sehari (matriks jam x hari)
- Ranking kamera tersibuk
- Export data ke CSV / Excel

### ⚙️ Halaman Admin (opsional)
- Tambah / edit / hapus kamera
- Konfigurasi virtual line secara visual (drag & drop di atas frame preview)
- Monitor status semua proses CV secara real-time
- Alert jika kamera offline

---

## 🔄 Alur Kerja Sistem (Flow Detail)

```
1. Admin tambah kamera baru di dashboard
   → Input stream URL, koordinat, nama
   → Konfigurasi virtual counting line

2. Capture Service (Python worker via Celery)
   → Connect ke stream URL
   → Ambil frame tiap X detik (configurable)
   → Kirim frame ke CV Engine

3. CV Engine (YOLOv8 + ByteTrack)
   → Deteksi bounding box tiap kendaraan
   → Track ID unik per objek (antar frame)
   → Cek apakah track melintasi virtual line
   → Klasifikasikan tipe kendaraan

4. Counting Aggregator
   → Simpan event ke PostgreSQL (vehicle_counts)
   → Update Redis cache (live count)
   → Trigger WebSocket broadcast ke frontend

5. Frontend
   → Subscribe WebSocket per camera_id
   → Update counter real-time tanpa refresh
   → Setiap menit: render ulang chart
```

---

## 📁 Struktur Folder Proyek

```
traffic-vision/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── cameras.py
│   │   │   │   ├── counts.py
│   │   │   │   └── analytics.py
│   │   │   └── websocket.py
│   │   ├── cv/
│   │   │   ├── capture.py        # stream reader
│   │   │   ├── detector.py       # YOLOv8 wrapper
│   │   │   ├── tracker.py        # ByteTrack integration
│   │   │   └── counter.py        # virtual line logic
│   │   ├── models/               # SQLAlchemy models
│   │   ├── workers/              # Celery tasks
│   │   └── main.py               # FastAPI app entry
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Map/
│   │   │   │   ├── MapView.jsx
│   │   │   │   └── CameraMarker.jsx
│   │   │   ├── Panel/
│   │   │   │   ├── CameraPanel.jsx
│   │   │   │   ├── LiveStream.jsx
│   │   │   │   ├── LiveCounter.jsx
│   │   │   │   └── ChartHourly.jsx
│   │   │   └── Analytics/
│   │   │       ├── HeatmapChart.jsx
│   │   │       └── CameraRanking.jsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.js
│   │   │   └── useCameraData.js
│   │   ├── stores/               # Zustand stores
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

---

## 🗓️ Rencana Pengembangan (Roadmap)

### Phase 1 — Core CV Pipeline (2–3 minggu)
- [ ] Setup environment Python + YOLOv8
- [ ] Capture stream dari 1 CCTV (RTSP/HTTP)
- [ ] Implementasi virtual counting line
- [ ] Simpan hasil count ke database
- [ ] Unit test akurasi deteksi

### Phase 2 — API & Real-time Backend (1–2 minggu)
- [ ] FastAPI REST endpoints (CRUD kamera, query count)
- [ ] WebSocket server untuk live push
- [ ] Celery workers untuk multi-kamera paralel
- [ ] Hourly & daily aggregation job (cron)

### Phase 3 — Frontend Dashboard (2–3 minggu)
- [ ] Setup React + Leaflet map
- [ ] Marker kamera dengan status real-time
- [ ] Panel detail kamera (stream + counter + chart)
- [ ] Halaman analytics
- [ ] Responsive design (mobile-friendly)

### Phase 4 — Multi-Kamera & Admin Panel (1–2 minggu)
- [ ] Onboard 5–10 kamera CCTV publik lokal
- [ ] Admin panel: kelola kamera
- [ ] Visual virtual line configurator
- [ ] Alert sistem (kamera offline, anomali traffic)

### Phase 5 — Polish & Deployment (1 minggu)
- [ ] Dockerize semua service
- [ ] Deploy ke VPS / server lokal
- [ ] Performance test multi-kamera
- [ ] Dokumentasi teknis & user guide

---

## ⚠️ Tantangan & Solusi

| Tantangan | Solusi |
|---|---|
| Kualitas stream CCTV publik buruk / low res | Preprocessing: denoise, enhance contrast sebelum inferensi |
| Stream sering putus | Auto-reconnect dengan exponential backoff |
| CPU terlalu berat untuk banyak kamera | Batch inference, atau sewa GPU cloud (Lambda Labs, RunPod) |
| Double-counting kendaraan berhenti | ByteTrack persistent ID + confidence threshold |
| Browser tidak bisa akses RTSP langsung | Transcode ke HLS dengan FFmpeg di server, kirim ke browser via HLS |
| Tidak ada akses resmi ke CCTV | Gunakan CCTV publik yang memang open-access; pastikan legalitas |

---

## 🔐 Catatan Legal & Etika

> Pastikan CCTV yang diakses adalah **feed publik yang boleh diakses** (bukan sistem pemerintah yang restricted).  
> Data video **tidak perlu disimpan** — hanya perlu proses frame dan simpan *angka statistiknya* saja.  
> Tidak ada identifikasi individu/wajah — sistem hanya menghitung kendaraan sebagai objek.

---

## 📊 Metrik Keberhasilan

| Metrik | Target |
|---|---|
| Akurasi counting | ≥ 85% dibanding hitungan manual |
| Latensi live counter | < 3 detik dari kejadian nyata |
| Uptime sistem | ≥ 95% |
| Kamera yang didukung paralel | Minimal 5 kamera simultan |
| Waktu load dashboard | < 2 detik |

---

## 🚀 Potensi Pengembangan Lanjutan

- **Prediksi kepadatan** — ML forecasting jam macet berdasarkan histori
- **Notifikasi anomali** — alert jika traffic spike tidak wajar (insiden?)
- **Integrasi Google Maps API** — rute alternatif berdasarkan kepadatan real-time
- **Mobile app** — versi ringkas untuk pantau cepat dari HP
- **Dashboard publik** — akses terbuka untuk warga pantau kondisi jalan kota
- **Pelaporan otomatis** — PDF/Excel dikirim email tiap hari ke instansi terkait

---

*Dokumen ini adalah living document — update sesuai perkembangan proyek.*