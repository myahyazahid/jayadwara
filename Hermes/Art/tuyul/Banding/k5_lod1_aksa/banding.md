# Banding karakter: SK_Tuyul_LOD1.fbx vs SK_Aksa_LOD1.fbx

**VONIS: GAGAL** — gagal di: cek audit: regangan p99 <= 40.0% di semua pose, profil pose, IoU badan vs konsep (front), IoU badan vs konsep (side), IoU badan vs konsep (back), kuda_kuda: regangan p99 (%), pukul: regangan p99 (%), tendang_tinggi: regangan p99 (%), dodge: regangan p99 (%), jongkok: regangan p99 (%), lari: regangan p99 (%), lompat: regangan p99 (%), tendang_samping: regangan p99 (%), tangkis: regangan p99 (%), putar_badan: regangan p99 (%), lunge: regangan p99 (%), bungkuk: regangan p99 (%), tangan_terangkat: regangan p99 (%), lengan_depan_90: regangan p99 (%), lengan_depan_atas: regangan p99 (%), lengan_samping_90: regangan p99 (%), lengan_guard: regangan p99 (%)

Profil pose: tuyul. Toleransi regangan p99 +3.0 poin persen, IoU badan boleh turun 0.05.

| Ukuran | Lama | Baru | Vonis |
|---|---|---|---|
| cek audit: regangan p99 <= 40.0% di semua pose |  | 154.8% di lengan_depan_atas | GAGAL (audit model baru) |
| profil pose | manny | tuyul | GAGAL (pembanding harus memakai profil pose yang sama) |
| tinggi (m) | 1.8001 | 1.0 | info |
| tris | 23036 | 30000 | info |
| jumlah tulang | 99 | 52 | info |
| slot material | 5 | 1 | info |
| tepi terbuka (boundary) | 4335 | 0 | info |
| IoU badan vs konsep (front) | 0.860 | 0.706 | GAGAL (turun 0.154) |
| IoU badan vs konsep (side) | 0.759 | 0.457 | GAGAL (turun 0.302) |
| IoU badan vs konsep (back) | 0.849 | 0.685 | GAGAL (turun 0.164) |
| kuda_kuda: regangan p99 (%) | 17.9 | 58.7 | GAGAL (+40.8 poin) |
| kuda_kuda: peregangan maks (cm) | 5.2 | 2.17 | info |
| pukul: regangan p99 (%) | 22.2 | 75.5 | GAGAL (+53.3 poin) |
| pukul: peregangan maks (cm) | 4.49 | 2.45 | info |
| tendang_tinggi: regangan p99 (%) | 18.8 | 51.2 | GAGAL (+32.4 poin) |
| tendang_tinggi: peregangan maks (cm) | 11.72 | 4.67 | info |
| dodge: regangan p99 (%) | 20.1 | 58.7 | GAGAL (+38.6 poin) |
| dodge: peregangan maks (cm) | 4.18 | 2.34 | info |
| jongkok: regangan p99 (%) | 25.0 | 75.2 | GAGAL (+50.2 poin) |
| jongkok: peregangan maks (cm) | 12.53 | 4.28 | info |
| lari: regangan p99 (%) | 18.7 | 64.0 | GAGAL (+45.3 poin) |
| lari: peregangan maks (cm) | 8.83 | 3.14 | info |
| lompat: regangan p99 (%) | 27.0 | 83.2 | GAGAL (+56.2 poin) |
| lompat: peregangan maks (cm) | 8.15 | 3.77 | info |
| tendang_samping: regangan p99 (%) | 17.6 | 45.7 | GAGAL (+28.1 poin) |
| tendang_samping: peregangan maks (cm) | 10.6 | 2.37 | info |
| tangkis: regangan p99 (%) | 18.4 | 93.1 | GAGAL (+74.7 poin) |
| tangkis: peregangan maks (cm) | 4.21 | 3.34 | info |
| putar_badan: regangan p99 (%) | 26.5 | 55.3 | GAGAL (+28.8 poin) |
| putar_badan: peregangan maks (cm) | 7.29 | 2.05 | info |
| lunge: regangan p99 (%) | 16.1 | 61.2 | GAGAL (+45.1 poin) |
| lunge: peregangan maks (cm) | 10.16 | 3.57 | info |
| bungkuk: regangan p99 (%) | 23.0 | 56.5 | GAGAL (+33.5 poin) |
| bungkuk: peregangan maks (cm) | 4.85 | 2.15 | info |
| tangan_terangkat: regangan p99 (%) | 27.6 | 111.1 | GAGAL (+83.5 poin) |
| tangan_terangkat: peregangan maks (cm) | 7.87 | 4.43 | info |
| lengan_depan_90: regangan p99 (%) | 16.4 | 115.4 | GAGAL (+99.0 poin) |
| lengan_depan_90: peregangan maks (cm) | 5.25 | 4.05 | info |
| lengan_depan_atas: regangan p99 (%) | 17.9 | 154.8 | GAGAL (+136.9 poin) |
| lengan_depan_atas: peregangan maks (cm) | 6.74 | 5.12 | info |
| lengan_samping_90: regangan p99 (%) | 13.8 | 59.5 | GAGAL (+45.7 poin) |
| lengan_samping_90: peregangan maks (cm) | 1.98 | 2.71 | info |
| lengan_guard: regangan p99 (%) | 15.4 | 86.8 | GAGAL (+71.4 poin) |
| lengan_guard: peregangan maks (cm) | 4.35 | 3.23 | info |

Gambar: `banding_ortho.png`, `banding_pose.png` (WAJIB dilihat dan dideskripsikan per bagian di laporan).
