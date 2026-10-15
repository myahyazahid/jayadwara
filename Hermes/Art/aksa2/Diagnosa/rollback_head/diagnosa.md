# Diagnosa SK_Aksa2.fbx — wilayah head, neck_01, spine_05 (radius 0.120 m, 2144 vertex)

## Dugaan penyebab (urut)

1. **MELAR** (skor 50) — p99 46.7% di tangan_terangkat, maks 2.47 cm di ((0.09, -0.044, 1.398), 'clavicle_l') → resep **F5**
2. **NORMAL TERBALIK? (ulangi dengan --pembanding)** (skor 30) — 16.1% muka menghadap ke dalam → resep **F7**

## Angka

| Ukuran | Nilai |
|---|---|
| lubang | {"loop_akibat_bobot_atau_jahitan": 0, "loop": 1, "loop_besar_>=6": 0, "vertex_tepi": 2, "melebar_maks_x": 1.09} |
| jahitan_terbelah | {"pasangan_kembar": 0, "bobot_beda": 0} |
| bobot_jauh | {"vertex": 0, "per_tulang": []} |
| bobot_tajam | {"tepi": 0, "per_tulang": []} |
| bobot_rusak | {"tanpa_bobot": 0, "lebih_4_influence": 0, "tidak_normal": 0} |
| normal_terbalik | {"muka": 650, "dari": 4042, "persen": 16.1} |

## Loop tepi terbuka di wilayah (terbesar dulu)

Loop yang juga ada di model sehat = tepi baju/kerah/kantong yang disengaja: JANGAN ditutup. Kandidat F1 = 'tidak' di kolom terakhir DAN bertanda merah di tempat yang dikeluhkan.

| # | vertex tepi | pusat (m) | tulang dominan | ukuran rest (cm) | akibat bobot/jahitan | ada di model sehat? |
|---|---|---|---|---|---|---|
| 1 | 2 | (0.052, -0.041, 1.669) | head | 0.5 | tidak | ? (pakai --pembanding) |

Pose terburuk: **tangan_terangkat**

| Pose | regangan p99 % | maks cm | lokasi maks | lubang melebar x | jahitan terpisah cm | tembus baru |
|---|---|---|---|---|---|---|
| kuda_kuda | 10.2 | 0.8 | ((0.099, -0.059, 1.377), 'clavicle_l') | 1.0 | 0.0 | 1 |
| pukul | 12.4 | 1.2 | ((0.099, -0.059, 1.377), 'clavicle_l') | 1.0 | 0.0 | 1 |
| tendang_tinggi | 14.2 | 0.79 | ((-0.097, -0.055, 1.375), 'clavicle_r') | 0.78 | 0.0 | 0 |
| dodge | 13.3 | 0.59 | ((-0.101, -0.058, 1.372), 'clavicle_r') | 1.04 | 0.0 | 0 |
| jongkok | 8.1 | 0.66 | ((-0.101, -0.058, 1.372), 'clavicle_r') | 1.09 | 0.0 | 0 |
| lari | 8.9 | 0.89 | ((-0.101, -0.058, 1.372), 'clavicle_r') | 1.03 | 0.0 | 2 |
| lompat | 31.6 | 1.67 | ((0.099, -0.059, 1.377), 'clavicle_l') | 1.0 | 0.0 | 5 |
| tendang_samping | 16.3 | 0.67 | ((-0.097, -0.055, 1.375), 'clavicle_r') | 0.98 | 0.0 | 5 |
| tangkis | 13.9 | 1.03 | ((0.099, -0.059, 1.377), 'clavicle_l') | 1.05 | 0.0 | 2 |
| putar_badan | 29.8 | 0.75 | ((0.073, 0.091, 1.584), 'head') | 1.0 | 0.0 | 3 |
| lunge | 4.9 | 0.72 | ((0.099, -0.059, 1.377), 'clavicle_l') | 1.06 | 0.0 | 0 |
| bungkuk | 24.0 | 0.73 | ((-0.022, 0.122, 1.601), 'head') | 0.98 | 0.0 | 0 |
| tangan_terangkat | 46.7 | 2.47 | ((0.09, -0.044, 1.398), 'clavicle_l') | 1.0 | 0.0 | 0 |
| lengan_depan_90 | 21.9 | 1.02 | ((0.099, -0.059, 1.377), 'clavicle_l') | 1.0 | 0.0 | 9 |
| lengan_depan_atas | 14.4 | 0.41 | ((0.124, -0.048, 1.389), 'clavicle_l') | 1.0 | 0.0 | 4 |
| lengan_samping_90 | 18.2 | 0.85 | ((0.099, -0.056, 1.383), 'clavicle_l') | 1.0 | 0.0 | 5 |
| lengan_guard | 13.8 | 0.57 | ((0.099, -0.059, 1.377), 'clavicle_l') | 1.0 | 0.0 | 4 |

Gambar: `diagnosa_sheet.png` (WAJIB dilihat: apakah warna penanda ada di tempat yang dikeluhkan?).
