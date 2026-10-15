# Diagnosa SK_Aksa2.fbx — wilayah upperarm_r, clavicle_r (radius 0.120 m, 2319 vertex)

## Dugaan penyebab (urut)

1. **BOBOT TAJAM** (skor 60) — 135 tepi lompatan bobot > 0,6: [('clavicle_l', 62), ('clavicle_r', 52), ('spine_05', 19)] (pembanding 0) → resep **F4**
2. **MELAR** (skor 50) — p99 565.9% di tangan_terangkat vs pembanding 62.4%, maks 25.33 cm di ((-0.234, 0.091, 1.264), 'upperarm_twist_01_r') → resep **F5**

## Angka

| Ukuran | Nilai |
|---|---|
| lubang | {"loop_akibat_bobot_atau_jahitan": 0, "loop": 0, "loop_besar_>=6": 0, "vertex_tepi": 0, "melebar_maks_x": 1.0} |
| jahitan_terbelah | {"pasangan_kembar": 0, "bobot_beda": 0} |
| bobot_jauh | {"vertex": 0, "per_tulang": []} |
| bobot_tajam | {"tepi": 135, "per_tulang": [["clavicle_l", 62], ["clavicle_r", 52], ["spine_05", 19], ["head", 2]]} |
| bobot_rusak | {"tanpa_bobot": 0, "lebih_4_influence": 0, "tidak_normal": 0} |
| normal_terbalik | {"muka": 360, "dari": 4388, "persen": 8.2} |

## Loop tepi terbuka di wilayah (terbesar dulu)

Loop yang juga ada di model sehat = tepi baju/kerah/kantong yang disengaja: JANGAN ditutup. Kandidat F1 = 'tidak' di kolom terakhir DAN bertanda merah di tempat yang dikeluhkan.

| # | vertex tepi | pusat (m) | tulang dominan | ukuran rest (cm) | akibat bobot/jahitan | ada di model sehat? |
|---|---|---|---|---|---|---|

Pose terburuk: **tangan_terangkat**

| Pose | regangan p99 % | maks cm | lokasi maks | lubang melebar x | jahitan terpisah cm | tembus baru |
|---|---|---|---|---|---|---|
| kuda_kuda | 240.1 | 10.85 | ((-0.234, 0.02, 1.262), 'upperarm_twist_01_r') | 1.0 | 0.0 | 186 |
| pukul | 337.3 | 15.72 | ((-0.234, 0.02, 1.262), 'upperarm_twist_01_r') | 1.0 | 0.0 | 29 |
| tendang_tinggi | 221.2 | 10.29 | ((-0.234, 0.02, 1.262), 'upperarm_twist_01_r') | 1.0 | 0.0 | 66 |
| dodge | 162.6 | 7.91 | ((-0.234, 0.02, 1.262), 'upperarm_twist_01_r') | 1.0 | 0.0 | 99 |
| jongkok | 188.3 | 8.91 | ((-0.234, 0.02, 1.262), 'upperarm_twist_01_r') | 1.0 | 0.0 | 56 |
| lari | 239.7 | 10.63 | ((-0.234, 0.02, 1.262), 'upperarm_twist_01_r') | 1.0 | 0.0 | 315 |
| lompat | 452.1 | 20.22 | ((-0.234, 0.091, 1.264), 'upperarm_twist_01_r') | 1.0 | 0.0 | 143 |
| tendang_samping | 255.3 | 12.25 | ((-0.234, 0.091, 1.264), 'upperarm_twist_01_r') | 1.0 | 0.0 | 57 |
| tangkis | 327.3 | 14.45 | ((-0.234, 0.02, 1.262), 'upperarm_twist_01_r') | 1.0 | 0.0 | 301 |
| putar_badan | 128.6 | 6.34 | ((-0.234, 0.02, 1.262), 'upperarm_twist_01_r') | 1.0 | 0.0 | 58 |
| lunge | 5.0 | 0.52 | ((0.084, -0.027, 1.415), 'clavicle_l') | 1.0 | 0.0 | 1 |
| bungkuk | 71.1 | 3.78 | ((-0.234, 0.02, 1.262), 'upperarm_twist_01_r') | 1.0 | 0.0 | 32 |
| tangan_terangkat | 565.9 | 25.33 | ((-0.234, 0.091, 1.264), 'upperarm_twist_01_r') | 1.0 | 0.0 | 467 |
| lengan_depan_90 | 353.7 | 16.18 | ((-0.234, 0.091, 1.264), 'upperarm_twist_01_r') | 1.0 | 0.0 | 141 |
| lengan_depan_atas | 448.6 | 22.03 | ((-0.234, 0.091, 1.264), 'upperarm_twist_01_r') | 1.0 | 0.0 | 83 |
| lengan_samping_90 | 230.8 | 11.16 | ((-0.234, 0.02, 1.262), 'upperarm_twist_01_r') | 1.0 | 0.0 | 54 |
| lengan_guard | 261.6 | 12.43 | ((-0.234, 0.091, 1.264), 'upperarm_twist_01_r') | 1.0 | 0.0 | 88 |

Gambar: `diagnosa_sheet.png` (WAJIB dilihat: apakah warna penanda ada di tempat yang dikeluhkan?).
