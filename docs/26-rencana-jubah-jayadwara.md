# 26 — Rencana Jubah Upacara Jayadwara

> **Status: v1.2 (14 Okt 2026) — J0, J1 disetujui; J2, J3 (kain bergerak) & J4 (lepas/pakai, tombol Y) disetujui developer; J5 belum (F2).** Sisa J4: pemicu lock-on (F1 Iter 6) & aksi combat pertama menggantikan tombol Y. Sebagian J3 (simulasi rantai) dan J4 (UJDCapeComponent + tombol Y sementara) sudah ditarik ke J1. J-Q1 & J-Q4 dijawab (bagian 4).
> Desain: K9 di [14](14-model-sheet-jayadwara.md); alur gameplay: [07](07-gameplay-sistem.md#jubah-upacara); konsep: [`concept-art/jayadwara_jubah_upacara.webp`](concept-art/jayadwara_jubah_upacara.webp).
> Jadwal: masuk **Fase 2** bareng cutscene transformasi ([23](23-rencana-fase-1.md) "Tidak masuk"). J0–J3 (aset) boleh ditarik lebih awal sebagai jalur art paralel kalau developer mau; J4–J5 butuh lock-on (Fase 1 Iterasi 6) dan Sequencer (F2).

---

## 1. Tujuan & syarat selesai

- [ ] `SK_Jayadwara2_Cape` (mesh terpisah) mengikuti pose `SK_Jayadwara2` tanpa mengubah mesh, skeleton, atau bobot badan yang sudah final ([25](25-rencana-redesign-jayadwara.md)).
- [ ] Bentuk & warna sesuai konsep: merah-putih-emas, panel putih tengah & sisi, rantai emas, ujung runcing bermotif. **Kerah ≤ dagu, tidak mekar ke belakang kepala** (K9).
- [ ] Kain bergerak wajar saat idle, jalan, berbalik, angin; tidak menembus kaki/badan pada skala 45 m.
- [ ] Pakai/lepas: lepas ±2 s (lock-on pertama), lepas cepat ±0,5 s (aksi combat pertama, input tidak hilang), pakai kembali (menang/kepergian), bisa di-skip. Jubah buyar jadi cahaya, tidak jatuh ke tanah.
- [ ] Tidak ada biaya jubah saat combat (mesh disembunyikan, simulasi mati).
- [ ] LOD0–LOD2, satu slot material (pola R8 [25](25-rencana-redesign-jayadwara.md)), lulus validator.
- [ ] Dipakai di cutscene transformasi Ep 1 (Sequencer) dan disetujui developer di Play.

## 2. Titik awal

| Item | Kondisi |
|---|---|
| Badan | `SK_Jayadwara2` final (89 tulang, rantai `cloth_back_01…03` ada **tanpa mesh**), `ABP_Jayadwara2`, `BP_Jayadwara2` |
| Konsep | Satu sheet AI (front/side/back/3/4 + breakdown). Pauldron & rantai di sheet ikut model yang ada, bukan dibuat ulang |
| Pelajaran dari Jayadwara2 | Lembar kain yang menempel ke badan memecah skinning (R2–R3d); Anim Dynamics tanpa batas melempar kain (R3d). Jubah dibuat **terpisah dari awal** dan tidak menyentuh kulit |
| C++ | Belum ada apa pun untuk jubah. Lock-on & transformasi ada di rencana Fase 1 |

## 3. Arsitektur (usulan)

- **Mesh & skeleton terpisah:** `SK_Jayadwara2_Cape` dengan skeleton sendiri `SKEL_Jayadwara2_Cape` = **seluruh 89 tulang Jayadwara2** (nama sama, supaya Copy Pose From Mesh & bobot paha/betis cocok) + rantai jubah baru `cape_{c,l,r,fl,fr}_01…06` (J1: 5 rantai — tengah, sisi, lapel depan). Skeleton badan **tidak diubah** (tidak perlu impor ulang `SK_Jayadwara2`).
- **Ikut pose:** `ABP_Jayadwara2_Cape` → *Copy Pose From Mesh* dari mesh badan, lalu simulasi di rantai `cape_*`.
- **Simulasi:** Chaos Cloth di mesh jubah dengan collider kapsul dari Physics Asset badan (paha, betis, pinggul, punggung). Cadangan: Anim Dynamics **berbatas kecil** di rantai `cape_*` (pelajaran R3d).
- **Rantai emas:** kaku, di-skin ke `spine_05`/`clavicle_*`, tidak disimulasi.
- **C++:** `UJDCapeComponent` di karakter raksasa: `SetCapeEquipped(bool, bInstant)`, state (`Equipped`, `Removing`, `Removed`, `Returning`), event untuk montage & Niagara. Pemicu dari lock-on pertama & aksi combat pertama (ability tag), pakai kembali dari event menang/cutscene. Logika di C++, montage/Niagara dirangkai di Blueprint.

## 4. Pertanyaan untuk developer (default dipakai kalau belum dijawab)

| # | Pertanyaan | Default |
|---|---|---|
| J-Q1 | Bentuk jubah dibuat dari mana? | ✅ **Dijawab 13 Okt: Tripo.** Developer membuat 3 kandidat (`yahya_design/cape01.glb`, `cap02.glb`, `cape03.glb`), Claude memilih **cap02** (lihat Hasil J0). Usulan awal: **Developer buat di Tripo** dari sheet konsep (gaya sama dengan Jayadwara2, pola jalur B). Alternatif: Claude bangun dari skrip Blender (lebih rapi topologinya, gaya lebih kaku) |
| J-Q2 | Simulasi kain | ✅ **Diperbarui 13 Okt (J1c): node C++ `FAnimNode_JDCapeChains`** (rantai Verlet ruang dunia + hambatan udara + kapsul kaki) — bisa diatur dari kode/ABP tanpa melukis cloth di editor. Chaos Cloth tetap opsi kalau hasil rantai kurang halus. Usulan awal: Chaos Cloth; fallback Anim Dynamics berbatas |
| J-Q3 | Animasi lepas/pakai | Developer cari/keyframe di editor (Control Rig) dari referensi pose; Claude siapkan notify & montage lewat skrip. Placeholder: lepas = jubah langsung buyar tanpa gerak tangan |
| J-Q4 | Kapan mulai | ✅ **Dijawab 13 Okt: J0–J3 sekarang** sebagai jalur art paralel (developer minta mulai). J4–J5 tetap menunggu lock-on (F1 Iter 6) & Sequencer (F2) |
| J-Q5 | Panjang jubah | Sesuai konsep (sampai mata kaki), karena tidak dipakai di combat |

## 5. Iterasi

| # | Iterasi | Isi | Claude | Developer | Gate | Estimasi |
|---|---|---|---|---|---|---|
| **J0** | Persiapan | Ukur titik kait di mesh Jayadwara2 rest (bawah pauldron, punggung atas, tengkuk); sheet ortografis jubah dari konsep; jawab J-Q1–Q5 | Ukur & render referensi Jayadwara2 depan/samping/belakang dengan garis bantu kait | Pilih jalur bentuk; (Tripo) buat jubah dari sheet | Titik kait & panjang disepakati | 2–4 j |
| **J1** | Spike bentuk + rig | Jubah kasar ditempel ke Jayadwara2, skeleton jubah + rantai `cape_*`, bobot, ekspor FBX, impor UE, Copy Pose From Mesh | Normalisasi skala/posisi, pisah dari kulit (jarak minimal ke badan), rig & bobot, skrip impor/setup UE | Nilai siluet di Play (idle, jalan) | Jubah ikut badan di idle & jalan tanpa celah/menembus; developer bilang lanjut | 6–10 j |
| **J2** | Bentuk final & tekstur | Panel putih, rantai emas kaku, ujung bermotif, tepi tertutup; satu material; LOD0–2 | Bersih-bersih mesh, UV, mask zona (merah/putih/emas), LOD, validator | Tuning warna di MI | Validator lulus, cek IP (kerah ≤ dagu) | 6–10 j |
| **J3** | Kain bergerak | Chaos Cloth + collider; uji idle, jalan, berbalik, angin, lompat | Setup cloth & collider lewat skrip sejauh API mengizinkan, uji tangkap layar | Tuning parameter kain di editor, nilai di Play | Tidak menembus kaki, tidak terlempar; FPS tidak turun berarti | 4–8 j |
| **J4** | Pakai/lepas | `UJDCapeComponent`, pemicu lock-on & aksi pertama, montage lepas/cepat/pakai, Niagara buyar/kembali, skip | C++ komponen + state + pemicu, notify, skrip montage, uji otomatis PIE | Animasi (J-Q3), efek Niagara, rasa timing | Alur [07](07-gameplay-sistem.md#jubah-upacara) jalan penuh; input serangan tidak hilang; tanpa jubah tidak ada biaya cloth | 8–12 j |
| **J5** | Cutscene & polish | Kedatangan berjubah di cutscene transformasi Ep 1, pose menang/kepergian, LOD layar | Bantu track Sequencer lewat skrip, cek LOD/FPS | Sutradarai cutscene | Developer setuju di Play | 3–6 j |

**Total ±29–50 jam.** J0–J3 tidak bergantung pada combat; J4 butuh lock-on (Fase 1 Iterasi 6); J5 butuh cutscene transformasi (F2).

## 6. Risiko

| Risiko | Mitigasi |
|---|---|
| Kain menembus kaki pada langkah lebar (seperti R3c) | Jubah tidak menyentuh kulit sejak J1; collider kapsul paha/betis; tidak dipakai di combat |
| Chaos Cloth susah diatur lewat skrip (Claude tidak bisa edit `.uasset` langsung) | Tuning di editor oleh developer; fallback Anim Dynamics berbatas |
| Animasi lepas tidak ada sumbernya | Placeholder buyar tanpa gerak (J-Q3) supaya alur C++ tetap bisa diuji |
| Mesh Tripo jubah menyatu/bertopologi berantakan | Pola Jayadwara2: pemisahan lembar via ketebalan, tutup tepi; atau jalur skrip (J-Q1) |
| Scope melebar ke Fase 1 | Jadwal default F2; Fase 1 tetap tanpa jubah ([23](23-rencana-fase-1.md)) |

## 7. Hasil iterasi

| Iterasi | Status | Tanggal | Ringkas |
|---|---|---|---|
| J0 Persiapan | ✅ disetujui developer | 13 Okt 2026 | Pilih `cap02`; depan dibuka; kerah 1,60 m / ujung 0,10 m; titik kait diukur; fit lokal = pekerjaan utama J1 |
| J1 Spike bentuk + rig | ✅ **selesai, disetujui developer** (putaran J1b–J1f) | 13 Okt 2026 | Fit lokal tanpa tembus (rest), rig 119 tulang, bobot kinematik, validator 27/27, terpasang di `BP_Jayadwara2` (komponen `Cape`) |
| J2 Bentuk final & tekstur | ✅ **disetujui developer** (14 Okt) | 13 Okt 2026 | Mask zona (recolor terbukti), LOD0–2 (29,2k/14,6k/7,0k), bros ornate, lubang ditutup, kerah ≤ 1,600 m (K9), validator 27/27 ×3, impor UE stabil |
| J3 Kain bergerak | ✅ **disetujui developer di Play** (14 Okt: "kain sudah bergerak dengan baik") | 14 Okt 2026 | Node `FAnimNode_JDCapeChains` + kapsul kaki; terbukti terangkat saat jatuh (Simulate). Sisa: uji jalan/lari/berbalik/angin/mendarat di Play, tuning, FPS |
| J4 Pakai/lepas | ✅ **lepas/pakai disetujui developer** (14 Okt: "sesuai harapan"); sisa = pemicu otomatis | 14 Okt 2026 | `UJDCapeComponent` (state, event), dissolve emas, tombol Y sementara. Sisa: pemicu lock-on (F1 Iter 6) & aksi combat pertama, lepas cepat 0,5 s, pakai kembali saat menang, animasi tangan, Niagara, skip |
| J5 Cutscene & polish | ⬜ belum | — | Butuh cutscene transformasi (F2) |

### Hasil J0 (13 Okt 2026)

**Pemilihan model** (3 GLB Tripo dari developer, semua 1 material 2048² BC/N/ORM, ±38k tris):

| Kandidat | Isi | Penilaian |
|---|---|---|
| `cape01.glb` | Jubah **menyatu dengan badan** karakter lain (bukan Jayadwara2), 99 tepi non-manifold | ❌ Melanggar prinsip "jubah terpisah dari kulit" (bagian 2); jubah tidak bisa dicabut bersih. Tetap berguna sebagai **acuan bentuk bukaan depan** (lapel putih di tepi depan) |
| **`cap02.glb`** | **Jubah saja**, 37,6k tris, satu lembar utuh, cocok dengan "Cape / Mantle breakdown" konsep (panel putih tengah & sisi, rantai emas berjuntai, ujung runcing bermotif emas) | ✅ **Dipilih.** Kekurangan: mantel **tertutup di depan** (panel depan sampai lutut) → dibuka di J0 |
| `cape03.glb` | Tripo memodelkan **seluruh sheet konsep** (8 figur + potongan breakdown + swatch palet) jadi satu mesh | ❌ Tidak terpakai |

Sumber disalin ke `Art/Source/jayadwara2_cape_tripo_v01.glb` (asli di `yahya_design/` tidak diubah). Skrip: `Art/Scripts/jayadwara2_cape_01_intake.py` (di atas `jayadwara2_v05_rig_r3.blend`, file itu tidak ditimpa) → `Art/Blender/jayadwara2/jayadwara2_cape_v00_intake.blend` (`JD2_Cape_Source` + empty `JD2C_ANCHOR_*`); render `jayadwara2_cape_02_render.py` → `Art/Export/_jd2c/`. Pembanding konsep vs hasil: **`Art/Export/_jd2c/_banding_konsep.png`**.

| Temuan / keputusan | Nilai | Akibat |
|---|---|---|
| Arah hadap GLB | Depan di −X | `--rot-z 90` → menghadap −Y |
| Topologi cap02 | 1 pulau, 85 tepi non-manifold (13 setelah merge jahitan UV), 26k → 18,6k vertex | Bersih, tanpa pemisahan lembar ala R2 |
| **Bukaan depan** | Tripo membuat mantel tabung tertutup; konsep terbuka memperlihatkan zirah & permata dada | Sektor depan ±55° di bawah pita kerah dibuang (4.766 muka, sisa 32,7k tris). Panel putih sisi jadi "lapel" depan seperti konsep. Tepi potongan masih mentah (tanpa list emas) → J2 |
| **Tinggi kerah (K9)** | Dagu Jayadwara2 terukur **1,613 m** | Puncak kerah **1,60 m** (≤ dagu ✅). Kerah jubah tertutup kerah leher badan yang lebih tinggi; tidak mekar ke belakang kepala |
| **Panjang** | Ujung runcing terbawah **0,10 m** (mata kaki, J-Q5) | Skala tinggi ×1,50 dari GLB |
| Lebar/kedalaman | 3 kandidat dibandingkan visual: seragam (lengan menembus, terlalu ramping), **×1,10 / ×1,25 / +2 cm Y**, ×1,30 / ×1,50 (mengembang) | Kandidat tengah paling mirip proporsi konsep → default `--fit`. Lebar ujung ±0,59 m |
| **Titik kait** (badan rest) | Tengkuk (0, 0,106, 1,57) · punggung atas/pusat rantai (0, 0,115, 1,45) · bahu di balik pauldron (±0,188, 0,069, 1,52) · dagu (0, −0,117, 1,613) | Dipakai J1 sebagai target lem jubah ke `spine_05`/`clavicle_*` |
| **Masalah utama untuk J1** | Fit global tidak bisa membebaskan jubah: **puncak jubah tenggelam di pelat punggung & pauldron** (dari belakang, pelat punggung terlihat di atas jubah; konsep: jubah menutup punggung sampai tengkuk). Laporan jarak: kerah 957/1.098 vertex di dalam badan, punggung 952/3.603, pinggul 97, kaki 136 (lengan dikecualikan) | J1: fit **lokal** (dorong keluar per tinggi/sudut + perataan) supaya bahu jubah naik menutup pelat punggung dan masuk di bawah pauldron; jarak bebas ≥2 cm di bawah kerah. Catatan: tanda jarak tidak andal di lembar kain tipis badan (sayap) → cek visual juga |
| Warna | Merah tua/putih/emas, tanpa silver | ✅ sesuai palet; merah Tripo lebih gelap dari konsep → tuning di MI (J2) |
| IP (K9) | Kerah ≤ dagu, tanpa kerah mekar, bukan senjata | ✅ |

**Gate J0 (developer):** setujui (1) pilihan `cap02`, (2) bukaan depan 55°, (3) kerah 1,60 m & ujung di mata kaki, (4) proporsi lebar ×1,10 / kedalaman ×1,25. → **Disetujui semua (13 Okt 2026).**

### Hasil J1 (13 Okt 2026)

Pipeline: `jayadwara2_cape_01_intake.py` → `jayadwara2_cape_10_fit_rig.py` (→ `Art/Blender/jayadwara2/jayadwara2_cape_v01_rig.blend`) → `jayadwara2_cape_11_pose_tests.py` → `jayadwara2_cape_14_export.py` → `validate_jayadwara.py` (27/27) → UE `Tools/ue_import_jayadwara2_cape.py` → `Tools/ue_setup_jayadwara2_cape.py`; bukti `Tools/ue_capture_jayadwara2_cape.py`. Gambar: `Art/Export/_jd2c/_ue_j1.png` (UE), `_pose_j1.png` dan `poses/j1b_*.png` (Blender), `jd2c_v01_*.png` (rest).

| Langkah | Hasil | Catatan |
|---|---|---|
| **Fit lokal** | Badan sebagai *lambung radial* per ketinggian (raycast horizontal dari luar ke sumbu); dorongan radial disamakan dalam 3 cm (sisi dalam/luar lembar) lalu disebar halus. **0 vertex di dalam badan + jarak bebas** (2,5 cm; kerah 1,2 cm); geser rata-rata 1,9 cm | **Lengan & pauldron dikecualikan** dari lambung: tanpa itu kerah terdorong melewati pauldron dan jadi "rak" datar. Kini pauldron duduk DI ATAS jubah seperti konsep, punggung tertutup sampai tengkuk. 130 muka sisa panel depan Tripo di sumbu tubuh (antara kaki) dibuang dulu; kalau ikut didorong radial jadi sirip di pinggul |
| **Skeleton** | 119 tulang = 89 badan + 30 `cape_*` (5 rantai × 6, induk `spine_05`) | Rantai **berbobot 0** di J1, disiapkan untuk J3 (Anim Dynamics cadangan). Di Blender, tulang bernama sama diberi Copy Transforms ke `JD2_Armature` (meniru Copy Pose From Mesh) |
| **Bobot (kinematik)** | Bobot kulit badan terdekat (lengan → clavicle, leher/kepala → spine_05, betis/telapak → calf), dilemahkan dengan jarak 3→23 cm ke "bobot jauh" (pelvis 0,9 m → spine_03 1,2 m → spine_05 1,45 m); kaki ≤ 0,6 (pola sayap R3d); dihaluskan topologi + spasial; ≤4 pengaruh | Sebaran: pelvis 45 %, paha/betis 36 %, spine 25 %, clavicle 6 % (dari pauldron: jubah di bawahnya ikut bahu) |
| **Uji pose** (kapsul paha r≈15 cm, betis r≈10 cm) | Rest/jongkok/putar badan/lengan/kepala rapi. **Jalan: tumit kaki belakang (lutut 30°) menembus ujung jubah** (±500–580 vertex di kapsul betis); lari & tendang 90° menembus paha/betis | Dicoba porsi kaki 0,85/1,0 dan jangkauan 30–40 cm: tembus turun (582 → 214) tapi regangan meledak (p99 76 % → 150 %, maks >1000 % = kain tampak sobek). **Skinning linear tidak bisa dua-duanya** → baseline 0,6 dipertahankan; tembus tumit diselesaikan di **J3** (Chaos Cloth + collider kapsul). Jubah tidak dipakai di combat, jadi lari/tendang bukan target |
| **Export & validasi** | `SK_Jayadwara2_Cape.fbx` 32.573 tris, 1 material, 119 tulang, validator **27/27** (`--height 1.50 --zmin 0.10 --extra-bone-prefix cape_ --no-sockets`, opsi baru, perilaku bawaan validator tidak berubah: badan tetap 27/27) | Tekstur BC/N/ORM Tripo + Emit hitam & Mask "zona merah penuh" datar (J1: warna = atlas apa adanya, recolor mati) |
| **UE** | `/Game/Jayadwara/Characters/Jayadwara2/Cape/`: `SK_Jayadwara2_Cape`, `SKEL_Jayadwara2_Cape` (89 tulang cocok nama dengan badan), `MI_Jayadwara2_Cape` (induk `M_Jayadwara2_Master`), `ABP_Jayadwara2_Cape` (**Copy Pose From Mesh, induk attach** → Output Pose). `BP_Jayadwara2` dapat komponen `Cape` (anak `CharacterMesh0`, tanpa tabrakan) | ABP diisi lewat fungsi editor C++ baru `UJDEditorToolsLibrary::SetupCopyPoseAnimBlueprint` (Python UE tidak bisa menyisipkan node anim graph). Tangkapan editor (pose rest): warna merah-putih-emas cerah, pauldron di atas jubah, bukaan depan memperlihatkan zirah |

**Sementara sampai J4:** jubah **selalu terpakai**, juga saat combat (belum ada lepas/pakai). Lepas dari BP: `python Tools/ue_remote.py -c "CAPE=False; exec(open(r'C:/repository/unreal_engine/jayadwara/Tools/ue_setup_jayadwara2_cape.py').read())"`.

**Sisa untuk J2:** tepi potongan depan mentah (belum ada list emas), pita kerah sedikit bergelombang di bahu, Mask zona merah/emas/putih, LOD1–2. **Untuk J3:** tumit/paha menembus saat langkah lebar (collider), rantai `cape_*` bila jalur cadangan Anim Dynamics.

**Gate J1 (developer):** Play di `Test_GiantScale2` (T = transformasi) → nilai siluet jubah di idle & jalan. → **13 Okt: "sudah bagus tapi perlu dipoles"** — (1) dari atas ada tonjolan di leher/bahu, (2) di depan ada bulatan merah yang seharusnya bersih (terbawa dari cap02), (3) minta tombol **Y** sementara untuk melepas jubah dengan animasi. → J1b.

### Hasil J1b (13 Okt 2026) — poles + tombol Y

| Masalah | Penyebab (dibandingkan dengan konsep) | Perbaikan |
|---|---|---|
| Bulatan merah di depan | Bagian depan **pita kerah** cap02 (7 cm teratas) sengaja tidak ikut dibuka di J0; setelah fit ia menjuntai melintang di atas zirah dada. Konsep: depan bersih, jubah hanya dari bahu ke belakang | `jayadwara2_cape_10_fit_rig.py`: bukaan depan 55° diteruskan ke pita kerah (z ≥ 1,40 m, 1.076 muka) + buang serpihan rantai yang terputus |
| Tonjolan leher/bahu (dilihat dari atas) | Pita kerah cap02 berupa **gulungan tebal** (seperti tudung terlipat); fit radial mendorongnya keluar jadi "donat" di sekeliling leher. Konsep: jubah jatuh rapi dari bahu, kerah tipis di belakang leher (detail *back collar*) | Zona bahu/leher 1,25–1,40 m (transisi halus): jarak tiap vertex ke lapisan terdalam lembar di sel (sudut 4°, tinggi 2,5 cm) dikompres **×0,12**, lalu lembar ditempel ke lambung badan + jarak bebas. Gulungan jadi flap datar. Uji pose & validator tidak berubah (27/27) |
| Tombol Y: lepas jubah dengan animasi | Belum ada aset animasi tangan (J-Q3) | **C++ `UJDCapeComponent`** (`Source/Jayadwara/Characters/JDCapeComponent.*`, dipasang di `AJDGiantCharacter` sebagai `CapeControl`): state Equipped/Removing/Removed/Returning, `SetCapeEquipped(bool, bInstant)`, `ToggleCape()`, event `OnCapeStateChanged` (untuk montage/Niagara J4). Animasi prosedural: jubah naik 6 % & mundur 5 % tinggi badan sambil **buyar jadi cahaya emas dari bawah ke atas** (2,0 s; pakai kembali 1,6 s). Setelah lepas, mesh disembunyikan & tick dimatikan (tanpa biaya). **Y** = `BindKey` sementara di `AJDGiantCharacter::SetupPlayerInputComponent` (diganti pemicu lock-on/aksi combat di J4). Material **`M_Jayadwara2_Cape_Master`** = salinan master badan + Masked: `v = 0,6·noise(posisi lokal) + 0,4·tinggi`, OpacityMask `v − Dissolve + 0,5`, pinggiran `|v − Dissolve| < 0,04` menyala emas (`Dissolve_GlowColor/Intensity/EdgeWidth`, `Dissolve_HeightRef`) |

Bukti: `Art/Export/_jd2c/_ue_j1b.png` (UE, rest), `_ue_j1b_lepas.png` (Dissolve 0 / 0,3 / 0,6 / 0,85). Animasi & tombol belum bisa diuji Claude (tidak ada tick di editor remote) → developer uji di Play: transformasi (T), lalu **Y** lepas, **Y** lagi pakai kembali.

**Nilai developer J1b (13 Okt):** leher belakang–bahu masih "terpotong", kurang mirip konsep; saat lompat jubah lengket di kaki — seharusnya terangkat saat turun, seperti terbang. → J1c.

### Hasil J1c (13 Okt 2026) — yoke seperti konsep + jubah terangkat saat lompat

| Masalah | Penyebab | Perbaikan |
|---|---|---|
| Leher belakang–bahu "terpotong" | Gulungan kerah cap02 (dipadatkan di J1b) + pelat punggung badan terlihat di atasnya. Konsep: jubah menutup punggung atas & puncak bahu sampai pangkal leher, panel putih mulai tepat di bawah kerah, bros permata di bahu | **Yoke dibangun dari skrip** (`build_yoke` di `jayadwara2_cape_10_fit_rig.py`): profil punggung/bahu per irisan vertikal (raycast dari titik di tulang belakang, z 1,42 m), di luar lambung badan (tanpa lengan/pauldron → masuk di bawah pauldron) dan di luar jubah lama; **selubung** ±12° menjembatani cekungan antar pelat belikat (tanpa itu muncul dua "punuk"); 103×23 titik, θ ±76,5° (berhenti otomatis di irisan terakhir yang valid), z 1,36–1,555 m (puncak bahu dari 1,50). UV per zona dari titik atlas bersih: merah, **strip putih tengah** (menyambung panel putih), list emas di kerah & tepi depan (tanpa list bawah supaya menyambung ke jubah). Muka jubah lama di bawah yoke dibuang (1.706). **Ornamen:** 2 bros (cincin emas + 4 ujung wajik + permata merah, r 5 cm, di ±0,15 m / 1,42 m) dan hiasan emas runcing di puncak strip putih |
| Jubah lengket di kaki saat lompat | Skinning kinematik (bobot pinggul/paha) tidak punya inersia | **Bobot baru:** di bawah 1,28 m jubah ikut **5 rantai `cape_*`** (interpolasi antar-rantai menurut sudut di sekeliling badan, antar-ruas menurut tinggi; transisi ke bobot kaku s/d 1,40 m; yoke & ornamen kaku ke spine_05/clavicle). Uji Blender: rantai diangkat besar → kain melengkung mulus (tanpa sobek). **Node C++ `FAnimNode_JDCapeChains`** (`Source/Jayadwara/Animation/`, node editor `UAnimGraphNode_JDCapeChains`, disisipkan oleh `UJDEditorToolsLibrary::AddCapeChainsNode` setelah Copy Pose): partikel tiap rantai di ruang dunia (Verlet, sub-langkah 1/60 s), gravitasi 980 cm/s², **hambatan udara 2/s** (badan jatuh → kain tertahan udara → terangkat; lari → tertinggal ke belakang), pegas ke pose animasi 5/s², batas sudut 75°, panjang ruas tetap, **kapsul paha/betis/pinggul** (radius 14/9,5/14 cm authoring + margin 1 cm; sendi rantai saat diam ≥1,3 cm dari kapsul) — sekaligus mengatasi tumit tembus J1. Reset otomatis saat teleport/jeda > 0,25 s. Parameter bisa dituning di `ABP_Jayadwara2_Cape` (node "JD Cape Chains") |

**Uji di UE (Simulate lewat remote, `Tools/ue_probe_jayadwara2_cape.py`):** Jayadwara2 jatuh bebas dari 600 m (4.000 cm/s): pada frame 60 fps ujung rantai belakang naik ±9 m dan rantai samping 9–13 m (≈20–30 % panjang jubah) → **jubah terangkat saat jatuh** ✅. Fase mendarat/diam & jalan belum terlihat (editor di latar belakang ±3 fps → node mereset tiap frame, by design) → developer uji di Play. Gambar: `Art/Export/_jd2c/_ue_j1c.png`. Validator 27/27 (34.765 tris).

### Hasil J1d (13 Okt 2026) — revisi bahu/leher

**Nilai developer J1c:** overall bagus; revisi: (1) jubah belakang jangan menutupi pauldron, (2) jangan ada "lipatan pembatas" (sambungan yoke–jubah) — harus lurus, (3) leher belakang belum selaras → jubah naik sampai kerah belakang / warnanya disamakan, (4) jangan ada garis kuning melintang di bagian atas.

| Revisi | Perbaikan |
|---|---|
| Tanpa lipatan pembatas, lurus | **Lembar yoke terpisah dihapus** (selalu menyisakan sambungan; dua percobaan — menekuk yoke ke jubah, lalu mendorong jubah ke yoke — tetap bergerigi/bertangga). Diganti **kain jubah asli diteruskan ke atas**: muka di atas 1,24 m dalam rentang punggung dibuang, lalu vertex 0,65–1,24 m direntangkan tegak (×1,82) sampai kerah, dan jarak horizontalnya mengikuti permukaan profil punggung/bahu (selubung + **menggantung lurus**: di bawah 1,50 m jari-jari tidak mengecil ke bawah) ditambah lipatan aslinya (selisih ke rata-rata sel 4°×3 cm). Hasil: lipatan tegak & panel putih bertekstur Tripo menerus tanpa sambungan; rentang memudar di tepi (±99°) |
| Tidak menutupi pauldron | Semua muka jubah di zona pauldron (|x| > 0,21 m, z > 1,44 m; tepi dalam pauldron diukur 0,20–0,22 m) dibuang |
| Leher belakang selaras | Kain naik sampai 1,60–1,613 m (≤ dagu 1,613, K9), satu kain dengan jubah → warna sama |
| Tanpa garis kuning | Tidak ada list emas melintang; yang tersisa hanya list tegak bawaan panel putih jubah |
| Ornamen (konsep) | 2 bros (±0,155 m, 1,46 m), **2 juntai rantai antar-bros** (lendut 6 & 13 cm), **liontin tengah**, **rantai gantung di bawah tiap bros** + wajik, hiasan runcing di puncak panel putih — semua dari skrip, ditempel ke permukaan kain (sinar lurus dari belakang) |

Bobot rantai (J1c) & node simulasi tetap. Validator 27/27 (29.115 tris). Gambar: `Art/Export/_jd2c/_ue_j1d.png`. **Sisa (J2):** tepi atas kain di dekat pauldron/pangkal leher sedikit bergerigi; bros masih sederhana; tekstur bagian yang direntangkan ×1,8 (ornamen emas kecil di panel ikut memanjang).

### Hasil J1e (13 Okt 2026) — rapikan dari atas

**Nilai developer J1d:** suka; dari atas terlihat seperti tempelan-tempelan, minta lebih rapi & menyatu.

| Penyebab | Perbaikan (`jayadwara2_cape_10_fit_rig.py`) |
|---|---|
| Potongan atas per pusat muka → tepi bergerigi, makin besar setelah direntangkan ×1,8 | Semua kain (punggung, sisi, lapel) dipotong dengan **bidang datar** di 1,24 m (`bisect_plane`), lalu direntangkan ke **tinggi target per sudut**: 1,60 m (kerah) di punggung, turun mulus ke 1,44 m (bawah pauldron) di 70–95° → satu garis tepi menerus, tanpa tebing antara punggung & lapel |
| Lipatan asli ikut sampai tepi → gigi-gigi | Lipatan dipudarkan dalam pita 10 cm di bawah tepi atas (jarak ke tepi, bukan tinggi absolut) |
| Zona pauldron dibuang per pusat muka → lubang & gerigi | Dipotong bidang z = 1,44 dan x = ±0,21 sebelum dibuang |
| Serpihan ujung ornamen Tripo | Pulau < 40 vertex dibuang; **semua tepi terbuka di atas 1,30 m dihaluskan** sepanjang garisnya (12 iterasi) + pita di bawahnya dihaluskan ringan |

Juga: `Tools/ue_import_jayadwara2_cape.py` kini **melepas rujukan `BP_Jayadwara2.Cape`** sebelum menghapus mesh lama (sebelumnya impor ulang sering gagal diam-diam: "tidak terimpor sebagai SkeletalMesh"); `ue_capture_jayadwara2_cape.py` punya kamera `atas` & `atas_belakang`. Validator 27/27 (30.270 tris). Gambar: `Art/Export/_jd2c/_ue_j1e.png`, `_ue_j1e_atas.png`.

### Hasil J1f (13 Okt 2026) — bagian atas menempel tubuh, naik sampai kerah di sisi

**Nilai developer J1e:** overall bagus; dari samping / sudut tertentu bagian atas jubah masih seperti tempelan — jubah harus seperti kain yang menempel di tubuh. Hanya bagian atas yang dikerjakan (ukiran emas, garis putih, dll. sudah oke). Saran: naikkan jubah sampai kerah.

| Penyebab | Perbaikan |
|---|---|
| Sisi jubah berhenti di bawah pauldron (1,44 m) → tepi potongan seperti lempengan dari samping | Rentang kain yang mengikuti tubuh diperlebar ±99° → **±122°** (bukaan depan 125°; batasnya hanya konstanta, profil badan valid sampai 125°); tepi atas = **kerah 1,60 m sampai 100°**, turun ke 1,55 m di tepi depan |
| Selubung & "gantung lurus" juga berlaku di sisi → sudut bahu berdiri tegak menjauhi badan (kotak) | Gantung lurus/selubung hanya di punggung tengah (penuh s/d 40°, hilang di 75°); di sisi kain **menempel tubuh** (profil bahu) |
| Potongan zona pauldron (x = ±0,21) terlihat dari belakang | Potongan dihapus — kain di sisi menempel bahu di bawah pauldron (tidak menutupinya), tanpa tepi potongan |

Ornamen, rantai, panel putih, bobot rantai & node simulasi tidak berubah. Validator 27/27 (29.249 tris). Gambar: `Art/Export/_jd2c/_ue_j1f.png`, `_ue_j1f_samping.png` (sudut screenshot developer). Catatan impor UE: kalau `ue_import_jayadwara2_cape.py` melapor "tidak terimpor", jalankan sekali lagi (aset lama baru terhapus tuntas di frame editor berikutnya).

**Gate J1: ✅ disetujui developer (13 Okt 2026, "bagus bgt") — iterasi J1 ditutup.** Sudah ditarik dari iterasi lain: simulasi rantai `FAnimNode_JDCapeChains` (J3; sisa: uji jalan/lari/mendarat & tuning di Play) dan `UJDCapeComponent` + dissolve + tombol Y sementara (J4; sisa: pemicu lock-on/aksi combat, animasi tangan, Niagara). Sisa untuk J2: tepi atas sedikit kasar dari atas di dekat pauldron, bros masih sederhana, Mask zona warna, LOD1–2, tekstur bagian yang direntangkan ×1,8.


### Hasil J2 (13 Okt 2026) — bentuk final & tekstur

| Item | Hasil |
|---|---|
| **Mask zona** | `Art/Scripts/make_textures_jayadwara2_cape.py` (python -I) → `T_Jayadwara2_Cape_Mask.png` (R merah, G emas, B 0, A putih; klasifikasi `jd2_atlas.zone_labels` sama dengan badan; texel gelap/lain → merah karena desain jubah tanpa zona hitam) + `_Mask.json`. Pangsa texel: merah 60 %, emas 28 %, putih 12 %. Diverifikasi render Blender (mask sebagai warna) dan UE: **`MI_Jayadwara2_Cape_TesWarna`** (merah → biru tua) mengubah kain saja, list emas & panel putih tetap (`Art/Export/_jd2c/_ue_j2_teswarna.png`). Developer: tuning `Zone_*_Color/_Amount` di `MI_Jayadwara2_Cape`. Catatan: konstanta luminans referensi master jubah masih salinan badan (tingkat terang recolor bisa sedikit beda; cukup diatur warnanya) |
| **LOD** | `Art/Scripts/jayadwara2_cape_16_make_lods.py` → `SK_Jayadwara2_Cape_LOD1/2.fbx` 14.620 / 7.018 tris (LOD0 29.244); validator 27/27 ×3; impor UE 3 level (layar 1,0/0,5/0,25). Pembanding `_jd2c/_lod_banding.png` |
| **Bros** | Pelat dasar + bezel tinggi + bintang 8 ujung (4 panjang, 4 pendek) + permata merah berfaset |
| **Bersih-bersih** | 2 lubang kecil (sisa bukaan ornamen Tripo di area yang direntangkan) ditutup otomatis (`holes_fill` ≤ 20 sisi, UV merah) |
| **Cek IP (K9)** | Kerah dijepit **≤ 1,600 m** (dagu 1,613) setelah penghalusan; tidak mekar ke belakang kepala; bukan senjata ✅ |
| **Impor UE** | `ue_import_jayadwara2_cape.py` kini **impor ulang di tempat** (skeleton yang ada dipakai); menghapus lalu mengimpor nama yang sama gagal karena importer "atomic reimport" ke objek lama yang masih di memori (butuh restart editor bila terlanjur). Diuji 2× berturut-turut stabil. Membuat `MI_Jayadwara2_Cape_TesWarna` |
| Diterima apa adanya | Tekstur bagian atas yang direntangkan ×1,8 (ornamen emas kecil di panel sedikit memanjang); tepi atas kain terbuka (dihaluskan, tidak ditutup list — developer tidak ingin garis kuning) |

**Gate J2 (developer):** validator lulus ✅, cek IP ✅; tinggal tuning warna di MI (opsional) & persetujuan. Gambar: `Art/Export/_jd2c/_ue_j2.png`.

### Catatan 14 Okt 2026 — jubah dibangun ulang di atas badan v06
Badan Jayadwara2 direvisi (docs/25 R7: kaki −4,5 cm, badan lebih panjang, kain tengah belakang). Pipeline jubah kini dijalankan di atas **`jayadwara2_v06_revisi.blend`** (`jayadwara2_cape_01_intake.py` dibuka pada file itu); hasil 29.184 / 14.590 / 7.002 tris, validator 27/27 ×3, terpasang di UE. Pipeline lain tidak berubah.
### Catatan 14 Okt 2026 — lengan menembus jubah & modul node
- **Lengan menembus jubah** (lapel/panel samping saat idle): `jayadwara2_cape_10_fit_rig.py` langkah `arm_clear` — kapsul lengan (upperarm, lowerarm, tangan+jari per sisi; radius p90 kulit lengan + 3 cm) dari pose rest; vertex jubah di dalamnya didorong ke **belakang** (+Y) sampai keluar kapsul, disamakan setebal lembar lalu disebar halus. 1.409 vertex di dalam lengan, dorongan maks 23 cm. Jubah di sisi lengan kini lebih ramping/berada di belakang lengan (`Art/Export/_jd2c/_ue_lengan.png`). Validator 27/27 ×3.
- **Node "JD Cape Chains" dipindah ke modul `JayadwaraAnimNodes` (UncookedOnly)** — sebelumnya di modul Editor sehingga compiler ABP memperingatkan *"from an Editor Only module, but is placed in a runtime blueprint"* (ABP gagal saat cook/package). Modul baru terdaftar di `Jayadwara.uproject` & `JayadwaraEditor.Target.cs`; class redirect lama→baru di `Config/DefaultEngine.ini` `[CoreRedirects]`. Peringatan hilang.
- Peringatan Asset Check *"anim sequence asset has no Skeleton"* untuk `Jayadwara2/Anims/*` hanya muncul **sesaat** ketika `ue_import_jayadwara2.py` membuat ulang `SKEL_Jayadwara2`; hilang setelah `ue_setup_jayadwara2.py` me-retarget ulang (selalu jalankan setup setelah impor badan).
