# Banding karakter: SK_Tuyul_LOD1.fbx vs SK_Jerangkong_LOD1.fbx

**VONIS: GAGAL** — gagal di: cek audit: regangan p99 <= 40.0% di semua pose, profil pose, kuda_kuda: regangan p99 (%), pukul: regangan p99 (%), tendang_tinggi: regangan p99 (%), dodge: regangan p99 (%), jongkok: regangan p99 (%), lari: regangan p99 (%), lompat: regangan p99 (%), tendang_samping: regangan p99 (%), tangkis: regangan p99 (%), putar_badan: regangan p99 (%), lunge: regangan p99 (%), bungkuk: regangan p99 (%), tangan_terangkat: regangan p99 (%), lengan_depan_90: regangan p99 (%), lengan_depan_atas: regangan p99 (%), lengan_samping_90: regangan p99 (%), lengan_guard: regangan p99 (%)

Profil pose: tuyul. Toleransi regangan p99 +3.0 poin persen, IoU badan boleh turun 0.05.

| Ukuran | Lama | Baru | Vonis |
|---|---|---|---|
| cek audit: regangan p99 <= 40.0% di semua pose |  | 154.8% di lengan_depan_atas | GAGAL (audit model baru) |
| profil pose | manny | tuyul | GAGAL (pembanding harus memakai profil pose yang sama) |
| tinggi (m) | 30.6525 | 1.0 | info |
| tris | 14783 | 30000 | info |
| jumlah tulang | 70 | 52 | info |
| slot material | 1 | 1 | info |
| tepi terbuka (boundary) | 802 | 0 | info |
| IoU badan vs konsep (front) | 0.672 | 0.706 | OK |
| IoU badan vs konsep (side) | 0.479 | 0.457 | OK |
| IoU badan vs konsep (back) | 0.639 | 0.685 | OK |
| kuda_kuda: regangan p99 (%) | 0.0 | 58.7 | GAGAL (+58.7 poin) |
| kuda_kuda: peregangan maks (cm) | 0.0 | 2.17 | info |
| pukul: regangan p99 (%) | 0.0 | 75.5 | GAGAL (+75.5 poin) |
| pukul: peregangan maks (cm) | 16.19 | 2.45 | info |
| tendang_tinggi: regangan p99 (%) | 0.0 | 51.2 | GAGAL (+51.2 poin) |
| tendang_tinggi: peregangan maks (cm) | 7.01 | 4.67 | info |
| dodge: regangan p99 (%) | 0.0 | 58.7 | GAGAL (+58.7 poin) |
| dodge: peregangan maks (cm) | 8.38 | 2.34 | info |
| jongkok: regangan p99 (%) | 0.0 | 75.2 | GAGAL (+75.2 poin) |
| jongkok: peregangan maks (cm) | 7.31 | 4.28 | info |
| lari: regangan p99 (%) | 0.0 | 64.0 | GAGAL (+64.0 poin) |
| lari: peregangan maks (cm) | 8.39 | 3.14 | info |
| lompat: regangan p99 (%) | 0.0 | 83.2 | GAGAL (+83.2 poin) |
| lompat: peregangan maks (cm) | 0.0 | 3.77 | PERIKSA jaw (+3.8 cm) |
| tendang_samping: regangan p99 (%) | 0.0 | 45.7 | GAGAL (+45.7 poin) |
| tendang_samping: peregangan maks (cm) | 16.53 | 2.37 | info |
| tangkis: regangan p99 (%) | 0.0 | 93.1 | GAGAL (+93.1 poin) |
| tangkis: peregangan maks (cm) | 4.21 | 3.34 | info |
| putar_badan: regangan p99 (%) | 0.0 | 55.3 | GAGAL (+55.3 poin) |
| putar_badan: peregangan maks (cm) | 20.01 | 2.05 | info |
| lunge: regangan p99 (%) | 0.0 | 61.2 | GAGAL (+61.2 poin) |
| lunge: peregangan maks (cm) | 5.25 | 3.57 | info |
| bungkuk: regangan p99 (%) | 0.0 | 56.5 | GAGAL (+56.5 poin) |
| bungkuk: peregangan maks (cm) | 12.74 | 2.15 | info |
| tangan_terangkat: regangan p99 (%) | 36.2 | 111.1 | GAGAL (+74.9 poin) |
| tangan_terangkat: peregangan maks (cm) | 76.23 | 4.43 | info |
| lengan_depan_90: regangan p99 (%) | 0.0 | 115.4 | GAGAL (+115.4 poin) |
| lengan_depan_90: peregangan maks (cm) | 0.0 | 4.05 | PERIKSA neck_02 (+4.0 cm) |
| lengan_depan_atas: regangan p99 (%) | 0.0 | 154.8 | GAGAL (+154.8 poin) |
| lengan_depan_atas: peregangan maks (cm) | 0.0 | 5.12 | PERIKSA neck_02 (+5.1 cm) |
| lengan_samping_90: regangan p99 (%) | 0.0 | 59.5 | GAGAL (+59.5 poin) |
| lengan_samping_90: peregangan maks (cm) | 0.0 | 2.71 | info |
| lengan_guard: regangan p99 (%) | 0.0 | 86.8 | GAGAL (+86.8 poin) |
| lengan_guard: peregangan maks (cm) | 0.0 | 3.23 | PERIKSA neck_02 (+3.2 cm) |

Gambar: `banding_ortho.png`, `banding_pose.png` (WAJIB dilihat dan dideskripsikan per bagian di laporan).
