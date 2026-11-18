# Sceadule-elite

Eksperimen konten: skill pembuat prompt poster sinematik dan alat carousel Instagram (hook, 11 slide, upload & jadwal via Repliz).

Isi saat ini adalah seri 103 carousel bertema **elit global**: forum dan lembaga, sistem moneter, operasi rahasia yang terbukti lewat dokumen, uang dan lobi, teknologi, Indonesia, sejarah, iklim dan pangan, serta literasi media. Setiap carousel memisahkan fakta terdokumentasi dari spekulasi dan ditutup dengan pertanyaan untuk komentar.

## Isi repo

| Lokasi | Fungsi |
|---|---|
| `carousel/content/dayNN.py` | Data konten per hari (topik, 9 slide isi, kesimpulan, pertanyaan) |
| `carousel/hooks.py` | Hook sampul gaya percakapan untuk tiap carousel |
| `carousel/engine.py` | Template slide (HTML/CSS/SVG) dan pembuat caption |
| `carousel/render.js` | Render HTML ke JPG 1080×1350 dengan Playwright |
| `carousel/pipeline.py` | Render, upload ke storage Repliz, lalu jadwalkan |
| `carousel/rehook.py`, `apply_hooks.py` | Ganti sampul/hook di jadwal yang sudah ada |
| `.claude/skills/cinematic-documentary-poster` | Skill Claude Code untuk membuat prompt poster sinematik |

## Persiapan

```bash
pip install -r requirements.txt
npm install            # memasang Playwright
npx playwright install chromium
```

Font yang dipakai: **Inter / Inter Display** (pasang di sistem agar tampilan sama).

Akses Repliz lewat variabel lingkungan. Jangan commit nilainya.

```bash
export REPLIZ_ACCESS_KEY=...   # dari repliz.com/user/setting/api
export REPLIZ_SECRET_KEY=...
export REPLIZ_ACCOUNT_ID=...   # ID akun Instagram di Repliz
```

## Cara pakai

```bash
cd carousel

# Render + upload saja, tanpa menjadwalkan
python3 pipeline.py day01 2026-11-18 "" 0 nosched

# Render + upload + jadwalkan (8 slot per hari: 07, 09, 11, 13, 15, 17, 19, 21 WIB)
# argumen: modul tanggal slot-yang-dilewati nomor-awal
python3 pipeline.py day01 2026-11-18 6 0

# Terapkan hook baru ke jadwal yang masih pending
python3 apply_hooks.py
```

Argumen ketiga adalah indeks slot yang dilewati (mis. `6` melewati 19.00 WIB). Argumen keempat adalah nomor awal carousel, dipakai untuk memilih variasi ilustrasi sampul.

Alur API Repliz yang dipakai: `POST /public/storage/file/init`, `PUT` ke URL presigned, `POST /public/storage/file/{id}/complete`, lalu `POST /public/schedule` dengan `type: "album"`. Jadwal yang masih `pending` bisa diubah lewat `PUT /public/schedule/{id}`.

## Catatan

- Slot waktu ditulis dalam UTC di `pipeline.py` (WIB = UTC+7).
- Instagram bisa membatasi akun baru yang memposting terlalu sering. Mulailah dengan 3–4 posting per hari dan naikkan bertahap.
- Isi carousel ditulis dari pengetahuan umum dan sebaiknya diperiksa ulang sebelum tayang, terutama angka dan tanggal.
- `state.json` dan folder `out/` dibuat saat dijalankan dan tidak di-commit.
