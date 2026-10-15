# Banding karakter: SK_Aksa2_LOD1.fbx vs SK_Aksa_LOD1.fbx

**VONIS: GAGAL** — gagal di: cek audit: regangan p99 <= 40.0% di semua pose, kuda_kuda: regangan p99 (%), pukul: regangan p99 (%), tendang_tinggi: regangan p99 (%), dodge: regangan p99 (%), jongkok: regangan p99 (%), lari: regangan p99 (%), lompat: regangan p99 (%), tendang_samping: regangan p99 (%), tangkis: regangan p99 (%), putar_badan: regangan p99 (%), lunge: regangan p99 (%), bungkuk: regangan p99 (%), tangan_terangkat: regangan p99 (%), lengan_depan_90: regangan p99 (%), lengan_depan_atas: regangan p99 (%), lengan_samping_90: regangan p99 (%), lengan_guard: regangan p99 (%)

Profil pose: manny. Toleransi regangan p99 +5.0 poin persen, IoU badan boleh turun 0.05.

| Ukuran | Lama | Baru | Vonis |
|---|---|---|---|
| cek audit: regangan p99 <= 40.0% di semua pose |  | 90.8% di tangan_terangkat | GAGAL (audit model baru) |
| tinggi (m) | 1.8001 | 1.8066 | info |
| tris | 23036 | 21331 | info |
| jumlah tulang | 99 | 89 | info |
| slot material | 5 | 1 | info |
| tepi terbuka (boundary) | 4335 | 5 | info |
| IoU badan vs konsep (front) | 0.860 | 0.881 | OK |
| IoU badan vs konsep (side) | 0.759 | 0.791 | OK |
| IoU badan vs konsep (back) | 0.849 | 0.877 | OK |
| kuda_kuda: regangan p99 (%) | 17.9 | 57.7 | GAGAL (+39.8 poin) |
| kuda_kuda: peregangan maks (cm) | 5.2 | 8.32 | PERIKSA clavicle_r (+3.1 cm) |
| pukul: regangan p99 (%) | 22.2 | 56.2 | GAGAL (+34.0 poin) |
| pukul: peregangan maks (cm) | 4.49 | 11.35 | PERIKSA clavicle_r (+6.9 cm) |
| tendang_tinggi: regangan p99 (%) | 18.8 | 60.7 | GAGAL (+41.9 poin) |
| tendang_tinggi: peregangan maks (cm) | 11.72 | 7.13 | info |
| dodge: regangan p99 (%) | 20.1 | 45.9 | GAGAL (+25.8 poin) |
| dodge: peregangan maks (cm) | 4.18 | 6.12 | info |
| jongkok: regangan p99 (%) | 25.0 | 70.0 | GAGAL (+45.0 poin) |
| jongkok: peregangan maks (cm) | 12.53 | 6.87 | info |
| lari: regangan p99 (%) | 18.7 | 55.0 | GAGAL (+36.3 poin) |
| lari: peregangan maks (cm) | 8.83 | 8.2 | info |
| lompat: regangan p99 (%) | 27.0 | 83.8 | GAGAL (+56.8 poin) |
| lompat: peregangan maks (cm) | 8.15 | 14.64 | PERIKSA upperarm_twist_01_r (+6.5 cm) |
| tendang_samping: regangan p99 (%) | 17.6 | 53.2 | GAGAL (+35.6 poin) |
| tendang_samping: peregangan maks (cm) | 10.6 | 8.75 | info |
| tangkis: regangan p99 (%) | 18.4 | 55.8 | GAGAL (+37.4 poin) |
| tangkis: peregangan maks (cm) | 4.21 | 10.97 | PERIKSA clavicle_r (+6.8 cm) |
| putar_badan: regangan p99 (%) | 26.5 | 52.1 | GAGAL (+25.6 poin) |
| putar_badan: peregangan maks (cm) | 7.29 | 5.19 | info |
| lunge: regangan p99 (%) | 16.1 | 49.4 | GAGAL (+33.3 poin) |
| lunge: peregangan maks (cm) | 10.16 | 6.73 | info |
| bungkuk: regangan p99 (%) | 23.0 | 39.8 | GAGAL (+16.8 poin) |
| bungkuk: peregangan maks (cm) | 4.85 | 3.32 | info |
| tangan_terangkat: regangan p99 (%) | 27.6 | 90.8 | GAGAL (+63.2 poin) |
| tangan_terangkat: peregangan maks (cm) | 7.87 | 18.13 | PERIKSA upperarm_twist_01_r (+10.3 cm) |
| lengan_depan_90: regangan p99 (%) | 16.4 | 69.9 | GAGAL (+53.5 poin) |
| lengan_depan_90: peregangan maks (cm) | 5.25 | 12.2 | PERIKSA upperarm_twist_01_r (+6.9 cm) |
| lengan_depan_atas: regangan p99 (%) | 17.9 | 80.8 | GAGAL (+62.9 poin) |
| lengan_depan_atas: peregangan maks (cm) | 6.74 | 16.73 | PERIKSA upperarm_twist_01_r (+10.0 cm) |
| lengan_samping_90: regangan p99 (%) | 13.8 | 41.4 | GAGAL (+27.6 poin) |
| lengan_samping_90: peregangan maks (cm) | 1.98 | 7.89 | PERIKSA upperarm_twist_01_r (+5.9 cm) |
| lengan_guard: regangan p99 (%) | 15.4 | 51.6 | GAGAL (+36.2 poin) |
| lengan_guard: peregangan maks (cm) | 4.35 | 9.45 | PERIKSA upperarm_twist_01_r (+5.1 cm) |

Gambar: `banding_ortho.png`, `banding_pose.png` (WAJIB dilihat dan dideskripsikan per bagian di laporan).
