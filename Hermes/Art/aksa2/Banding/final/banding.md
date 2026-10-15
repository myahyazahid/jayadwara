# Banding karakter: SK_Aksa2.fbx vs SK_Aksa.fbx

**VONIS: GAGAL** — gagal di: cek audit: regangan p99 <= 40.0% di semua pose, kuda_kuda: regangan p99 (%), pukul: regangan p99 (%), tendang_tinggi: regangan p99 (%), dodge: regangan p99 (%), jongkok: regangan p99 (%), lari: regangan p99 (%), lompat: regangan p99 (%), tendang_samping: regangan p99 (%), tangkis: regangan p99 (%), putar_badan: regangan p99 (%), lunge: regangan p99 (%), bungkuk: regangan p99 (%), tangan_terangkat: regangan p99 (%), lengan_depan_90: regangan p99 (%), lengan_depan_atas: regangan p99 (%), lengan_samping_90: regangan p99 (%), lengan_guard: regangan p99 (%)

Profil pose: manny. Toleransi regangan p99 +5.0 poin persen, IoU badan boleh turun 0.05.

| Ukuran | Lama | Baru | Vonis |
|---|---|---|---|
| cek audit: regangan p99 <= 40.0% di semua pose |  | 103.8% di tangan_terangkat | GAGAL (audit model baru) |
| tinggi (m) | 1.8008 | 1.806 | info |
| tris | 52152 | 38786 | info |
| jumlah tulang | 99 | 89 | info |
| slot material | 5 | 1 | info |
| tepi terbuka (boundary) | 10844 | 3 | info |
| IoU badan vs konsep (front) | 0.860 | 0.881 | OK |
| IoU badan vs konsep (side) | 0.759 | 0.791 | OK |
| IoU badan vs konsep (back) | 0.848 | 0.877 | OK |
| kuda_kuda: regangan p99 (%) | 19.9 | 68.4 | GAGAL (+48.5 poin) |
| kuda_kuda: peregangan maks (cm) | 2.96 | 5.96 | info |
| pukul: regangan p99 (%) | 22.6 | 73.2 | GAGAL (+50.6 poin) |
| pukul: peregangan maks (cm) | 4.67 | 8.42 | PERIKSA upperarm_twist_01_r (+3.8 cm) |
| tendang_tinggi: regangan p99 (%) | 19.8 | 76.3 | GAGAL (+56.5 poin) |
| tendang_tinggi: peregangan maks (cm) | 9.03 | 6.59 | info |
| dodge: regangan p99 (%) | 21.7 | 55.2 | GAGAL (+33.5 poin) |
| dodge: peregangan maks (cm) | 3.03 | 4.16 | info |
| jongkok: regangan p99 (%) | 26.7 | 88.6 | GAGAL (+61.9 poin) |
| jongkok: peregangan maks (cm) | 6.56 | 4.77 | info |
| lari: regangan p99 (%) | 21.2 | 66.6 | GAGAL (+45.4 poin) |
| lari: peregangan maks (cm) | 4.42 | 5.96 | info |
| lompat: regangan p99 (%) | 28.2 | 96.3 | GAGAL (+68.1 poin) |
| lompat: peregangan maks (cm) | 5.18 | 11.42 | PERIKSA upperarm_twist_01_r (+6.2 cm) |
| tendang_samping: regangan p99 (%) | 19.2 | 68.9 | GAGAL (+49.7 poin) |
| tendang_samping: peregangan maks (cm) | 5.86 | 6.91 | info |
| tangkis: regangan p99 (%) | 20.7 | 66.0 | GAGAL (+45.3 poin) |
| tangkis: peregangan maks (cm) | 3.61 | 8.19 | PERIKSA upperarm_twist_01_r (+4.6 cm) |
| putar_badan: regangan p99 (%) | 27.0 | 62.8 | GAGAL (+35.8 poin) |
| putar_badan: peregangan maks (cm) | 5.81 | 5.0 | info |
| lunge: regangan p99 (%) | 18.8 | 58.2 | GAGAL (+39.4 poin) |
| lunge: peregangan maks (cm) | 5.8 | 4.52 | info |
| bungkuk: regangan p99 (%) | 23.1 | 44.6 | GAGAL (+21.5 poin) |
| bungkuk: peregangan maks (cm) | 4.02 | 3.92 | info |
| tangan_terangkat: regangan p99 (%) | 29.8 | 103.8 | GAGAL (+74.0 poin) |
| tangan_terangkat: peregangan maks (cm) | 7.78 | 14.26 | PERIKSA upperarm_twist_01_r (+6.5 cm) |
| lengan_depan_90: regangan p99 (%) | 17.3 | 79.6 | GAGAL (+62.3 poin) |
| lengan_depan_90: peregangan maks (cm) | 5.43 | 9.23 | PERIKSA upperarm_twist_01_r (+3.8 cm) |
| lengan_depan_atas: regangan p99 (%) | 20.6 | 95.0 | GAGAL (+74.4 poin) |
| lengan_depan_atas: peregangan maks (cm) | 6.96 | 12.87 | PERIKSA upperarm_twist_01_r (+5.9 cm) |
| lengan_samping_90: regangan p99 (%) | 13.2 | 43.0 | GAGAL (+29.8 poin) |
| lengan_samping_90: peregangan maks (cm) | 1.79 | 6.25 | PERIKSA upperarm_twist_01_r (+4.5 cm) |
| lengan_guard: regangan p99 (%) | 17.5 | 59.9 | GAGAL (+42.4 poin) |
| lengan_guard: peregangan maks (cm) | 3.15 | 7.05 | PERIKSA upperarm_twist_01_r (+3.9 cm) |

Gambar: `banding_ortho.png`, `banding_pose.png` (WAJIB dilihat dan dideskripsikan per bagian di laporan).
