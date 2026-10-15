# Diagnosa SK_Aksa.fbx — wilayah upperarm_r, clavicle_r (radius 0.120 m, 3282 vertex)

## Dugaan penyebab (urut)

1. **LUBANG? (tepi baju juga melebar; ulangi dengan --pembanding)** (skor 60) — 3 loop tepi terbuka (di luar akibat bobot/jahitan), melebar x1.31 → resep **F1**
2. **TEMBUS? (ulangi dengan --pembanding)** (skor 35) — 2532 pasangan segitiga baru menembus di tangan_terangkat; lipatan sendi pada pose dalam wajar menembus sedikit → resep **F6**
3. **NORMAL TERBALIK? (ulangi dengan --pembanding)** (skor 30) — 32.1% muka menghadap ke dalam → resep **F7**

## Angka

| Ukuran | Nilai |
|---|---|
| lubang | {"loop_akibat_bobot_atau_jahitan": 0, "loop": 3, "loop_besar_>=6": 3, "vertex_tepi": 244, "melebar_maks_x": 1.31} |
| jahitan_terbelah | {"pasangan_kembar": 36, "bobot_beda": 14} |
| bobot_jauh | {"vertex": 0, "per_tulang": []} |
| bobot_tajam | {"tepi": 0, "per_tulang": []} |
| bobot_rusak | {"tanpa_bobot": 0, "lebih_4_influence": 0, "tidak_normal": 0} |
| normal_terbalik | {"muka": 1869, "dari": 5817, "persen": 32.1} |

## Loop tepi terbuka di wilayah (terbesar dulu)

Loop yang juga ada di model sehat = tepi baju/kerah/kantong yang disengaja: JANGAN ditutup. Kandidat F1 = 'tidak' di kolom terakhir DAN bertanda merah di tempat yang dikeluhkan.

| # | vertex tepi | pusat (m) | tulang dominan | ukuran rest (cm) | akibat bobot/jahitan | ada di model sehat? |
|---|---|---|---|---|---|---|
| 1 | 110 | (0.0, 0.033, 1.547) | neck_01 | 21.5 | tidak | ? (pakai --pembanding) |
| 2 | 94 | (0.0, 0.001, 1.492) | spine_05 | 13.6 | tidak | ? (pakai --pembanding) |
| 3 | 40 | (0.0, 0.009, 1.519) | spine_05 | 13.2 | tidak | ? (pakai --pembanding) |

Pose terburuk: **tangan_terangkat**

| Pose | regangan p99 % | maks cm | lokasi maks | lubang melebar x | jahitan terpisah cm | tembus baru |
|---|---|---|---|---|---|---|
| kuda_kuda | 25.8 | 2.13 | ((-0.192, 0.06, 1.375), 'upperarm_r') | 1.0 | 0.02 | 1606 |
| pukul | 27.2 | 4.67 | ((-0.192, 0.06, 1.375), 'upperarm_r') | 1.31 | 0.02 | 1385 |
| tendang_tinggi | 21.3 | 2.45 | ((-0.206, 0.084, 1.424), 'upperarm_r') | 1.13 | 0.02 | 1238 |
| dodge | 24.7 | 1.6 | ((-0.363, -0.012, 1.257), 'upperarm_twist_02_r') | 1.16 | 0.03 | 2164 |
| jongkok | 15.1 | 1.52 | ((-0.192, 0.06, 1.375), 'upperarm_r') | 1.1 | 0.02 | 1421 |
| lari | 27.9 | 1.91 | ((-0.351, -0.023, 1.25), 'upperarm_twist_02_r') | 1.17 | 0.02 | 1715 |
| lompat | 41.9 | 5.17 | ((-0.281, -0.072, 1.215), 'upperarm_r') | 1.0 | 0.02 | 1021 |
| tendang_samping | 23.1 | 2.02 | ((-0.225, 0.024, 1.486), 'clavicle_r') | 1.14 | 0.02 | 1191 |
| tangkis | 33.0 | 3.61 | ((-0.229, 0.09, 1.423), 'upperarm_r') | 1.02 | 0.02 | 1956 |
| putar_badan | 38.3 | 0.78 | ((0.005, 0.12, 1.493), 'clavicle_l') | 1.28 | 0.21 | 2028 |
| lunge | 0.0 | 0.03 | ((0.072, -0.001, 1.493), 'clavicle_l') | 1.03 | 0.02 | 576 |
| bungkuk | 37.4 | 0.94 | ((-0.138, 0.076, 1.2), 'spine_03') | 1.11 | 0.06 | 1940 |
| tangan_terangkat | 62.4 | 7.77 | ((-0.281, -0.072, 1.215), 'upperarm_r') | 1.0 | 0.25 | 2532 |
| lengan_depan_90 | 34.4 | 5.42 | ((-0.192, 0.06, 1.375), 'upperarm_r') | 1.0 | 0.02 | 1428 |
| lengan_depan_atas | 41.7 | 6.94 | ((-0.192, 0.06, 1.375), 'upperarm_r') | 1.0 | 0.02 | 1119 |
| lengan_samping_90 | 22.1 | 1.79 | ((-0.225, 0.024, 1.486), 'clavicle_r') | 1.0 | 0.02 | 859 |
| lengan_guard | 33.3 | 3.14 | ((-0.192, 0.06, 1.375), 'upperarm_r') | 1.0 | 0.02 | 1384 |

Gambar: `diagnosa_sheet.png` (WAJIB dilihat: apakah warna penanda ada di tempat yang dikeluhkan?).
