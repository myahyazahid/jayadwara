# Banding karakter: SK_Aksa2_LOD3.fbx vs SK_Aksa_LOD3.fbx

**VONIS: GAGAL** — gagal di: cek audit: regangan p99 <= 40.0% di semua pose, kuda_kuda: regangan p99 (%), pukul: regangan p99 (%), tendang_tinggi: regangan p99 (%), dodge: regangan p99 (%), jongkok: regangan p99 (%), lari: regangan p99 (%), lompat: regangan p99 (%), tendang_samping: regangan p99 (%), tangkis: regangan p99 (%), putar_badan: regangan p99 (%), lunge: regangan p99 (%), bungkuk: regangan p99 (%), tangan_terangkat: regangan p99 (%), lengan_depan_90: regangan p99 (%), lengan_depan_atas: regangan p99 (%), lengan_samping_90: regangan p99 (%), lengan_guard: regangan p99 (%)

Profil pose: manny. Toleransi regangan p99 +5.0 poin persen, IoU badan boleh turun 0.05.

| Ukuran | Lama | Baru | Vonis |
|---|---|---|---|
| cek audit: regangan p99 <= 40.0% di semua pose |  | 108.1% di tangan_terangkat | GAGAL (audit model baru) |
| tinggi (m) | 1.7914 | 1.7977 | info |
| tris | 3067 | 3489 | info |
| jumlah tulang | 99 | 89 | info |
| slot material | 5 | 1 | info |
| tepi terbuka (boundary) | 469 | 5 | info |
| IoU badan vs konsep (front) | 0.855 | 0.880 | OK |
| IoU badan vs konsep (side) | 0.764 | 0.792 | OK |
| IoU badan vs konsep (back) | 0.847 | 0.878 | OK |
| kuda_kuda: regangan p99 (%) | 16.5 | 58.6 | GAGAL (+42.1 poin) |
| kuda_kuda: peregangan maks (cm) | 7.06 | 9.29 | info |
| pukul: regangan p99 (%) | 19.0 | 57.0 | GAGAL (+38.0 poin) |
| pukul: peregangan maks (cm) | 7.76 | 12.76 | PERIKSA upperarm_twist_01_r (+5.0 cm) |
| tendang_tinggi: regangan p99 (%) | 15.3 | 59.2 | GAGAL (+43.9 poin) |
| tendang_tinggi: peregangan maks (cm) | 12.63 | 8.86 | info |
| dodge: regangan p99 (%) | 14.2 | 42.0 | GAGAL (+27.8 poin) |
| dodge: peregangan maks (cm) | 7.27 | 6.84 | info |
| jongkok: regangan p99 (%) | 18.6 | 62.5 | GAGAL (+43.9 poin) |
| jongkok: peregangan maks (cm) | 31.93 | 7.67 | info |
| lari: regangan p99 (%) | 16.3 | 53.0 | GAGAL (+36.7 poin) |
| lari: peregangan maks (cm) | 14.62 | 9.12 | info |
| lompat: regangan p99 (%) | 19.5 | 93.3 | GAGAL (+73.8 poin) |
| lompat: peregangan maks (cm) | 11.86 | 17.08 | PERIKSA upperarm_twist_01_r (+5.2 cm) |
| tendang_samping: regangan p99 (%) | 11.4 | 57.5 | GAGAL (+46.1 poin) |
| tendang_samping: peregangan maks (cm) | 12.11 | 10.3 | info |
| tangkis: regangan p99 (%) | 17.4 | 58.4 | GAGAL (+41.0 poin) |
| tangkis: peregangan maks (cm) | 6.43 | 12.25 | PERIKSA clavicle_r (+5.8 cm) |
| putar_badan: regangan p99 (%) | 19.0 | 46.5 | GAGAL (+27.5 poin) |
| putar_badan: peregangan maks (cm) | 9.32 | 5.72 | info |
| lunge: regangan p99 (%) | 13.0 | 44.2 | GAGAL (+31.2 poin) |
| lunge: peregangan maks (cm) | 18.42 | 7.87 | info |
| bungkuk: regangan p99 (%) | 16.4 | 36.4 | GAGAL (+20.0 poin) |
| bungkuk: peregangan maks (cm) | 9.43 | 4.39 | info |
| tangan_terangkat: regangan p99 (%) | 24.3 | 108.1 | GAGAL (+83.8 poin) |
| tangan_terangkat: peregangan maks (cm) | 7.25 | 21.46 | PERIKSA upperarm_twist_01_r (+14.2 cm) |
| lengan_depan_90: regangan p99 (%) | 11.9 | 70.2 | GAGAL (+58.3 poin) |
| lengan_depan_90: peregangan maks (cm) | 3.87 | 13.32 | PERIKSA clavicle_r (+9.4 cm) |
| lengan_depan_atas: regangan p99 (%) | 14.7 | 90.0 | GAGAL (+75.3 poin) |
| lengan_depan_atas: peregangan maks (cm) | 6.41 | 18.81 | PERIKSA upperarm_twist_01_r (+12.4 cm) |
| lengan_samping_90: regangan p99 (%) | 11.7 | 47.8 | GAGAL (+36.1 poin) |
| lengan_samping_90: peregangan maks (cm) | 4.51 | 9.32 | PERIKSA upperarm_twist_01_r (+4.8 cm) |
| lengan_guard: regangan p99 (%) | 12.8 | 52.3 | GAGAL (+39.5 poin) |
| lengan_guard: peregangan maks (cm) | 5.22 | 10.84 | PERIKSA clavicle_r (+5.6 cm) |

Gambar: `banding_ortho.png`, `banding_pose.png` (WAJIB dilihat dan dideskripsikan per bagian di laporan).
