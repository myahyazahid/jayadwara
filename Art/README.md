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
| `02_rig.py` | Armature 44 tulang, skin weight, socket |
| `03_pose_tests.py` | Action `JD_PoseTest` (6 pose) |
| `04_silhouette_export.py` + `silhouette_compare.py` *(sistem)* | Bandingkan siluet dengan referensi (IoU) |
| `05_export_fbx.py` | Export `Export/SK_Jayadwara_Proxy.fbx` |
| `validate_jayadwara.py` *(Blender headless)* | Validasi FBX: `blender --background --factory-startup --python Art/Scripts/validate_jayadwara.py -- Art/Export/SK_Jayadwara_Proxy.fbx` |

Urutan membangun ulang proxy: `01` → `02` → `03` → `05` → `validate`.

## Aturan
- **Satuan:** 1 unit Blender = 1 m. Tinggi Jayadwara = **1,90 m** (telapak kaki → puncak helm, tanpa tanduk). Skala raksasa diterapkan di Unreal saat import.
- **Penamaan objek:** `JD_<Kelompok>_<Bagian>_<L|R>` (mis. `JD_Armor_Pauldron_L`).
- **Versi:** simpan versi baru (`v01`, `v02`, …) di akhir langkah besar; jangan menimpa versi yang sudah disetujui.
- **Sumber kebenaran:** setelah sebuah iterasi disetujui, `.blend` adalah sumber kebenaran. Script hanya membuat basis; jangan jalankan ulang di atas hasil edit manual.
- **Git:** `.blend`, `.fbx`, `.png` lewat Git LFS (`.gitattributes`). File cadangan `*.blend1` di-ignore. Jalankan `git lfs install` sekali sebelum commit pertama.
- **Referensi:** buat ulang dengan `python -I Art/Scripts/make_reference_planes.py` (butuh `pillow`, `numpy`, `scipy`).
