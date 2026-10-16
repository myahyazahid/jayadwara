# Banding karakter: SK_Tuyul_LOD3.fbx vs SK_Aksa_LOD3.fbx

**VONIS: GAGAL** — gagal di: cek audit: regangan p99 <= 40.0% di semua pose, profil pose, IoU badan vs konsep (front), IoU badan vs konsep (side), IoU badan vs konsep (back), kuda_kuda: regangan p99 (%), pukul: regangan p99 (%), tendang_tinggi: regangan p99 (%), dodge: regangan p99 (%), jongkok: regangan p99 (%), lari: regangan p99 (%), lompat: regangan p99 (%), tendang_samping: regangan p99 (%), tangkis: regangan p99 (%), putar_badan: regangan p99 (%), lunge: regangan p99 (%), bungkuk: regangan p99 (%), tangan_terangkat: regangan p99 (%), lengan_depan_90: regangan p99 (%), lengan_depan_atas: regangan p99 (%), lengan_samping_90: regangan p99 (%), lengan_guard: regangan p99 (%)

Profil pose: tuyul. Toleransi regangan p99 +3.0 poin persen, IoU badan boleh turun 0.05.

| Ukuran | Lama | Baru | Vonis |
|---|---|---|---|
| cek audit: regangan p99 <= 40.0% di semua pose |  | 165.5% di lengan_depan_atas | GAGAL (audit model baru) |
| profil pose | manny | tuyul | GAGAL (pembanding harus memakai profil pose yang sama) |
| tinggi (m) | 1.7914 | 0.9998 | info |
| tris | 3067 | 6000 | info |
| jumlah tulang | 99 | 52 | info |
| slot material | 5 | 1 | info |
| tepi terbuka (boundary) | 469 | 0 | info |
| IoU badan vs konsep (front) | 0.854 | 0.710 | GAGAL (turun 0.143) |
| IoU badan vs konsep (side) | 0.764 | 0.460 | GAGAL (turun 0.305) |
| IoU badan vs konsep (back) | 0.845 | 0.688 | GAGAL (turun 0.157) |
| kuda_kuda: regangan p99 (%) | 16.5 | 71.6 | GAGAL (+55.1 poin) |
| kuda_kuda: peregangan maks (cm) | 7.06 | 5.81 | info |
| pukul: regangan p99 (%) | 19.0 | 97.8 | GAGAL (+78.8 poin) |
| pukul: peregangan maks (cm) | 7.76 | 7.54 | info |
| tendang_tinggi: regangan p99 (%) | 15.3 | 55.1 | GAGAL (+39.8 poin) |
| tendang_tinggi: peregangan maks (cm) | 12.63 | 8.37 | info |
| dodge: regangan p99 (%) | 14.2 | 72.4 | GAGAL (+58.2 poin) |
| dodge: peregangan maks (cm) | 7.27 | 6.86 | info |
| jongkok: regangan p99 (%) | 18.6 | 71.6 | GAGAL (+53.0 poin) |
| jongkok: peregangan maks (cm) | 31.93 | 8.23 | info |
| lari: regangan p99 (%) | 16.3 | 77.9 | GAGAL (+61.6 poin) |
| lari: peregangan maks (cm) | 14.62 | 8.1 | info |
| lompat: regangan p99 (%) | 19.5 | 122.6 | GAGAL (+103.1 poin) |
| lompat: peregangan maks (cm) | 11.86 | 4.57 | info |
| tendang_samping: regangan p99 (%) | 11.4 | 57.2 | GAGAL (+45.8 poin) |
| tendang_samping: peregangan maks (cm) | 12.11 | 5.24 | info |
| tangkis: regangan p99 (%) | 17.4 | 116.1 | GAGAL (+98.7 poin) |
| tangkis: peregangan maks (cm) | 6.43 | 10.05 | PERIKSA upperarm_r (+3.6 cm) |
| putar_badan: regangan p99 (%) | 19.0 | 71.4 | GAGAL (+52.4 poin) |
| putar_badan: peregangan maks (cm) | 9.32 | 3.35 | info |
| lunge: regangan p99 (%) | 13.0 | 62.3 | GAGAL (+49.3 poin) |
| lunge: peregangan maks (cm) | 18.42 | 5.72 | info |
| bungkuk: regangan p99 (%) | 16.4 | 59.4 | GAGAL (+43.0 poin) |
| bungkuk: peregangan maks (cm) | 9.43 | 3.8 | info |
| tangan_terangkat: regangan p99 (%) | 24.3 | 156.6 | GAGAL (+132.3 poin) |
| tangan_terangkat: peregangan maks (cm) | 7.25 | 6.47 | info |
| lengan_depan_90: regangan p99 (%) | 11.9 | 134.5 | GAGAL (+122.6 poin) |
| lengan_depan_90: peregangan maks (cm) | 3.87 | 5.19 | info |
| lengan_depan_atas: regangan p99 (%) | 14.7 | 165.5 | GAGAL (+150.8 poin) |
| lengan_depan_atas: peregangan maks (cm) | 6.41 | 7.3 | info |
| lengan_samping_90: regangan p99 (%) | 11.7 | 83.4 | GAGAL (+71.7 poin) |
| lengan_samping_90: peregangan maks (cm) | 4.51 | 3.43 | info |
| lengan_guard: regangan p99 (%) | 12.8 | 107.2 | GAGAL (+94.4 poin) |
| lengan_guard: peregangan maks (cm) | 5.22 | 10.28 | PERIKSA upperarm_r (+5.1 cm) |

Gambar: `banding_ortho.png`, `banding_pose.png` (WAJIB dilihat dan dideskripsikan per bagian di laporan).
