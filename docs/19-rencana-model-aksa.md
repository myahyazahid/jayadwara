# 19 — Rencana Implementasi: Model Aksa (Wujud Manusia)

> **Status: USULAN v0.1 (12 Okt 2026)**, menunggu persetujuan developer.
> Mengikuti pola [13-rencana-model-jayadwara.md](13-rencana-model-jayadwara.md) dan memakai ulang pipeline-nya (`Art/Scripts/`, validator, skrip import UE). Bagian yang berbeda dari Jayadwara ditulis eksplisit.
> Keputusan dasar (12 Okt 2026): model Aksa **dibuat sendiri** di Blender (Claude + developer); **MetaHuman** dipakai sebagai placeholder visual sampai model ini jadi ([12](12-technical-design.md#mesh-logika-vs-mesh-visual-aksa)).

## 1. Tujuan & definisi "siap dipakai di UE"

`SK_Aksa` menggantikan komponen MetaHuman di `BP_Aksa` **tanpa mengubah logika, animasi, atau kode** ([12](12-technical-design.md#mesh-logika-vs-mesh-visual-aksa)).

- [ ] Skeletal mesh `SK_Aksa` (LOD0–LOD3) yang memakai **skeleton Mannequin UE5** (lihat keputusan A1) dan bisa memutar animasi Mannequin/Mixamo yang sama dengan Manny.
- [ ] Wajah, rambut, dan pakaian sesuai [`aksa_turnaround_v01.webp`](concept-art/aksa_turnaround_v01.webp) dan [`Aksa versi Final.png`](concept-art/Aksa%20versi%20Final.png), **tanpa** alat transformasi di lengan ([03](03-karakter.md#aksa-jaya-mangkubumi-aksa)).
- [ ] Material & tekstur (5 slot, bagian 6.3).
- [ ] Rantai tulang tambahan untuk selendang & ujung jaket (Anim Dynamics).
- [ ] Morph target ekspresi dasar (kedip, senyum, marah, mulut terbuka).
- [ ] Lulus validasi otomatis + uji pose silat + checklist IP & budaya (bagian 8).
- [ ] Terpasang di `BP_Aksa` menggantikan MetaHuman; animasi gameplay tetap jalan.

## 2. Titik awal (12 Okt 2026)

| Item | Status |
|---|---|
| Konsep | `Aksa versi Final.png` (pose dinamis, ada gauntlet yang dibuang) + `aksa_turnaround_v01.webp` (A-pose depan/samping/belakang + kepala depan/samping, tanpa gauntlet, dengan kalung) |
| Blender | 5.2.2 LTS + MCP; pipeline Jayadwara (`jd_common.py`, `jd_skeleton.py`, validator, render pembanding) |
| UE | Project jalan; `BP_Aksa` = `SKM_Manny_Simple` + `ABP_Unarmed`; `IK_Mannequin` sudah dibuat (`Tools/ue_setup_retarget.py`) |
| MetaHuman placeholder | Belum dibuat (developer) |

**Pelajaran dari Jayadwara yang langsung dipakai:**
1. **Ukur dari reference plane** sebelum menerjemahkan angka (kesalahan lebar kaki di Iterasi 1).
2. **Bandingkan render ortografis vs konsep** berdampingan, bukan hanya angka IoU (revisi besar Iterasi 2). Kepala dirender close-up 3/4.
3. **Kontrak export UE** yang sudah teruji di Iterasi 6: objek armature bernama `Armature`, data dalam cm dan skala di-apply, `FBX_SCALE_ALL`, tanpa empty `SOCKET_*` (socket lewat JSON).
4. **Lapisan luar harus pas di badan**, tanpa celah atau tonjolan ([armor fit](13-rencana-model-jayadwara.md#iterasi-2--hero-modeling-mid-poly)). Untuk Aksa: jaket, celana, dan sepatu terhadap badan.
5. **Metrik deformasi absolut** (perubahan panjang tepi dalam cm), bukan rasio.

## 3. Keputusan Teknis (dengan default yang direkomendasikan)

| # | Keputusan | Default yang direkomendasikan | Alasan |
|---|---|---|---|
| **A1** | Skeleton | **Skeleton Mannequin UE5 asli**: `SKM_Manny` diekspor dari UE → dipakai sebagai armature di Blender → `SK_Aksa` diimpor ke `SKEL_Mannequin` yang sama | Semua animasi Manny/Mixamo-retarget langsung jalan tanpa retargeter. Aksa akan punya animasi terbanyak di game. Jayadwara memakai skeleton sendiri + IK Retargeter karena orientasi tulangnya beda; risiko itu diuji di **spike Iterasi 0**. Fallback: skeleton sendiri + retargeter seperti Jayadwara |
| **A2** | Basis badan & wajah | **MPFB2** (MakeHuman untuk Blender): mesh manusia dengan topologi bersih, lalu di-stylize lewat skrip agar mirip konsep | Wajah manusia dari primitif skrip cenderung kaku. **Hanya aset CC0** dari MPFB2 yang dipakai. Perlu developer menyetujui pemasangan ekstensinya |
| **A3** | Tinggi Aksa | **175 cm** | Atlet silat Indonesia; sedikit di bawah Manny. Kapsul & kamera mengikuti ([12](12-technical-design.md#mesh-logika-vs-mesh-visual-aksa)) |
| **A4** | Ekspresi wajah | **Morph target saja** (±8: kedip L/R, senyum, marah, mulut terbuka, alis naik, meringis, mata lirik) | Skeleton Mannequin tidak punya tulang wajah; dialog vertical slice = teks + potret. Rig wajah penuh → Iterasi 7 |
| **A5** | Rambut | **Mesh gumpalan stylized** (seperti konsep), kaku ke `head` | Lebih ringan dan lebih cocok gaya game daripada groom/cards |
| **A6** | Kulit tertutup baju | **Dihapus** (hanya kepala, leher, lengan bawah, tangan yang tersisa) | Mencegah kulit tembus baju saat pose silat lebar; hemat poligon |
| **A7** | Kain | **Rantai tulang + Anim Dynamics** untuk selendang (±6 tulang) dan dua ujung depan jaket (±2 tulang); celana & badan jaket ter-skin biasa | Sama dengan selendang Jayadwara; tanpa simulasi kain Chaos (berat) |
| **A8** | Anggaran poligon | LOD0 ≤ **60k** · LOD1 ≤ 25k · LOD2 ≤ 10k · LOD3 ≤ 4k tris | Mode manusia sering dilihat dekat; tetap di bawah Jayadwara (≤100k) |

## 4. Prinsip Desain Model

- **Stylized semi-realistis** seperti konsep: bentuk tegas, siluet terbaca dari jauh, detail kecil (jahitan, motif batik) di tekstur, bukan geometri.
- **Siluet kunci**: rambut berantakan ke atas, kerah tinggi berbatik, jaket pendek terbuka, selendang menjuntai di pinggang kiri, boots tebal.
- **Silat dulu**: setiap keputusan bentuk diuji di pose kuda-kuda lebar dan tendangan tinggi; celana dan jaket tidak boleh menghambat atau robek visual.
- **Ketidakkonsistenan referensi** diputuskan di model sheet (Iterasi 0), bukan ditebak saat modeling. Yang sudah diketahui: posisi selendang di view samping, senyum di wajah depan (model = netral), jumlah kantong celana antar-view.

### Daftar bagian & anggaran poligon LOD0

| Kelompok | Bagian | Deformasi | Tulang utama | Anggaran |
|---|---|---|---|---|
| Kepala | Kepala, telinga, mata (+ kornea), alis, gigi/lidah sederhana | Ter-skin + morph | `head`, `neck_*` | 12k |
| Rambut | Gumpalan rambut | Kaku | `head` | 6k |
| Badan terlihat | Leher, lengan bawah, tangan + jari | Ter-skin | lengan, tangan, jari | 6k |
| Atasan | Kaos hitam, jaket (kerah berbatik, lengan digulung, kantong, emblem punggung) | Ter-skin + rantai ujung jaket | tulang belakang, bahu, lengan | 14k |
| Bawahan | Celana kargo (kantong, strap paha), sabuk + gesper | Ter-skin | pinggul, paha, betis | 9k |
| Aksesori | Selendang batik, kalung + liontin, sarung tangan tanpa jari | Selendang: rantai; kalung: `spine_05`/`neck_01`; sarung tangan: ter-skin | — | 5k |
| Sepatu | Boots bertali, sol, trim emas | Ter-skin (pergelangan) + kaku | `foot`, `ball` | 6k |
| **Total** | | | | **±58k** |

## 5. Pembagian Kerja

| Claude (skrip Blender & UE, lewat MCP / `ue_remote.py`) | Developer |
|---|---|
| Reference plane, model sheet, ukuran proporsi | Menyetujui model sheet & keputusan A1–A8 |
| Spike skeleton Manny (export UE → Blender → UE) | Memasang ekstensi MPFB2 (setuju unduhan) |
| Membangun & men-stylize badan, kepala, rambut, pakaian lewat skrip | Review tiap kelompok; **wajah**: feedback paling banyak di sini |
| Rig, skinning, morph target, uji pose, validator | Perbaikan weight manual di titik rumit (bahu, pinggul) |
| UV, tekstur dasar, material preview, LOD, export | Hand-paint (kulit, lipatan, batik), cek warna |
| Import UE, ganti MetaHuman → `SK_Aksa`, Anim Dynamics, potret dialog | Main dan menilai di game |

## 6. Spesifikasi Teknis Aset

### 6.1 Skeleton
- **A1 (default):** armature = `SKM_Manny` hasil ekspor UE, **tidak diubah** posisi/orientasi tulangnya. Mesh Aksa di-fit ke armature itu (proporsi dikoreksi lewat mesh, bukan tulang). Tulang tambahan hanya **daun baru** di bawah tulang yang ada: `sash_01..06` (di bawah `pelvis`), `jacket_l/r_01..02` (di bawah `spine_03`). UE menggabungkan tulang daun baru ke `SKEL_Mannequin` saat import tanpa mengganggu animasi.
- Kalau spike gagal (fallback): skeleton sendiri bernama Mannequin + `IK_Aksa` + `RTG_Mannequin_To_Aksa`, persis seperti Jayadwara.

### 6.2 Socket (lewat `SK_Aksa_sockets.json`, bukan empty)
`hand_r_hit`, `hand_l_hit`, `foot_r_hit`, `foot_l_hit` (hit detection), `pendant` (VFX kalung saat transformasi), `head_fx`, `back_fx`.

### 6.3 Material (5 slot)
| Slot | Isi | Tekstur |
|---|---|---|
| `MI_Aksa_Skin` | Kulit kepala, leher, lengan, tangan | BC, N, ORM, (SSS mask) 2048² |
| `MI_Aksa_Eyes` | Iris, sklera, kornea | BC 512² |
| `MI_Aksa_Hair` | Rambut, alis | BC, N, ORM 1024² |
| `MI_Aksa_Cloth` | Jaket, kaos, celana, selendang, kerah batik | Mask zona, BC, N, ORM 2048² |
| `MI_Aksa_Gear` | Boots, sarung tangan, sabuk, gesper, kalung, emblem | BC, N, ORM 1024² |

Palet diambil dari konsep (hex di model sheet): navy jaket, hitam/charcoal kaos & celana, emas aksen (**sama dengan emas Jayadwara**, `jd_common.HEX`), coklat batik, kulit sawo matang. **Tanpa silver/chrome, tanpa biru menyala.**

### 6.4 Kontrak export FBX
Sama dengan kontrak Jayadwara yang sudah diperbaiki di Iterasi 6 ([13](13-rencana-model-jayadwara.md#iterasi-6--integrasi-unreal)): objek armature bernama `Armature`, data dalam cm dan skala di-apply, `FBX_SCALE_ALL`, tanpa empty, tanpa animasi, LOD sebagai file terpisah (`SK_Aksa.fbx`, `SK_Aksa_LOD1..3.fbx`), morph target ikut (`use_shape_keys`).

### 6.5 Validasi otomatis
`validate_jayadwara.py` digeneralisasi jadi `validate_character.py` (profil per karakter) + cek baru:
- nama, jumlah, dan hierarki tulang **sama persis dengan `SKM_Manny`** (kecuali tulang daun tambahan);
- morph target ada dan tidak menggeser vertex di luar kepala;
- tidak ada kulit di bawah baju (A6);
- batas tris per LOD (A8), ≤4 influence, bobot ternormalisasi, UV 0–1, tepat 5 slot material.

## 7. Iterasi

> Estimasi jam **kasar** (kapasitas ±10–15 jam/minggu). Direvisi di akhir Iterasi 1.

| Iter | Nama | Estimasi | Butuh UE? |
|---|---|---|---|
| 0 | Design lock, fondasi & **spike skeleton** | 8–10 jam | Ya (spike) |
| 1 | Badan dasar + proxy pakaian + rig Manny | 10–12 jam | Ya (uji ganti MetaHuman) |
| 2 | **Kepala & wajah** + rambut | 15–20 jam | Tidak |
| 3 | Pakaian hero | 20–25 jam | Tidak |
| 4 | Skinning final, rantai kain, morph target | 12–15 jam | Tidak |
| 5 | UV, tekstur & material | 15–20 jam | Tidak |
| 6 | LOD, export & integrasi UE | 10–12 jam | Ya |
| 7 | Polish & varian (opsional) | — | Ya |

**Total Iter 0–6: ±90–115 jam ≈ 7–9 minggu** pada kapasitas penuh. Di roadmap, model Aksa dijadwalkan di pengadaan aset Fase 2 (Apr–Mei 2027, [10](10-roadmap.md#fase-2--vertical-slice-episode-1-gerbang-yang-retak-apr--des-2027)); kalau dikerjakan lebih awal sebagai jalur art paralel (seperti Jayadwara), tanggal Fase 0–1 ikut bergeser (keputusan A9).

### Iterasi 0 — Design lock, fondasi & spike skeleton
**Tujuan:** menghilangkan ambiguitas desain dan risiko teknis terbesar sebelum modeling.
- **Claude:**
  - Normalisasi `aksa_turnaround_v01.webp` jadi reference plane depan/samping/belakang + kepala (`make_reference_planes.py`, 1000 px = 1,75 m).
  - **Model sheet Aksa** (dokumen baru di `docs/`, nomor berikutnya): proporsi (jumlah kepala, bahu, panjang kaki/lengan), palet hex, part list final, keputusan atas ketidakkonsistenan referensi.
  - Scene `Art/Blender/aksa_v00_setup.blend` (collection per kelompok, penggaris 1,75 m, penanda landmark).
  - **Spike skeleton (A1):** ekspor `SKM_Manny` dari UE → impor ke Blender → tempel mesh uji sederhana → ekspor dengan kontrak 6.4 → impor ke UE memakai `SKEL_Mannequin` → putar 3 animasi Mannequin. Lulus = tidak ada tulang terpelintir/terbalik dan tidak ada skeleton baru yang dibuat.
- **Developer:** menyetujui model sheet & A1–A9; memasang ekstensi MPFB2 (A2).
- **Gate:** model sheet disetujui; spike lulus (atau fallback dipilih); reference plane sejajar.

### Iterasi 1 — Badan dasar + proxy pakaian + rig Manny
**Tujuan:** proporsi benar, ter-rig, dan **jalur ganti MetaHuman → SK_Aksa terbukti** sejak awal.
- **Claude:** badan MPFB2 di-fit ke reference plane (tinggi 1,75 m, proporsi atlet ramping); pakaian proxy dari primitif (jaket, celana, boots, selendang) dengan 5 slot warna datar; skinning otomatis ke armature Manny; 6 uji pose (kuda-kuda, pukul, tendang tinggi, dodge, jongkok, tangan terangkat); export; validator; pasang di `BP_Aksa` versi uji dan putar animasi gameplay.
- **Developer:** review proporsi di Blender dan di game ("bahu lebih lebar", "kaki kurang panjang").
- **Gate:** siluet depan/samping cocok dengan konsep; animasi Manny jalan di `SK_Aksa` proxy; tidak ada tembus parah di 6 pose.

### Iterasi 2 — Kepala & wajah + rambut
**Tujuan:** wajah yang terbaca sebagai Aksa. **Bagian paling berisiko**, jadi dikerjakan sebelum pakaian hero.
- **Claude:** stylize kepala MPFB2 terhadap reference kepala depan/samping (rahang tegas, alis tebal lurus, hidung lurus, mata coklat); mata dengan kornea terpisah; alis sebagai mesh; rambut gumpalan stylized (poni jatuh di dahi, ujung mencuat ke atas); render close-up depan, samping, 3/4 berdampingan dengan konsep (`render_compare.py` mode kepala).
- **Developer:** feedback wajah (bagian yang paling butuh mata manusia).
- **Gate (Go/No-Go):** wajah "terasa Aksa" menurut developer. Kalau belum setelah 2 putaran revisi: pilih perbaiki lagi, atau **commission sculpt kepala saja** dengan model ini sebagai basis (jauh lebih murah daripada commission karakter utuh).

### Iterasi 3 — Pakaian hero
- **Claude:** jaket (terbuka, kerah tinggi berlapis batik, lengan digulung, kantong dada, aksen emas bahu, emblem emas di punggung), kaos, celana kargo (kantong samping, strap paha), sabuk + gesper emas, selendang batik, sarung tangan tanpa jari, boots bertali + trim emas, kalung + liontin pecahan batu. Hapus kulit tertutup (A6). Skrip fit ala `15_body_fit.py`: pakaian pas di badan tanpa celah dan tanpa tembus.
- **Developer:** review per kelompok (atasan → bawahan → aksesori → sepatu).
- **Gate:** render ortografis berdampingan dengan konsep; tidak ada celah/tembus di pose netral dan kuda-kuda.

### Iterasi 4 — Skinning final, rantai kain, morph target
- **Claude:** bobot final (bahu, pinggul, lutut untuk pose silat lebar), tulang twist & jari dari skeleton Manny, rantai `sash_*` dan `jacket_*`, 8 morph target (A4), uji pose diperluas (13 pose seperti Jayadwara) + `06_deform_check.py`.
- **Developer:** perbaikan weight manual di titik rumit.
- **Gate:** peregangan maks terukur dan dijelaskan; tidak ada tembus kain × kaki di kuda-kuda dan tendangan; morph target tidak merusak mesh.

### Iterasi 5 — UV, tekstur & material
- **Claude:** UV terskrip (`07_uv_unwrap.py` dengan packer sendiri), tekstur dasar (mask zona, BC, N, ORM), motif batik pada kerah & selendang, material preview di Blender yang meniru parameter UE, spesifikasi material Aksa (dokumen baru di `docs/`).
- **Developer:** hand-paint kulit (gradasi, pipi), lipatan kain, keausan sepatu; review motif.
- **Catatan budaya:** motif batik umum (kawung, ceplok, truntum); **hindari batik larangan keraton** (parang rusak, dll., [06](06-referensi-mitologi.md#panduan-sensitivitas-budaya)).
- **Gate:** preview mendekati palet konsep; tepat 5 slot; ukuran tekstur sesuai 6.3.

### Iterasi 6 — LOD, export & integrasi UE
- **Claude:** LOD1–3 (`16_make_lods.py`, lindungi mata/wajah/liontin), export final, validator di semua LOD; skrip import (generalisasi `ue_import_jayadwara.py` → `ue_import_character.py`) ke `SKEL_Mannequin`; material master `M_JD_Character` + 5 MI; **ganti MetaHuman → `SK_Aksa` di `BP_Aksa`** sesuai [12](12-technical-design.md#mesh-logika-vs-mesh-visual-aksa); Physics Asset; Anim Dynamics selendang & ujung jaket; render **potret dialog** (netral, senyum, marah) dari model untuk UI ([18](18-kebutuhan-episode-1.md#f-ui--narasi)).
- **Developer:** main di game, nilai di bawah lighting Ep 1.
- **Gate:** semua animasi gameplay jalan di `SK_Aksa`; tidak ada perubahan kode/ABP yang dibutuhkan untuk mengganti MetaHuman; 60 FPS di `Test_Greybox`.

### Iterasi 7 — Polish & varian *(opsional, Fase 2+)*
Rig wajah penuh untuk cutscene, kepala hi-res, varian pakaian (seragam DWARA, kasual, versi terluka setelah boss Ep 1), model Dimas sebagai turunan Aksa (sepupu, rig sama).

---

## 8. Checklist IP & budaya (dipakai di setiap gate)

- [ ] **Tidak ada alat transformasi di lengan** (gauntlet, gelang, bracer, jam): terlalu mirip Mebius Brace ([01](01-konsep-dan-pilar.md#wajib-dihindari)).
- [ ] Kalung/liontin **tidak menyala** di luar adegan transformasi dan **tidak berfungsi sebagai timer**.
- [ ] Tidak ada silver/chrome atau cahaya biru (palet "teknologi" di konsep lama dibuang).
- [ ] Emblem punggung jaket bukan Garuda dan tidak mirip logo tim di serial Ultra.
- [ ] Motif batik umum, bukan batik larangan.
- [ ] Pose uji & animasi: hindari silang lengan bentuk L.

---

## 9. Risiko

| Risiko | Mitigasi |
|---|---|
| Wajah terlihat kaku / tidak mirip | Basis MPFB2 (A2), Iterasi 2 dikerjakan sebelum pakaian, render pembanding close-up, gate Go/No-Go, fallback commission sculpt kepala |
| Skeleton Manny rusak setelah bolak-balik Blender ↔ UE | Spike di Iterasi 0 sebelum modeling apa pun; fallback skeleton sendiri + retargeter (sudah terbukti di Jayadwara) |
| Kain tembus kaki di pose silat lebar | Uji kuda-kuda & tendangan sejak proxy (Iterasi 1); celana sedikit longgar di selangkangan; rantai tulang selendang |
| Lisensi aset basis | Hanya aset CC0 dari MPFB2; catat asal setiap aset di `Art/README.md` |
| Waktu bersaing dengan Fase 0–1 | Keputusan A9: kerjakan paralel atau tunggu Fase 2; MetaHuman menutup kebutuhan visual sementara |
| Referensi AI tidak konsisten antar-view | Diputuskan di model sheet (Iterasi 0) |

---

## 10. Keputusan untuk Developer (sebelum Iterasi 0)

| # | Pertanyaan | Usulan Claude |
|---|---|---|
| **A1** | Pakai skeleton Mannequin asli? | **Ya**, dengan spike di Iterasi 0; fallback skeleton sendiri |
| **A2** | Pasang ekstensi MPFB2 di Blender (unduh dari extensions.blender.org)? | **Ya**, hanya aset CC0 |
| **A3** | Tinggi Aksa 175 cm? | **Ya** |
| **A4** | Ekspresi lewat morph target saja (tanpa rig wajah) untuk sekarang? | **Ya**; rig wajah di Iterasi 7 |
| **A5–A8** | Rambut gumpalan, hapus kulit tertutup, rantai kain, anggaran 60k | **Ya** (default di bagian 3) |
| **A9** | Mulai kapan: sekarang sebagai jalur art paralel, atau menunggu Fase 2 (Apr 2027)? | Developer yang menentukan. Kalau sekarang: selesaikan dulu sisa Iterasi 6 Jayadwara supaya tidak dua model setengah jadi |

---

## 11. Backlog (di luar scope rencana ini)

- Rig wajah penuh & lip-sync (voice acting di luar scope vertical slice).
- Varian pakaian Aksa, model Dimas (turunan rig Aksa).
- Anggota DWARA lain sebagai karakter 3D (vertical slice cukup potret).
