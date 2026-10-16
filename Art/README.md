# Art — sumber aset 3D (di luar `Content/` Unreal)

Folder ini berisi file sumber untuk aset yang dibuat di Blender 5.2. Unreal hanya membaca `Content/`, jadi folder ini aman di luar project UE.
Rencana lengkap: [docs/13-rencana-model-jayadwara.md](../docs/13-rencana-model-jayadwara.md) · Model sheet: [docs/14-model-sheet-jayadwara.md](../docs/14-model-sheet-jayadwara.md)
Model Aksa: rencana [docs/19-rencana-model-aksa.md](../docs/19-rencana-model-aksa.md) · model sheet [docs/21-model-sheet-aksa.md](../docs/21-model-sheet-aksa.md)

| Folder | Isi |
|---|---|
| `Reference/` | Referensi ortografis & detail: `jd_*` (dari `jayadwara_final.webp`), `ak_*` (dari `aksa_turnaround_v01.webp`), `manny/` (hasil spike) |
| `Blender/` | File `.blend` berversi: `jayadwara_giant_vNN_<tahap>.blend` |
| `Scripts/` | Script Python Blender (modeling, rig, validasi) dan alat bantu referensi |
| `Export/` | Hasil export FBX + tekstur siap import UE |
| `Level/` | Data tata letak map per episode (sumber kebenaran untuk greybox Blender/UE): `ep01_medan.py` (fungsi tinggi medan + uji), `ep01_layout_v01.json` (objek, penanda, kamera). Desain: [docs/30](../docs/30-desain-level-ep01.md) |

## Script (`Scripts/`)
Dijalankan di Blender (mis. lewat MCP: `exec(open(path).read())`), kecuali yang ditandai *sistem*.

| Script | Fungsi |
|---|---|
| `make_reference_planes.py` *(sistem)* | Membuat referensi ortografis dari sheet konsep |
| `00_setup_scene.py` | Scene awal: satuan, collection, reference plane, landmark |
| `jd_common.py`, `jd_skeleton.py` | Modul bersama: warna, material, primitif; posisi sendi & nama tulang |
| `01_blockout.py` | Bangun proxy (43 bagian, 4 material) |
| `02_rig.py` | Armature 89 tulang (twist, jari, IK), skin weight (heat-map + smoothing), socket |
| `03_pose_tests.py` | Action `JD_PoseTest` (13 pose, frame 1 = A-pose) |
| `06_deform_check.py` | Ukur peregangan undersuit (cm absolut) dan penetrasi baru antar-armor di semua pose |
| `04_silhouette_export.py` + `silhouette_compare.py` *(sistem)* | Bandingkan siluet dengan referensi (IoU) |
| `jd_hero.py` | Library hard-surface: tube/loft, plat melengkung (patch), kurva menempel di permukaan, solidify+bevel |
| `10_hero_body.py` … `14_hero_leg.py` | Hero modeling Iterasi 2 per kelompok: undersuit, kepala, torso+bahu, lengan+sabuk+kain, kaki (bangun di atas v01 → simpan v02) |
| `15_body_fit.py` | Tempelkan undersuit ke zirah (celah ±8 mm) + catat sumber dorongan; `02_rig` lalu mewariskan bobot zirah ke otot di bawahnya. Jalankan setelah `10`–`14` (undersuit baru dari `10`) dan sebelum `02` |
| `07_uv_unwrap.py` | UV: unwrap + packer sendiri per slot material; menulis UV ke tiap bagian dan NPZ per-muka |
| `make_textures.py` *(sistem)* | Tekstur dari NPZ: Mask, BC (batik kawung), N, ORM (+AO bake), Emit → `Export/Textures/` |
| `08_materials.py` | Material Blender berbasis tekstur, meniru master material UE (docs/15) |
| `09_bake_ao.py` | Bake AO (Cycles) ke `Export/Textures/_bake/` |
| `05_export_fbx.py` | Export FBX. Proxy: default (`SK_Jayadwara_Proxy`). Hero: pakai `16_make_lods.py` (memanggil skrip ini per LOD lewat `PREP`) |
| `16_make_lods.py` | Iterasi 5: paket export final `Export/SK_Jayadwara.fbx` (LOD0) + `_LOD1..3.fbx` (decimate per bagian, bobot dibersihkan) + `SK_Jayadwara_sockets.json` |
| `make_reference_planes_aksa.py` *(sistem)* | Aksa: referensi ortografis ternormalisasi (1000 px = 1,75 m) dari turnaround → `Reference/ak_*.png` |
| `make_reference_planes_jerangkong.py` *(sistem)* | Jerangkong: referensi ortografis ternormalisasi (1000 px = 2,2 m) + crop detail + palet → `Reference/jk_*.png` |
| `jerangkong_00_setup_scene.py` | Jerangkong Iterasi 0: scene `jerangkong_v00_setup.blend` (collection per kelompok potongan, reference plane, penggaris 2,2 m, landmark `JK_LM_*`, target bungkuk sedang `JK_TGT_*`). Headless: `blender --background --factory-startup --python Art/Scripts/jerangkong_00_setup_scene.py` |
| `jerangkong_01_import_tripo.py` | Jerangkong jalur B: impor `Source/jerangkong_tripo_v01.glb` (Tripo) → `jerangkong_v01_tripo.blend` (`JK_Source`, menghadap -Y, 2,19 m) |
| `jayadwara2_01_import_tripo.py` *(headless)* | Redesign Jayadwara (docs/25 R0): impor GLB Tripo developer → `jayadwara2_v01_tripo.blend` (`JD2_Source`) + laporan tris/tekstur/pulau/non-manifold/simetri/arah hadap. Argumen `-- --src --out --top-z --rot-z` |
| `jd2_skeleton.py` | Jayadwara2: skeleton 89 tulang (nama & hierarki = `jd_skeleton.py`), sendi diukur dari mesh Tripo (landmark `LM`) |
| `jayadwara2_02_render_views.py` | R0: render ortografis depan/samping/belakang + 3/4 + kepala (Workbench, tekstur apa adanya) → `Export/_jd2/` |
| `jayadwara2_03_measure.py` / `_04_uv_islands.py` | R0: ukur proporsi, celah pose, warna tekstur, pulau UV |
| `jayadwara2_10_rig_spike.py` *(headless)* | R1: skeleton + split jahitan sentuh + bobot kapsul bertetangga → `jayadwara2_v02_rig_spike.blend` |
| `jayadwara2_11_macro_render.py` | R1: peta pembagian bagian berwarna (cek klasifikasi) |
| `jayadwara2_20_thickness.py` | R2: ketebalan lokal (ray ±normal) → peta lembar tipis `Export/_jd2/_thick.png` |
| `jayadwara2_21_rig_r2.py` *(headless)* | R2: rig = skeleton + lembar kain via ketebalan + split jahitan + buang sliver + zirah kaku → `jayadwara2_v03_rig_r2.blend` (menggantikan `_10_rig_spike`) |
| `jayadwara2_22_rig_r3.py` *(headless)* | R3: R2 + bobot twist + sayap/kain ikut paha + zona sendi dilunakkan → `jayadwara2_v05_rig_r3.blend` (menggantikan `_21_rig_r2`; pose uji kini memisahkan badan vs kain) |
| `jayadwara2_23_revisi_badan.py` *(headless)* | R7 (14 Okt): v05 → `jayadwara2_v06_revisi.blend` — kaki −4,5 cm / pinggul→dada ×1,107 (tinggi tetap, lengan tidak ikut), kain tengah belakang opsional (dibatalkan developer → jalankan dengan `-- --no-back`). badan v06 (tanpa helai belakang) |
| `jayadwara2_24_armpit_audit.py` *(headless)* | R8: audit ketiak — tepi terbuka + render close-up ketiak kanan (Workbench, backface culling) di 6 pose lengan → `Export/_jd2/armpit` (argumen outdir, pakai path absolut) |
| `jayadwara2_25_ketiak.py` *(headless)* | R8 (13 Okt): v06 → `jayadwara2_v07_ketiak.blend` — tutup lubang ketiak (jahit rel lengan↔badan, 4 baris, bobot interpolasi + cincin dihaluskan, UV texel bodysuit gelap). **Badan aktif = v07**: export/LOD dijalankan pada file ini |
| `jayadwara2_16_make_lods.py` *(headless)* | R5: LOD1–3 (`SK_Jayadwara2_LOD1..3.fbx`, 18,7k/8,6k/3,7k tris) lewat Decimate + grup `LODPROTECT` (invert!) + ekspor kontrak sama; render perbandingan `_lod_*.png` |
| `jayadwara2_17_walk_head_tests.py` | R3c: uji langkah jalan & kepala miring besar (menangkap bug sayap berserakan, dagu tertinggal) → `_walk_*`, `_tilt_*` |
| `jd2_atlas.py` / `analyze_atlas_jayadwara2.py` | R4: posisi 3D per texel + zona warna HSV; analisis atlas → `Export/_jd2/_atlas_zones.png` |
| `make_textures_jayadwara2.py` | R4: BC (snap peralihan, soket mata dari `BC_src`), `T_Jayadwara2_Emit` (permata, mata), `T_Jayadwara2_Mask` (RGBA zona) + `.json` (butuh `_15_dump_uv`) |
| `jayadwara2_30_materials.py` | R4: material preview Blender meniru UE → `jayadwara2_v04_tex.blend` + render `_bl_*.png` |
| `jayadwara2_13_pose_tests.py` | R1: 13 pose (pakai `03_pose_tests.py`) + tabel peregangan + contact sheet `Export/_jd2/poses/` |
| `jayadwara2_14_export.py` | R1: `SK_Jayadwara2.fbx` + `_sockets.json` + `Textures_Jayadwara2/` (validator: `--materials 1 --no-zone --max-tris 100000`) |
| `jayadwara2_cape_01_intake.py` *(headless, di atas `jayadwara2_v05_rig_r3.blend`)* | Jubah J0 (docs/26): impor `Source/jayadwara2_cape_tripo_v01.glb` (= `yahya_design/cap02.glb`), putar +90°, kerah 1,60 / ujung 0,10 m, buka depan 55°, fit `--fit sx,sy,dy` (default 1.1,1.25,0.02) → `jayadwara2_cape_v00_intake.blend` (`JD2_Cape_Source` + `JD2C_ANCHOR_*`) + laporan jarak per zona & titik kait. File rig final tidak ditimpa |
| `jayadwara2_cape_02_render.py` | Jubah J0: badan + jubah depan/samping/belakang/3/4/kerah dengan titik kait (kuning), garis dagu (biru), mata kaki (hijau) → `Export/_jd2c/jd2c_<tag>_*.png`; `--no-cape` untuk badan saja |
| `jayadwara2_cape_10_fit_rig.py` *(headless, di atas `jayadwara2_cape_v00_intake.blend`)* | Jubah J1/J1b/J1c: yoke leher/bahu + bros + hiasan puncak dibangun dari skrip (J1c), bobot bawah ke rantai `cape_*` (`--skin chains`, bawaan J1c; `kinematic` = J1), buang sisa panel di sumbu tubuh + depan pita kerah (J1b), gulungan bahu/leher dipadatkan ×0,12 (J1b), fit lokal radial (lambung badan tanpa lengan & pauldron, jarak bebas 2,5 cm / kerah 1,2 cm), `JD2C_Armature` = 89 tulang badan + rantai `cape_{c,l,r,fl,fr}_01..06` (berbobot 0, untuk J3) dengan Copy Transforms ke `JD2_Armature`, bobot kinematik (kulit terdekat → pelvis/spine jauh, kaki ≤ 0,6) → `jayadwara2_cape_v01_rig.blend`. Opsi `--leg-max --near-d1 --no-calf` |
| `jayadwara2_cape_11_pose_tests.py` | Jubah J1: 9 pose (jalan, lari, tendang, jongkok, putar, lengan, kepala) → `Export/_jd2c/poses/<tag>_<pose>.png` + tabel tembus kapsul kaki & regangan |
| `jayadwara2_cape_14_export.py` | Jubah J1: `SK_Jayadwara2_Cape.fbx` (119 tulang) + `_sockets.json` (skala) + `Textures_Jayadwara2_Cape/` (BC/N/ORM Tripo + Emit/Mask datar). Validasi: `validate_jayadwara.py -- Art/Export/SK_Jayadwara2_Cape.fbx --materials 1 --no-zone --max-tris 60000 --height 1.50 --zmin 0.10 --extra-bone-prefix cape_ --no-sockets` (27/27). UE: `python Tools/ue_remote.py Tools/ue_import_jayadwara2_cape.py` lalu `Tools/ue_setup_jayadwara2_cape.py` (setup wajib diulang setelah impor ulang); bukti visual `Tools/ue_capture_jayadwara2_cape.py` (CAP_STAGE setup lalu shoot; `CAP_DISSOLVE=[...]` = deret uji lepas). Impor juga membuat `M_Jayadwara2_Cape_Master` (dissolve, J1b); setup menyisipkan node simulasi "JD Cape Chains" (J1c). Uji jatuh: `Tools/ue_probe_jayadwara2_cape.py` (PROBE_STAGE place → start → read… → stop) |
| `make_textures_jayadwara2_cape.py` *(python -I)* | Jubah J2: `T_Jayadwara2_Cape_Mask.png` (R merah, G emas, A putih) + `_Mask.json` dari BC; jalankan setelah `jayadwara2_cape_14_export.py` (export tidak menimpa Mask yang sudah ada) |
| `jayadwara2_cape_16_make_lods.py` *(headless)* | Jubah J2: `SK_Jayadwara2_Cape_LOD1/2.fbx` (Decimate 0,50/0,24) lewat export yang sama + `_jd2c/_lod_*` |
| `jk_skeleton.py`, `jk_segment.py` | Jerangkong: posisi sendi terukur + daftar potongan/socket; segmentasi mesh ke tulang (numpy) |
| `jerangkong_10_build.py` *(Blender headless)* | Rig + 17 potongan kaku + cap + bobot + socket → `jerangkong_v02_rig.blend`, `Export/_jk_faces.npz` |
| `make_textures_jerangkong.py` *(sistem)* | Tekstur dari atlas Tripo: BC dibersihkan, Emit (R Kala / G retak / B gelang), N, ORM → `Export/Textures_Jerangkong/` |
| `jerangkong_12_materials.py`, `jerangkong_13_pose_tests.py` | Material `M_Jerangkong` (meniru master UE); 7 pose uji (render Eevee, argumen `-- <outdir>`) |
| `jerangkong_14_export.py` | SK boss (×14) & minion (×0,85) LOD0–3, 14 `SM_Jerangkong_*`, `parts.json`, `sockets.json` |
| `validate_jerangkong.py` *(Blender headless)* | Validasi FBX Jerangkong (`-- Export/SK_Jerangkong.fbx --parts` untuk cek pivot SM) |
| `aksa_00_setup_scene.py` | Aksa Iterasi 0: scene `aksa_v00_setup.blend` (collection, reference plane, penggaris 1,75 m, landmark `AK_LM_*`). Headless: `blender --background --factory-startup --python Art/Scripts/aksa_00_setup_scene.py` |
| `aksa_spike_analyze_manny.py` *(Blender headless)* | Aksa spike S2: analisis FBX Manny dari `Tools/ue_export_manny.py` → `Reference/manny/manny_rest.json` |
| `aksa_spike_roundtrip.py`, `aksa_spike_compare.py` *(Blender headless)* | Aksa spike S3/S4: export uji sesuai kontrak (+ tulang `root`), lalu banding pose referensi hasil impor/ekspor UE dengan Manny |
| `ak_common.py` | Aksa: modul bersama (tinggi 1,806 m, K, warna zona, 5 slot material, bobot jarak/haluskan, segmen tulang, jalur selendang) |
| `aksa_10_armature.py` | Aksa Iterasi 1: skala referensi, impor Manny, tulang `root` + `sash_01..06` → `aksa_v01_proxy.blend` |
| `aksa_11_proxy.py` | Aksa Iterasi 1: proxy 30 bagian (3.094 tris, 5 slot) ter-skin ke armature Manny |
| `aksa_12_render.py` + `aksa_12_compare_sheet.py` | Aksa: render ortografis depan/samping/belakang (opsional per pose) + lembar perbandingan konsep vs proxy dan IoU (`Export/_compare_aksa_proxy_*.png`) |
| `aksa_13_pose_tests.py` | Aksa: 6 uji pose silat (action `AK_PoseTest`) + peregangan tepi (cm) |
| `aksa_14_export.py` | Aksa: export `Export/SK_Aksa_Proxy.fbx` (kontrak: `root` tulang sungguhan, objek `Armature`, cm, `FBX_SCALE_ALL`) + `_sockets.json` |
| `ak_head.py`, `ak_hair.py` | Aksa Iterasi 2: pembangun kepala (loft cincin + fitur wajah analitik; angka di `KEYS`/`feature`) dan rambut (tudung + gumpalan, seed tetap) |
| `aksa_20_head.py` | Aksa Iterasi 2: ganti proxy kepala dengan kepala, telinga, mata, alis, rambut, leher → `aksa_v02_head.blend` (jangan jalankan ulang di atas hasil sculpt manual) |
| `ak_cloth.py`, `aksa_30_outfit.py` | Aksa Iterasi 3: pakaian hero + tangan metaball (loft terbuka, solidify, pelat menempel permukaan, dorong-keluar antar lapisan) → `aksa_v04_outfit.blend` |
| `aksa_40_rig.py` | Aksa Iterasi 4: tulang twist deform, rantai `jacket_*`, bobot ulang lengan/tangan/kaki/ujung jaket (jalankan setelah `aksa_30`) |
| `aksa_24_face.py` | Aksa revisi wajah di file kerja v05: alis busur tipis, senyum tipis dipanggang ke Basis, mata lebih terbuka (idempoten; lalu `aksa_50` → textures → `aksa_51` → export) |
| `ak_hair5.py` | Aksa rambut gaya 5 (aktif, dipanggil `aksa_22`): low fade (warna vertex kulit kepala) + atas bertekstur 950 helai |
| `ak_hair4.py`, `aksa_23_hair4.py` | Aksa rambut gaya 4 (aktif): cangkang gaya 3 + 1000 helai pita meruncing; `aksa_23` mengganti rambut di file kerja tanpa mengulang kepala/pakaian (lalu ulangi `aksa_50` → textures → `aksa_51` → export) |
| `aksa_50_uv.py` | Aksa Iterasi 5: UV per slot (smart_project + packer sendiri, mata planar) + NPZ `Export/_uv_faces_aksa.npz` → `aksa_v05_tex.blend` (jangan ulang setelah developer mengecat) |
| `make_textures_aksa.py` | Aksa Iterasi 5: tekstur dasar `Export/Textures_Aksa/T_Aksa_<Slot>_<BC\|N\|ORM\|SSS\|Mask>.png` dari NPZ (Python sistem: `python -I`) |
| `aksa_51_materials.py` | Aksa Iterasi 5: material Blender bertekstur meniru `M_Aksa_Master` UE |
| `aksa_60_lods.py` | Aksa Iterasi 6: paket final `Export/SK_Aksa.fbx` (LOD0 + morph) + `SK_Aksa_LOD1..3.fbx` + socket JSON (validasi tiap LOD dengan `--max-tris`) |
| `aksa_61_portraits.py` | Aksa Iterasi 6: potret dialog netral/senyum/marah → `Export/Portraits/` (headless dari `aksa_v05_tex.blend`) |
| `aksa_41_render_morphs.py` + `aksa_41_morph_sheet.py` | Aksa: render 8 morph target wajah + grid (`Export/_aksa_morphs.png`) |
| `aksa_31_render_body.py` | Aksa: render badan Eevee 3/4 depan/belakang + close-up tangan & boots |
| `ak_hair3.py` | Aksa rambut gaya 3 (aktif): disisir ke belakang + belahan samping, helai sejajar, tepi ditempel ke kurva garis rambut |
| `aksa_22_mpfb_head.py`, `ak_hair2.py` | Aksa Iterasi 2 putaran 2: kepala dari MPFB (MACRO + TARGETS wajah, dipetakan ke ukuran konsep) + rambut gaya textured crop (cangkang + gumpalan mengikuti aliran) → `aksa_v03_mpfb.blend`. Butuh ekstensi MPFB aktif |
| `aksa_21_render_head.py` + `aksa_21_head_sheet.py` | Aksa: render kepala berbingkai sama dengan `ak_head_*.png` (depan, samping, 3/4; Eevee headless) + lembar konsep vs model (`Export/_compare_aksa_kepala.png`) |
| `validate_aksa.py` *(Blender headless)* | Validasi FBX Aksa terhadap Manny (17 cek): `blender --background --factory-startup --python Art/Scripts/validate_aksa.py -- Art/Export/SK_Aksa_Proxy.fbx` |
| `validate_jayadwara.py` *(Blender headless)* | Validasi FBX: `blender --background --factory-startup --python Art/Scripts/validate_jayadwara.py -- Art/Export/SK_Jayadwara_Proxy.fbx` |

Urutan membangun ulang proxy: `01` → `02` → `03` → `05` → `validate`.
Urutan hero (di atas scene yang sudah ada 00): `10` → `11` → `12` → `13` → `14` → `15` → `02` → `03` → `06` → `07` → `make_textures` → `09` → `make_textures` → `08` → `16` (LOD0–3) → `validate` tiap FBX (`--max-tris` 100000 / 30000 / 14000 / 6000).
Import ke Unreal: `Export/README_IMPORT_UE.md` + `Tools/ue_import_jayadwara.py` (belum diuji). Catatan: `15` mengubah undersuit di tempat, jadi setiap kali `15` dijalankan ulang, jalankan `10` dulu.

## Aturan
- **Satuan:** 1 unit Blender = 1 m. Tinggi Jayadwara = **1,90 m** (telapak kaki → puncak helm, tanpa tanduk). Skala raksasa diterapkan di Unreal saat import.
- **Penamaan objek:** `JD_<Kelompok>_<Bagian>_<L|R>` (mis. `JD_Armor_Pauldron_L`); Aksa: awalan `AK_` (tinggi **1,75 m**, ujung rambut tertinggi).
- **Folder per karakter (15 Okt 2026):** `.blend` disimpan di `Art/Blender/<karakter>/` (`aksa/`, `aksa2/`, `jayadwara/`, `jayadwara2/` termasuk jubah, `jerangkong/`). Karakter baru = folder baru (buat folder dulu sebelum skrip menyimpan). Path gambar di dalam `.blend` relatif terhadap lokasi file (`//..\..\Export\...`), jadi jangan memindahkan `.blend` antar-kedalaman tanpa memperbaikinya (lihat skrip pemetaan ulang di riwayat sesi 15 Okt).
- **Versi:** simpan versi baru (`v01`, `v02`, …) di akhir langkah besar; jangan menimpa versi yang sudah disetujui.
- **Sumber kebenaran:** setelah sebuah iterasi disetujui, `.blend` adalah sumber kebenaran. Script hanya membuat basis; jangan jalankan ulang di atas hasil edit manual.
- **Git:** `.blend`, `.fbx`, `.png` lewat Git LFS (`.gitattributes`). File cadangan `*.blend1` di-ignore. Jalankan `git lfs install` sekali sebelum commit pertama.
- **Referensi:** buat ulang dengan `python -I Art/Scripts/make_reference_planes.py` (butuh `pillow`, `numpy`, `scipy`).

## Jerangkong — urutan (jalur B, model Tripo)
`blender --background Blender/jerangkong/jerangkong_v00_setup.blend --python Scripts/jerangkong_01_import_tripo.py` → `blender --background Blender/jerangkong/jerangkong_v01_tripo.blend --python Scripts/jerangkong_10_build.py` → `python -I Scripts/make_textures_jerangkong.py` → `jerangkong_12_materials.py` (pada v02) → `jerangkong_13_pose_tests.py -- <outdir>` → `jerangkong_14_export.py` → `validate_jerangkong.py` tiap FBX → UE: `python Tools/ue_remote.py Tools/ue_import_jerangkong.py` lalu `Tools/ue_setup_jerangkong.py` (setup wajib diulang setelah import ulang: skeleton dibuat ulang). Bukti visual: `Tools/ue_capture_jerangkong.py` (tahap `setup` lalu `shoot`).

## Aksa — urutan dan impor (Iterasi 1)
Urutan: `aksa_00_setup_scene.py` (headless, `aksa_v00_setup.blend`) → buka v00 di Blender → `aksa_10_armature.py` → `aksa_11_proxy.py` → `aksa_20_head.py` (Iterasi 2, menyimpan v02) → `aksa_13_pose_tests.py` → `aksa_14_export.py` (untuk WIP: set `FBX_OUT`/`MESH_NAME` = `Art/Export/SK_Aksa_WIP.fbx` / `SK_Aksa_WIP` sebelum exec) → `validate_aksa.py`. Render banding: `aksa_12_render.py` (headless, argumen `-- <outdir> [pose]`) lalu `python -I Art/Scripts/aksa_12_compare_sheet.py <outdir>`.
Impor ke Unreal (editor terbuka, **tidak sedang Play**): `python Tools/ue_remote.py Tools/ue_import_aksa.py` (mesh + LOD1–3 ke skeleton `SK_Mannequin` asli; tulang `sash_*`/`jacket_*` tergabung ke skeleton itu), lalu `python Tools/ue_remote.py Tools/ue_setup_aksa.py` (PA_Aksa, ABP_Aksa + Anim Dynamics jaket, BP_Aksa memakai SK_Aksa, potret dialog) lalu cek visual `python Tools/ue_remote.py Tools/ue_check_aksa.py` (hapus actor uji + pulihkan kamera: `-c "CLEAN=True; exec(open(r'<path ue_check_aksa.py>').read())"`).
Spike skeleton (hanya perlu diulang kalau Manny/UE berubah): `Tools/ue_export_manny.py` → `aksa_spike_analyze_manny.py` → `aksa_spike_roundtrip.py` → `Tools/ue_spike_aksa_import.py` → `aksa_spike_compare.py`.

## Aksa2 (model Tripo, 15 Okt 2026)
Sumber `Source/aksa2_tripo_v01.glb`, file kerja final `Blender/aksa2/aksa2_v06_F4.blend`. Ekspor ulang: `blender --background Blender/aksa2/aksa2_v06_F4.blend --python Scripts/aksa2_export.py` (LOD0, `BAKE_CM=100`) lalu `... --python Scripts/aksa2_lods.py` (LOD1–3), validasi `validate_aksa.py -- <fbx> --slots M_Aksa2_Body --require-uv --max-tris 60000|25000|10000|4000`, impor UE `python Tools/ue_remote.py Tools/ue_import_aksa2.py`. Morph wajah: `blender --background --factory-startup --python Scripts/aksa2_40_morph.py` (v06 → `aksa2_v07_morph.blend`), lembar ekspresi `aksa2_41_render_morphs.py -- <outdir>` lalu `python -I Scripts/aksa2_41_render_morphs.py --sheet <outdir>`; ekspor/LOD memakai v07. Detail, vonis banding, dan jebakan impor: `docs/19` §12.

## Asal aset pihak ketiga
| Aset | Sumber | Lisensi | Dipakai untuk |
|---|---|---|---|
| MPFB 2.0.18 (MakeHuman untuk Blender) | extensions.blender.org, `add-on-mpfb-v2.0.18.zip`, SHA-256 `c075b3e9b94b8e5556a5f03f4653602d02ea306de08126e8f55ed6dee28a2dad` | Kode GPLv3 (hanya dijalankan di Blender, tidak didistribusikan di game); **base mesh & target CC0** | Basis kepala + leher Aksa (`aksa_22_mpfb_head.py`) |
| UE5 Mannequin (`SKM_Manny_Simple`, `SK_Mannequin`) | Template Third Person UE 5.6 | Lisensi Epic (aset Unreal) | Skeleton Aksa; LOD2 Manny hanya hantu referensi di `.blend` |
| Model awal Jerangkong (`Source/jerangkong_tripo_v01.glb`) | Dibuat developer dengan Tripo AI dari `docs/concept-art/jerangkong_v01.webp` (12 Okt 2026) | Paket akun developer mengizinkan pemakaian komersial (dikonfirmasi developer). Konten buatan AI wajib diungkapkan di formulir rilis Steam | Mesh & atlas tekstur Jerangkong/Kerangka (jalur B, docs/20) |
