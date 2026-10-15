# Panduan Kerja ala Claude (untuk Hermes)

> Dari Claude, untuk Hermes. **Read-only bagimu.** Wajib dibaca sebelum tugas model 3D, rig, tekstur, atau **perbaikan** ("lengan robek", "ketiak bolong", "wajah meleh", "kain tembus").
> Urutan berlaku: `AGENTS.md` > instruksi khusus `Hermes/<model>_hermes.md` > `Hermes/panduan_model_3d.md` > file ini.
> Versi: 15 Okt 2026 (+ §8 model realistis). Semua resep dan angka di sini sudah diuji Claude pada kerusakan buatan di `SK_Aksa` (lihat §7).

---

## 1. Kenapa hasil Claude memuaskan

Bukan karena "lebih pintar". Ada delapan kebiasaan yang selalu dipakai:

1. **Baca riwayat dulu.** Hampir semua masalah pernah terjadi. Sebelum menyentuh file, cari di `docs/13`, `19`, `20`, `25`, `26` dengan kata kunci gejala (`robek`, `bolong`, `melar`, `tembus`, `meleh`, `keropos`). Riwayatnya berisi penyebab, perbaikan, dan skrip yang sudah terbukti.
2. **Reproduksi sebelum memperbaiki.** Keluhan "lengan robek" harus dilihat sendiri di pose dan sudut yang sama sebelum ada yang diubah. Kalau tidak bisa direproduksi, berarti kamu belum paham masalahnya.
3. **Ukur, jangan menebak.** Penyebab ditentukan dari angka (`diagnosa_mesh.py`). "Sepertinya bobotnya" bukan diagnosis.
4. **Selalu ada pembanding sehat.** Angka hanya berarti kalau dibandingkan. Tepi kerah juga "lubang", dan lipatan paha saat jongkok juga "tembus". Yang dihitung hanya yang **lebih buruk dari model sehat**.
5. **Satu penyebab, satu perbaikan, satu file baru.** Tidak memperbaiki tiga hal sekaligus, tidak menimpa file. `v05 → v06`, file lama tetap ada.
6. **Perbaikan lewat skrip, bukan klik manual.** Skrip bisa diulang, diperiksa, dan dibatalkan. Klik di GUI tidak bisa.
7. **Ukur ulang dengan alat yang sama** (`--sebelum`). "Bobot jauh turun" belum tentu berhasil. Yang menentukan: regangan pose kembali mendekati model sehat (§7 menunjukkan perbaikan yang angkanya membaik tapi regangannya justru memburuk).
8. **Regresi seluruh badan.** Perbaikan ketiak bisa merusak bahu. Setelah wilayah beres, jalankan audit + banding seluruh badan.

## 2. Alur umum (tugas apa pun)

| Langkah | Yang dikerjakan | Bukti di laporan |
|---|---|---|
| 1 Baca | `AGENTS.md`, instruksi tugas, dokumen desain terkait, riwayat masalah serupa | Daftar dokumen yang dibaca + kutipan yang relevan |
| 2 Rencana | Tulis langkah, file yang akan dibuat (versi baru), cara mengukur hasil, **kriteria lulus berangka** | Rencana di laporan **sebelum** mulai |
| 3 Kerjakan 1 langkah | Skrip di `Hermes/Tools/`, output ke file baru | Path file + log skrip |
| 4 Ukur | Alat ukur yang sama dengan sebelum langkah | Angka sebelum → sesudah |
| 5 Lihat | Buka gambar, deskripsikan per bagian | Deskripsi + path PNG |
| 6 Putuskan | Lulus → langkah berikut. Gagal → kembali ke 3 dengan hipotesis baru (maks 3×, lalu berhenti & laporkan) | Alasan keputusan |
| 7 Regresi | Audit/banding seluruh model | `banding.md` |
| 8 Lapor | Template §6 | Laporan lengkap |

## 3. Alur perbaikan model ("lengan robek", dst.)

Contoh di bawah memakai keluhan **"lengan kanan bawah robek saat menangkis"**. Ganti tulang dan pose sesuai keluhan.

### Langkah 0: tulis keluhan persis
Bagian tubuh mana, kanan atau kiri, saat animasi/pose apa, dilihat dari sudut mana, terlihat di Blender atau hanya di UE, dan sejak versi file mana. Kalau developer tidak menyebutkan, **tanya**.

### Langkah 1: siapkan dua FBX
- **Model yang dikeluhkan**: export dari file kerja terbaru dengan skrip export proyek (kontrak FBX docs/19 §6.4) → `Hermes/Art/<topik>/Export/SK_<Nama>_vNN.fbx`.
- **Pembanding sehat**, pilih yang pertama tersedia:
  1. versi model ini **sebelum** rusak (kalau kerusakannya baru muncul);
  2. model lama yang digantikan (Aksa2 → `Art/Export/SK_Aksa.fbx`);
  3. model sejenis yang sudah disetujui (`panduan_model_3d.md` §1).
  Bandingkan **LOD yang sama** (LOD2 vs LOD2), bukan LOD2 vs LOD0.

### Langkah 2: pilih tulang wilayah
| Keluhan | `--tulang` |
|---|---|
| Lengan atas / bahu | `upperarm_r,clavicle_r` |
| Ketiak | `upperarm_r,clavicle_r` (+ `spine_05` kalau badan ikut) |
| Siku / lengan bawah | `lowerarm_r,hand_r` (+ `upperarm_r` untuk siku) |
| Leher / dagu / "wajah meleh" | `neck_01,neck_02,head` |
| Pinggul / selangkangan | `pelvis,thigh_l,thigh_r` |
| Paha / lutut | `thigh_l,calf_l` |
| Pergelangan kaki / sepatu | `calf_l,foot_l` |
Untuk sisi kiri, ganti `_r` dengan `_l`. Untuk monster non-Manny, pakai nama tulangnya sendiri.

### Langkah 3: diagnosa
```
blender --background --factory-startup --python Art/Scripts/diagnosa_mesh.py -- <FBX pembanding> --tulang lowerarm_r,hand_r --out Hermes/Art/<topik>/Diagnosa/pembanding_lenganbawah --tanpa-render
blender --background --factory-startup --python Art/Scripts/diagnosa_mesh.py -- <FBX model> --tulang lowerarm_r,hand_r --out Hermes/Art/<topik>/Diagnosa/v05_lenganbawah --pembanding-hasil Hermes/Art/<topik>/Diagnosa/pembanding_lenganbawah
```
(Raksasa/monster: tambahkan `--height <m>` dan `--profil <json>` yang sama dengan audit.)

Baca `diagnosa.md`:
- **Dugaan penyebab** sudah diurutkan. Dugaan #1 = yang dikerjakan lebih dulu. Ada keterangan "akibatnya" berarti lubang tersebut hilang dengan sendirinya setelah penyebabnya diperbaiki.
- **Buka `diagnosa_sheet.png`.** Warna penanda (merah lubang, magenta bobot jauh, kuning jahitan, oranye bobot tajam, biru tembus) **harus berada di tempat yang dikeluhkan**. Kalau warna ada di tempat lain, wilayah atau tulangnya salah, jadi kembali ke langkah 2.
- **"Tidak ada temuan terukur"**: (a) pose keluhan belum ada di profil, jadi cari pose terdekat lewat `--pose`; (b) masalahnya hanya muncul di UE (resep F8); (c) masalahnya visual/tekstur, bukan geometri. Tulis mana yang berlaku.

### Langkah 4: perbaiki dengan resep (§4)
```
blender --background Hermes/Art/<topik>/Blender/<topik>_v05.blend --python Art/Scripts/perbaiki_mesh.py -- F3 --objek <nama mesh> --tulang lowerarm_r,hand_r --out Hermes/Art/<topik>/Blender/<topik>_v06_F3.blend --sumber <FBX pembanding>
```
Baca output: `sebelum` / `sesudah` / `PERINGATAN`. **Ada PERINGATAN = belum selesai** (ikuti saran di peringatannya, mis. naikkan `--radius`).

### Langkah 5: ukur ulang
Export v06, lalu jalankan diagnosa yang sama ditambah `--sebelum <dir diagnosa v05>`. Lulus kalau:
- dugaan yang diperbaiki **hilang**;
- regangan p99 setiap pose **≤ pembanding + 5 poin** (angka di tabel pose; bandingkan dengan `diagnosa.json` pembanding);
- tidak ada baris **MEMBURUK** yang besar (> 5 poin regangan, atau loop lubang/bobot tajam bertambah);
- di gambar, warna penanda hilang dari tempat yang dikeluhkan.
Masih ada dugaan lain → kembali ke langkah 4 dengan dugaan berikutnya (file v07, dst.).

### Langkah 6: regresi & UE
1. `audit_karakter.py` + `banding_karakter.py` seluruh badan melawan pembanding → **VONIS LULUS**.
2. LOD dibuat ulang dari versi yang sudah diperbaiki, lalu tiap LOD divalidasi dan diaudit.
3. Impor ulang ke UE sandbox, putar animasi keluhan (mis. `MM_Attack_*` untuk pukul/tangkis), lalu screenshot dari sudut keluhan **dan dari bawah**.

## 4. Katalog resep

| Kode | Masalah | Kapan | Cara | Jebakan |
|---|---|---|---|---|
| **F1** | Lubang | Loop tepi terbuka yang **tidak ada di model sehat** (kolom terakhir tabel loop = **tidak**) dan berwarna merah di tempat keluhan | `F1 --pusat "x,y,z;..."`, salin dari tabel loop. Lalu **F4**. Ulangi sampai tabel tidak punya loop "tidak" di tempat keluhan (sisa loop 3 tepi pun ditutup) | **Jangan pernah** menutup loop "ya" (kerah, lengan baju, kantong). Lubang lebar di antara dua bagian yang bergerak beda (ketiak lengan↔badan) lebih baik dijahit "ritsleting" dengan baris tambahan (pola `Art/Scripts/jayadwara2_25_ketiak.py`, docs/25 R8) |
| **F2** | Jahitan terbelah | Vertex kembar berbobot beda (khas GLB Tripo: vertex dipecah per UV) | `F2 --gabung` (bobot disamakan + digabung, UV tetap). Diagnosa ulang: biasanya masih ada F3 sesudahnya | Tanpa `--gabung` jahitan tetap ada sebagai tepi terbuka; aman selama bobotnya sama. **Model potongan kaku** (Jerangkong, docs/20: tulang rontok/susun ulang): vertex kembar ANTAR potongan memang terpisah, jadi itu desain, bukan kerusakan. Pakai versi yang disetujui sebagai `--pembanding`, dan jangan pernah `--gabung` antar potongan |
| **F3** | Bobot ke tulang salah | Dugaan "BOBOT KE TULANG SALAH" | Utama: `F3 --sumber <FBX sehat ber-skeleton sama>` (transfer dari permukaan terdekat, pola docs/25 R1). Tanpa sumber: `F3 --mode jarak`. Hanya ≤ 30 vertex terisolasi: `F3` (tetangga) | **Naikkan `--radius` sampai PERINGATAN "di luar wilayah" hilang**; kerusakan di luar wilayah tetap menarik tepi (§7: radius 0,12 gagal, 0,20 pulih). Tulang kecil (leher) bisa tidak pernah menang bobot: periksa distribusi per tulang, perbaiki dengan interpolasi menurut tinggi (docs/25 R3b) |
| **F4** | Bobot tajam | Lompatan bobot > 0,6 di banyak tepi; setelah F1 | `F4 --iterasi 3 [--kunci pelvis,head]` | Bagian yang memang kaku (gesper, helm, pelat zirah, sol) dikunci, jangan dilunakkan (docs/25 R2: "zirah melentur") |
| **F5** | Melar tanpa cacat topologi | Regangan tinggi, dugaan lain kosong | (a) bobot twist untuk lengan/paha (docs/25 R3); (b) lunakkan zona sendi ±radius sendi; (c) tambah topologi di pita sendi (subdivide 1 tingkat); (d) pose ekstrem: tanya developer apakah pose itu dipakai animasi (docs/25 gate R3) | Jangan menghaluskan bobot seluruh badan; masalahnya pindah ke tempat lain |
| **F6** | Tembus | "TEMBUS" (sudah dibandingkan dengan model sehat) | Lapisan dalam didorong keluar ±8 mm dari lapisan luar (pola `15_body_fit.py`, docs/13); kain ikut kaki dengan bobot kontinu menurut jarak ke kulit (docs/25 R3c); **jangan memisahkan sambungan** kain↔kulit (docs/25 R3d: 440 tepi terbuka) | Lipatan sendi saat jongkok/siku tertekuk wajar sedikit tembus |
| **F7** | Normal terbalik | "NORMAL TERBALIK" lebih buruk dari model sehat, dan di gambar terlihat bolong/gelap tanpa lubang tepi | `F7`, lalu periksa gambar | Lapisan dalam/kantong boleh menghadap ke dalam; kalau yang terbalik justru itu, batalkan (pakai file sebelumnya) |
| **F8** | Hanya terlihat di UE | Blender bersih, UE rusak | Cek berurutan: (1) urutan impor ulang lengkap (docs/25: import → setup → cape → combo); (2) LOD: grup vertex Decimate harus di-**invert** (docs/25 R5 pelajaran 1); (3) Anim Dynamics melempar rantai (docs/25 R3d), matikan dulu untuk menguji; (4) tulang twist tidak digerakkan animasi hasil retarget (docs/25 R3 temuan 2); (5) editor sedang PIE = skrip tidak melihat aset; (6) tekstur blur saat capture = streaming (`r.Streaming.FullyLoadUsedTextures 1`) | Jangan "memperbaiki" dengan opsi impor UE (Recompute Normals dll.) tanpa tahu penyebabnya; sumber kebenaran tetap file Blender |

## 5. Jebakan teknis yang sudah memakan korban

| Jebakan | Gejala | Cara benar |
|---|---|---|
| Menghapus grup vertex sambil membaca `v.groups` | Sebagian bobot lama tertinggal, hasil acak | Ambil daftar indeks dulu: `for gi in [g.group for g in v.groups]: obj.vertex_groups[gi].remove([i])` |
| Segitiga luas nol (Tripo, hasil decimate) | Barisentrik NaN → bobot NaN → vertex tanpa bobot | Periksa `math.isfinite`, fallback ke vertex terdekat |
| Ekor tulang hasil impor FBX tidak sejajar anggota badan | Arah lengan/ruas tulang salah (mis. `lowerarm` menunjuk ke atas) | Ujung anatomis = kepala anak utama (bukan twist/ik) |
| Rujukan Python basi setelah operator impor | Tulis ke mesh yang salah / data hilang | Ambil ulang `obj = bpy.data.objects[nama]; me = obj.data` setelah impor |
| Export FBX tanpa kontrak | Root tambahan, skala ke tulang root, socket jadi tulang | Kontrak docs/19 §6.4: `Armature`, cm di-apply, `FBX_SCALE_ALL`, tanpa empty |
| File masih pointer Git LFS | "ASCII FBX not supported" / file 130 byte | `git lfs pull --include="<file>"` |
| Impor ke `SK_Mannequin` | Skeleton proyek rusak, retarget crash (docs/25 R7) | Salinan skeleton di sandbox (AGENTS.md §3) |
| Uji dari satu sudut saja | Lubang ketiak lolos 13 pose uji (docs/25 R8) | Selalu render dari bawah dengan backface culling (audit & diagnosa sudah melakukannya) |
| Uji satu pose saja | Perbaikan kaki R3c hanya dicek di satu pose jalan, gagal di Play (R3d) | Semua pose profil + pose keluhan |
| "Vertex tanpa bobot = 0" dianggap cukup | Leher tidak punya bobot `neck_*` sama sekali (docs/25 R3b) | Lihat distribusi bobot per tulang |

## 6. Larangan saat memperbaiki

- Menghapus muka/vertex untuk "menyembunyikan" masalah.
- Mengubah skala/posisi tulang supaya mesh terlihat cocok (skeleton Manny tidak boleh diubah).
- Menghaluskan bobot seluruh badan.
- Memperbaiki di UE (opsi impor, material) padahal sumber masalah ada di file Blender.
- Memperbaiki lebih dari satu dugaan dalam satu langkah.
- Mengubah pembanding, profil pose, toleransi, atau radius **diagnosa** supaya dugaan hilang. (Radius **perbaikan** boleh dinaikkan; itu yang diminta PERINGATAN.)
- Menyatakan selesai tanpa `--sebelum`, tanpa regresi seluruh badan, dan tanpa melihat gambar.

## 7. Contoh lengkap (diuji Claude, 15 Okt 2026)

Kerusakan buatan pada `SK_Aksa`, pembanding = `SK_Aksa` asli.

| Kasus | Diagnosa (dugaan #1) | Resep | Hasil `--sebelum` |
|---|---|---|---|
| **Lengan bawah robek** (vertex kembar di tengah lengan bawah, salinannya dibobot ke lengan atas) | JAHITAN TERBELAH 251 pasangan, terpisah 22 cm; 87 loop lubang = akibat | `F2 --gabung` → diagnosa ulang → `F3 --sumber SK_Aksa.fbx --radius 0.2` | Regangan tangkis 2062 % → **28,5 %** (sehat 28,5 %), pukul 143 → **3,0 %** (sehat 3,0 %); tidak ada temuan |
| **Paha** (bobot paha dipindah ke betis) | BOBOT KE TULANG SALAH 135 vertex; 1 loop = akibat | `F3 --sumber` radius 0,12: **gagal** (bobot jauh 135 → 1, tapi regangan jongkok 504 → 651 %) + PERINGATAN di luar wilayah → radius 0,20 | Jongkok **64,6 %** (sehat 64,0 %), lari 48,6 (47,1), kuda-kuda 39,0 (38,2); tidak ada temuan. `--mode jarak` radius 0,20: 62,5 % (juga lulus) |
| **Ketiak bolong** (muka di bawah ketiak dihapus) | LUBANG BARU 7 loop vs 3 di model sehat; tabel: loop di x = 0 (kerah) "ya", loop di ketiak kanan "**tidak**" | `F1 --pusat` 5 loop "tidak" → `F4` | Loop besar 7 → 3 (= sehat); sisa 3 loop kecil (3 tepi) masih merah di gambar → putaran kedua F1 |

Pelajaran yang sudah ada di resep: radius perbaikan harus mencakup seluruh kerusakan; "angka penyebab turun" belum berarti berhasil; jangan menutup semua loop.

## 8. Model realistis (gaya proyek sejak 14 Okt 2026)

Gaya visual proyek sekarang **realistis** (docs/README, docs/09): geometri & tekstur dasar dari **Tripo**, lalu dibersihkan, dipisah, di-rig, dan dibawa ke UE. Jayadwara2 dan Jerangkong sudah lewat jalur ini, dan sebagian besar resep di atas (docs/25 R2–R8) **berasal dari model Tripo itu**. Alur, alat, dan resep tetap berlaku. Yang berubah:

| Hal | Stylized (dulu) | Realistis (sekarang) | Yang dilakukan |
|---|---|---|---|
| Rambut, bulu mata, mata | Gumpalan/cangkang tertutup | **Kartu rambut** & lembar tipis bertepi terbuka, saling tumpang-tindih | Diagnosa dengan `--abaikan-material Hair,Lash,Brow,Eye` (sesuaikan nama slot). Tanpa itu: ratusan "lubang" palsu (kepala `SK_Aksa`: 267 loop → 3 setelah diabaikan) |
| Toleransi regangan | Tekstur polos, melar tidak kelihatan | Pori kulit, serat kain, ukiran di tekstur **ikut melar** dan terlihat | `banding_karakter.py --toleransi 3` (bukan 5) untuk karakter yang dilihat dekat (manusia, wajah, tangan) |
| Pembanding | `SK_Aksa` (skrip, stylized) | Model realistis pertama yang disetujui | Sebelum ada model realistis yang disetujui: pakai `SK_Aksa` **hanya untuk regangan/bobot** (kualitas rig). Tepi terbuka, normal, dan tembus antar-gaya tidak bisa dibandingkan, jadi nilai lewat gambar. Monster: `SK_Jerangkong`; raksasa berzirah: `SK_Jayadwara2` (sudah Tripo/realistis) |
| Tekstur | Dibuat skrip dari palet | Atlas Tripo membawa **bayangan terpanggang** (docs/09 risiko) | Render tekstur dengan cahaya datar (Workbench, warna TEXTURE): gelap permanen di ketiak/dagu/lipatan yang tidak ikut berubah saat pose = bayangan terpanggang. Laporkan; perbaikan (Tripo flat-lit, delighting, material dibuat ulang) diputuskan developer |
| Normal map & seam | Hampir datar | Detail di normal map; seam UV terlihat di bawah Lumen | Cek di UE level Hermes dengan Lumen: garis terang/gelap di seam = tangent tidak cocok (resep F8: impor normal map dengan basis MikkTSpace, jangan "Recompute" sembarangan) |
| Kerapatan mesh | Puluhan ribu tris | Tripo bisa ratusan ribu sebelum LOD | Diagnosa/audit lebih lama: batasi `--pose` ke pose keluhan saat iterasi, jalankan semua pose hanya di regresi akhir |
| Wajah manusia | Morph target skrip | Rawan *uncanny*; MetaHuman masih **keputusan terbuka** (docs/08 #5) | Hermes **tidak** membuat rig/morph wajah realistis atau memakai MetaHuman tanpa instruksi khusus. Tulis temuan di laporan |
| Anggaran poligon | docs/19 A8 (LOD0 60k manusia) | Belum ditetapkan ulang untuk realistis | Pakai angka di docs sampai developer memutuskan. Model melebihi anggaran: **laporkan angkanya**, jangan decimate agresif sampai detail realistisnya hilang |

## 9. Template laporan perbaikan

```markdown
## Perbaikan: <keluhan persis dari developer>
- File: <topik>_v05.blend → v06_F2 → v07_F3 (semua versi tetap ada)
- Pembanding sehat: <FBX> (alasan)
- Riwayat serupa yang dibaca: docs/25 R8 (...), ...
### Reproduksi
- Pose/animasi: ..., sudut: ..., gambar: Diagnosa/v05_.../diagnosa_sheet.png
- Yang terlihat: (deskripsi per bagian)
### Diagnosa v05
(tempel bagian "Dugaan penyebab" + tabel loop dari diagnosa.md)
### Putaran 1: <resep> pada dugaan #1
- Perintah: ...
- Output skrip: sebelum ... / sesudah ... / PERINGATAN ...
- Diagnosa ulang (--sebelum): (tempel tabel Sebelum → sesudah)
- Gambar: ... (deskripsi)
- Keputusan: lulus / gagal (alasan) → putaran 2
### Regresi
- banding.md seluruh badan: VONIS ...
- LOD: validator ... ×4
- UE: screenshot animasi keluhan + dari bawah
### Sisa / pertanyaan untuk developer
```
