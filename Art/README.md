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
- **Versi:** simpan versi baru (`v01`, `v02`, …) di akhir langkah besar; jangan menimpa versi yang sudah disetujui.
- **Sumber kebenaran:** setelah sebuah iterasi disetujui, `.blend` adalah sumber kebenaran. Script hanya membuat basis; jangan jalankan ulang di atas hasil edit manual.
- **Git:** `.blend`, `.fbx`, `.png` lewat Git LFS (`.gitattributes`). File cadangan `*.blend1` di-ignore. Jalankan `git lfs install` sekali sebelum commit pertama.
- **Referensi:** buat ulang dengan `python -I Art/Scripts/make_reference_planes.py` (butuh `pillow`, `numpy`, `scipy`).

## Aksa — urutan dan impor (Iterasi 1)
Urutan: `aksa_00_setup_scene.py` (headless, `aksa_v00_setup.blend`) → buka v00 di Blender → `aksa_10_armature.py` → `aksa_11_proxy.py` → `aksa_20_head.py` (Iterasi 2, menyimpan v02) → `aksa_13_pose_tests.py` → `aksa_14_export.py` (untuk WIP: set `FBX_OUT`/`MESH_NAME` = `Art/Export/SK_Aksa_WIP.fbx` / `SK_Aksa_WIP` sebelum exec) → `validate_aksa.py`. Render banding: `aksa_12_render.py` (headless, argumen `-- <outdir> [pose]`) lalu `python -I Art/Scripts/aksa_12_compare_sheet.py <outdir>`.
Impor ke Unreal (editor terbuka, **tidak sedang Play**): `python Tools/ue_remote.py Tools/ue_import_aksa.py` (mesh + LOD1–3 ke skeleton `SK_Mannequin` asli; tulang `sash_*`/`jacket_*` tergabung ke skeleton itu), lalu `python Tools/ue_remote.py Tools/ue_setup_aksa.py` (PA_Aksa, ABP_Aksa + Anim Dynamics jaket, BP_Aksa memakai SK_Aksa, potret dialog) lalu cek visual `python Tools/ue_remote.py Tools/ue_check_aksa.py` (hapus actor uji + pulihkan kamera: `-c "CLEAN=True; exec(open(r'<path ue_check_aksa.py>').read())"`).
Spike skeleton (hanya perlu diulang kalau Manny/UE berubah): `Tools/ue_export_manny.py` → `aksa_spike_analyze_manny.py` → `aksa_spike_roundtrip.py` → `Tools/ue_spike_aksa_import.py` → `aksa_spike_compare.py`.

## Asal aset pihak ketiga
| Aset | Sumber | Lisensi | Dipakai untuk |
|---|---|---|---|
| MPFB 2.0.18 (MakeHuman untuk Blender) | extensions.blender.org, `add-on-mpfb-v2.0.18.zip`, SHA-256 `c075b3e9b94b8e5556a5f03f4653602d02ea306de08126e8f55ed6dee28a2dad` | Kode GPLv3 (hanya dijalankan di Blender, tidak didistribusikan di game); **base mesh & target CC0** | Basis kepala + leher Aksa (`aksa_22_mpfb_head.py`) |
| UE5 Mannequin (`SKM_Manny_Simple`, `SK_Mannequin`) | Template Third Person UE 5.6 | Lisensi Epic (aset Unreal) | Skeleton Aksa; LOD2 Manny hanya hantu referensi di `.blend` |
