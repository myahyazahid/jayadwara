# Banding karakter: SK_Tuyul_LOD2.fbx vs SK_Aksa_LOD2.fbx

**VONIS: GAGAL** — gagal di: cek audit: regangan p99 <= 40.0% di semua pose, profil pose, IoU badan vs konsep (front), IoU badan vs konsep (side), IoU badan vs konsep (back), kuda_kuda: regangan p99 (%), pukul: regangan p99 (%), tendang_tinggi: regangan p99 (%), dodge: regangan p99 (%), jongkok: regangan p99 (%), lari: regangan p99 (%), lompat: regangan p99 (%), tendang_samping: regangan p99 (%), tangkis: regangan p99 (%), putar_badan: regangan p99 (%), lunge: regangan p99 (%), bungkuk: regangan p99 (%), tangan_terangkat: regangan p99 (%), lengan_depan_90: regangan p99 (%), lengan_depan_atas: regangan p99 (%), lengan_samping_90: regangan p99 (%), lengan_guard: regangan p99 (%)

Profil pose: tuyul. Toleransi regangan p99 +3.0 poin persen, IoU badan boleh turun 0.05.

| Ukuran | Lama | Baru | Vonis |
|---|---|---|---|
| cek audit: regangan p99 <= 40.0% di semua pose |  | 137.4% di lengan_depan_atas | GAGAL (audit model baru) |
| profil pose | manny | tuyul | GAGAL (pembanding harus memakai profil pose yang sama) |
| tinggi (m) | 1.7925 | 1.0 | info |
| tris | 8198 | 14000 | info |
| jumlah tulang | 99 | 52 | info |
| slot material | 5 | 1 | info |
| tepi terbuka (boundary) | 600 | 0 | info |
| IoU badan vs konsep (front) | 0.858 | 0.707 | GAGAL (turun 0.151) |
| IoU badan vs konsep (side) | 0.755 | 0.458 | GAGAL (turun 0.296) |
| IoU badan vs konsep (back) | 0.848 | 0.686 | GAGAL (turun 0.162) |
| kuda_kuda: regangan p99 (%) | 17.7 | 53.6 | GAGAL (+35.9 poin) |
| kuda_kuda: peregangan maks (cm) | 7.84 | 2.99 | info |
| pukul: regangan p99 (%) | 23.8 | 72.9 | GAGAL (+49.1 poin) |
| pukul: peregangan maks (cm) | 4.51 | 3.85 | info |
| tendang_tinggi: regangan p99 (%) | 19.7 | 49.5 | GAGAL (+29.8 poin) |
| tendang_tinggi: peregangan maks (cm) | 10.03 | 6.19 | info |
| dodge: regangan p99 (%) | 20.1 | 56.9 | GAGAL (+36.8 poin) |
| dodge: peregangan maks (cm) | 4.52 | 3.27 | info |
| jongkok: regangan p99 (%) | 24.8 | 67.0 | GAGAL (+42.2 poin) |
| jongkok: peregangan maks (cm) | 16.46 | 5.79 | info |
| lari: regangan p99 (%) | 19.3 | 62.3 | GAGAL (+43.0 poin) |
| lari: peregangan maks (cm) | 10.05 | 3.64 | info |
| lompat: regangan p99 (%) | 25.9 | 90.3 | GAGAL (+64.4 poin) |
| lompat: peregangan maks (cm) | 9.43 | 4.25 | info |
| tendang_samping: regangan p99 (%) | 16.5 | 47.5 | GAGAL (+31.0 poin) |
| tendang_samping: peregangan maks (cm) | 10.56 | 3.57 | info |
| tangkis: regangan p99 (%) | 18.0 | 86.2 | GAGAL (+68.2 poin) |
| tangkis: peregangan maks (cm) | 4.42 | 4.88 | info |
| putar_badan: regangan p99 (%) | 28.1 | 54.5 | GAGAL (+26.4 poin) |
| putar_badan: peregangan maks (cm) | 8.31 | 2.66 | info |
| lunge: regangan p99 (%) | 16.5 | 53.8 | GAGAL (+37.3 poin) |
| lunge: peregangan maks (cm) | 11.1 | 4.27 | info |
| bungkuk: regangan p99 (%) | 20.6 | 52.2 | GAGAL (+31.6 poin) |
| bungkuk: peregangan maks (cm) | 6.74 | 2.86 | info |
| tangan_terangkat: regangan p99 (%) | 25.9 | 124.8 | GAGAL (+98.9 poin) |
| tangan_terangkat: peregangan maks (cm) | 6.47 | 5.39 | info |
| lengan_depan_90: regangan p99 (%) | 14.9 | 106.0 | GAGAL (+91.1 poin) |
| lengan_depan_90: peregangan maks (cm) | 3.71 | 5.77 | info |
| lengan_depan_atas: regangan p99 (%) | 17.9 | 137.4 | GAGAL (+119.5 poin) |
| lengan_depan_atas: peregangan maks (cm) | 5.95 | 8.0 | info |
| lengan_samping_90: regangan p99 (%) | 13.4 | 64.8 | GAGAL (+51.4 poin) |
| lengan_samping_90: peregangan maks (cm) | 3.16 | 3.1 | info |
| lengan_guard: regangan p99 (%) | 15.1 | 79.8 | GAGAL (+64.7 poin) |
| lengan_guard: peregangan maks (cm) | 4.36 | 5.06 | info |

Gambar: `banding_ortho.png`, `banding_pose.png` (WAJIB dilihat dan dideskripsikan per bagian di laporan).
