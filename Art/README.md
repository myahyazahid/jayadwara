# Art — sumber aset 3D (di luar `Content/` Unreal)

Folder ini berisi file sumber untuk aset yang dibuat di Blender 5.2. Unreal hanya membaca `Content/`, jadi folder ini aman di luar project UE.
Rencana lengkap: [docs/13-rencana-model-jayadwara.md](../docs/13-rencana-model-jayadwara.md) · Model sheet: [docs/14-model-sheet-jayadwara.md](../docs/14-model-sheet-jayadwara.md)

| Folder | Isi |
|---|---|
| `Reference/` | Referensi ortografis & detail (diturunkan dari `docs/concept-art/jayadwara_final.webp`) |
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
| `validate_jayadwara.py` *(Blender headless)* | Validasi FBX: `blender --background --factory-startup --python Art/Scripts/validate_jayadwara.py -- Art/Export/SK_Jayadwara_Proxy.fbx` |

Urutan membangun ulang proxy: `01` → `02` → `03` → `05` → `validate`.
Urutan hero (di atas scene yang sudah ada 00): `10` → `11` → `12` → `13` → `14` → `15` → `02` → `03` → `06` → `07` → `make_textures` → `09` → `make_textures` → `08` → `16` (LOD0–3) → `validate` tiap FBX (`--max-tris` 100000 / 30000 / 14000 / 6000).
Import ke Unreal: `Export/README_IMPORT_UE.md` + `Tools/ue_import_jayadwara.py` (belum diuji). Catatan: `15` mengubah undersuit di tempat, jadi setiap kali `15` dijalankan ulang, jalankan `10` dulu.

## Aturan
- **Satuan:** 1 unit Blender = 1 m. Tinggi Jayadwara = **1,90 m** (telapak kaki → puncak helm, tanpa tanduk). Skala raksasa diterapkan di Unreal saat import.
- **Penamaan objek:** `JD_<Kelompok>_<Bagian>_<L|R>` (mis. `JD_Armor_Pauldron_L`).
- **Versi:** simpan versi baru (`v01`, `v02`, …) di akhir langkah besar; jangan menimpa versi yang sudah disetujui.
- **Sumber kebenaran:** setelah sebuah iterasi disetujui, `.blend` adalah sumber kebenaran. Script hanya membuat basis; jangan jalankan ulang di atas hasil edit manual.
- **Git:** `.blend`, `.fbx`, `.png` lewat Git LFS (`.gitattributes`). File cadangan `*.blend1` di-ignore. Jalankan `git lfs install` sekali sebelum commit pertama.
- **Referensi:** buat ulang dengan `python -I Art/Scripts/make_reference_planes.py` (butuh `pillow`, `numpy`, `scipy`).
