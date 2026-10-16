# Banding karakter: SK_Tuyul_LOD3.fbx vs SK_Jerangkong_LOD3.fbx

**VONIS: GAGAL** — gagal di: cek audit: regangan p99 <= 40.0% di semua pose, profil pose, kuda_kuda: regangan p99 (%), pukul: regangan p99 (%), tendang_tinggi: regangan p99 (%), dodge: regangan p99 (%), jongkok: regangan p99 (%), lari: regangan p99 (%), lompat: regangan p99 (%), tendang_samping: regangan p99 (%), tangkis: regangan p99 (%), putar_badan: regangan p99 (%), lunge: regangan p99 (%), bungkuk: regangan p99 (%), tangan_terangkat: regangan p99 (%), lengan_depan_90: regangan p99 (%), lengan_depan_atas: regangan p99 (%), lengan_samping_90: regangan p99 (%), lengan_guard: regangan p99 (%)

Profil pose: tuyul. Toleransi regangan p99 +3.0 poin persen, IoU badan boleh turun 0.05.

| Ukuran | Lama | Baru | Vonis |
|---|---|---|---|
| cek audit: regangan p99 <= 40.0% di semua pose |  | 165.5% di lengan_depan_atas | GAGAL (audit model baru) |
| profil pose | manny | tuyul | GAGAL (pembanding harus memakai profil pose yang sama) |
| tinggi (m) | 30.6807 | 0.9998 | info |
| tris | 2405 | 6000 | info |
| jumlah tulang | 70 | 52 | info |
| slot material | 1 | 1 | info |
| tepi terbuka (boundary) | 330 | 0 | info |
| IoU badan vs konsep (front) | 0.656 | 0.710 | OK |
| IoU badan vs konsep (side) | 0.426 | 0.460 | OK |
| IoU badan vs konsep (back) | 0.630 | 0.688 | OK |
| kuda_kuda: regangan p99 (%) | 0.0 | 71.6 | GAGAL (+71.6 poin) |
| kuda_kuda: peregangan maks (cm) | 0.0 | 5.81 | PERIKSA upperarm_r (+5.8 cm) |
| pukul: regangan p99 (%) | 0.0 | 97.8 | GAGAL (+97.8 poin) |
| pukul: peregangan maks (cm) | 7.85 | 7.54 | info |
| tendang_tinggi: regangan p99 (%) | 0.0 | 55.1 | GAGAL (+55.1 poin) |
| tendang_tinggi: peregangan maks (cm) | 9.61 | 8.37 | info |
| dodge: regangan p99 (%) | 0.0 | 72.4 | GAGAL (+72.4 poin) |
| dodge: peregangan maks (cm) | 11.34 | 6.86 | info |
| jongkok: regangan p99 (%) | 0.0 | 71.6 | GAGAL (+71.6 poin) |
| jongkok: peregangan maks (cm) | 9.43 | 8.23 | info |
| lari: regangan p99 (%) | 0.0 | 77.9 | GAGAL (+77.9 poin) |
| lari: peregangan maks (cm) | 5.47 | 8.1 | info |
| lompat: regangan p99 (%) | 0.0 | 122.6 | GAGAL (+122.6 poin) |
| lompat: peregangan maks (cm) | 0.0 | 4.57 | PERIKSA neck_02 (+4.6 cm) |
| tendang_samping: regangan p99 (%) | 0.0 | 57.2 | GAGAL (+57.2 poin) |
| tendang_samping: peregangan maks (cm) | 8.33 | 5.24 | info |
| tangkis: regangan p99 (%) | 0.0 | 116.1 | GAGAL (+116.1 poin) |
| tangkis: peregangan maks (cm) | 5.63 | 10.05 | PERIKSA upperarm_r (+4.4 cm) |
| putar_badan: regangan p99 (%) | 0.0 | 71.4 | GAGAL (+71.4 poin) |
| putar_badan: peregangan maks (cm) | 9.48 | 3.35 | info |
| lunge: regangan p99 (%) | 0.0 | 62.3 | GAGAL (+62.3 poin) |
| lunge: peregangan maks (cm) | 6.94 | 5.72 | info |
| bungkuk: regangan p99 (%) | 0.0 | 59.4 | GAGAL (+59.4 poin) |
| bungkuk: peregangan maks (cm) | 15.39 | 3.8 | info |
| tangan_terangkat: regangan p99 (%) | 21.6 | 156.6 | GAGAL (+135.0 poin) |
| tangan_terangkat: peregangan maks (cm) | 62.59 | 6.47 | info |
| lengan_depan_90: regangan p99 (%) | 0.0 | 134.5 | GAGAL (+134.5 poin) |
| lengan_depan_90: peregangan maks (cm) | 0.0 | 5.19 | PERIKSA neck_02 (+5.2 cm) |
| lengan_depan_atas: regangan p99 (%) | 0.0 | 165.5 | GAGAL (+165.5 poin) |
| lengan_depan_atas: peregangan maks (cm) | 0.0 | 7.3 | PERIKSA neck_02 (+7.3 cm) |
| lengan_samping_90: regangan p99 (%) | 0.0 | 83.4 | GAGAL (+83.4 poin) |
| lengan_samping_90: peregangan maks (cm) | 0.0 | 3.43 | PERIKSA neck_02 (+3.4 cm) |
| lengan_guard: regangan p99 (%) | 0.0 | 107.2 | GAGAL (+107.2 poin) |
| lengan_guard: peregangan maks (cm) | 0.0 | 10.28 | PERIKSA upperarm_r (+10.3 cm) |

Gambar: `banding_ortho.png`, `banding_pose.png` (WAJIB dilihat dan dideskripsikan per bagian di laporan).
