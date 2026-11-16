# Import Jayadwara ke Unreal Engine 5.6

> Hasil **Iterasi 5**, **diuji & diperbaiki di Iterasi 6** (UE 5.6.1, 12 Okt 2026; [docs/13](../../docs/13-rencana-model-jayadwara.md)). Mesh diimpor di **skala 1**; skala raksasa ada di `AJDGiantCharacter`. Setelah import: `Tools/ue_setup_retarget.py` lalu `Tools/ue_setup_giant.py`.

## 1. Isi paket (`Art/Export/`)

| File | Isi |
|---|---|
| `SK_Jayadwara.fbx` | LOD0: skeletal mesh tunggal (51.808 tris, 4 slot material) + armature `Armature` 89 tulang (gaya UE5 Mannequin), data dalam cm, **tanpa** empty socket |
| `SK_Jayadwara_LOD1.fbx` … `_LOD3.fbx` | LOD1 ±26.000 · LOD2 ±11.800 · LOD3 ±5.400 tris. Skeleton sama. |
| `SK_Jayadwara_sockets.json` | 9 socket: tulang induk + posisi. UE **tidak** membuat socket skeletal mesh dari empty FBX. |
| `Textures/T_Jayadwara_<Slot>_<Mask\|BC\|N\|ORM>.png` + `T_Jayadwara_Face_Emit.png` | Tekstur 4 slot (spesifikasi: [docs/15](../../docs/15-spesifikasi-material-jayadwara.md)) |
| `../../Tools/ue_import_jayadwara.py` | Skrip Unreal Python yang menjalankan semua langkah di bawah |

Semua FBX lolos `validate_jayadwara.py` 27/27 (nama/jumlah tulang, 1 root, armature bernama `Armature`, tanpa empty, tinggi 1,99 m, ≤4 influence, bobot ternormalisasi, 0 vertex tanpa bobot, UV 0–1, socket di JSON).

Spesifikasi export (`05_export_fbx.py`, revisi Iterasi 6): Z-up, depan -Y (Blender), salinan armature+mesh diskalakan ×100 lalu di-apply, objek armature bernama `Armature`, `FBX_SCALE_ALL`, tanpa leaf bone, tanpa animasi, tanpa empty, tulang IK (`ik_foot_*`, `ik_hand_*`) ikut. Alasannya di docs/13 Iterasi 6.

## 2. Prasyarat

- UE **5.6.1**, project `Jayadwara` sudah dibuat.
- Plugin **Python Editor Script Plugin** aktif (Edit → Plugins), untuk opsi A.
- Tujuan konten (docs/12): `/Game/Jayadwara/Characters/Jayadwara/` dengan subfolder `Mesh/`, `Materials/`, `Textures/`.

## 3. Opsi A: skrip (disarankan)

Di Output Log, pilih mode **Python**:

```
py "C:/repository/unreal_engine/jayadwara/Tools/ue_import_jayadwara.py"
```

Yang dikerjakan skrip:
1. Impor tekstur dengan setelan docs/15:
   - BC: sRGB on.
   - Mask/ORM/Emit: sRGB off, kompresi Masks.
   - N: Normalmap + **Flip Green** (normal dari Blender berformat OpenGL).
2. Membuat `M_Jayadwara_Master` dan 4 material instance `MI_Jayadwara_<Slot>`. Cloth two-sided; Face `Emissive_Enable = 1`.
3. Menghapus isi `Mesh/` lalu mengimpor `SK_Jayadwara` di **skala 1** (lihat bagian 4) dengan physics asset. Material dari FBX tidak diimpor.
4. Impor LOD1–3 ke slot LOD dan set screen size awal 1,0 / 0,5 / 0,25 / 0,12.
5. Pasang MI ke slot material, rename skeleton → `SKEL_Jayadwara` dan physics asset → `PA_Jayadwara`.
6. Buat socket dari `SK_Jayadwara_sockets.json`.

Kalau ada langkah gagal, Output Log menampilkan baris **`[Jayadwara][MANUAL]`** berisi langkah penggantinya (lihat opsi B).

**Teruji di 5.6.1:** CVar `Interchange.FeatureFlags.Import.FBX` ada (skrip mematikannya sementara supaya opsi FBX lama berlaku); `SkeletalMeshEditorSubsystem.import_lod`, `SkeletalMesh.add_socket`/`rename_socket`, `AnimPoseExtensions` tersedia. Skrip berjalan tanpa `[MANUAL]`.

## 4. Skala raksasa

- Skala raksasa **di-bake di FBX** (`Art/Scripts/16_make_lods.py`, `GIANT_HEIGHT_M` = 45, placeholder): mesh di UE ±47,1 m termasuk tanduk, diimpor di skala 1, komponen mesh `BP_Jayadwara` berskala 1. Posisi di `SK_Jayadwara_sockets.json` sudah berskala sama (`export_scale`).
- **Jangan pakai Import Uniform Scale** (di UE 5.6.1 masuk ke skala tulang root) dan **jangan menskalakan komponen mesh** (Anim Dynamics rusak). Alasan & uji: docs/13 Iterasi 6.
- Gerak, kapsul, kamera dihitung di `AJDGiantCharacter` dari `GiantHeightCm` / `AuthoredHeightCm` (190). `MeshHeightCm` harus sama dengan `GIANT_HEIGHT_M` × 100.
- Ganti tinggi raksasa: ubah `GIANT_HEIGHT_M`, jalankan `16_make_lods.py` (Blender), lalu `ue_import_jayadwara.py` → `ue_setup_retarget.py` → `ue_setup_giant.py`; samakan `GiantHeightCm` & `MeshHeightCm`.

## 5. Opsi B: manual

**B1. Tekstur.** Seret semua `T_Jayadwara_*.png` ke `Textures/`, lalu atur:

| Akhiran | sRGB | Compression | Lainnya |
|---|---|---|---|
| `_BC` | on | Default | |
| `_N` | off | Normalmap | **Flip Green Channel** on |
| `_Mask`, `_ORM`, `_Emit` | off | Masks | |

**B2. Mesh.** Impor `SK_Jayadwara.fbx` ke `Mesh/`:
- Skeletal Mesh on; Import Uniform Scale **1** (FBX sudah 45 m, bagian 4); Convert Scene on.
- Create Physics Asset on; Import Animations off; Import Materials/Textures off.
- Normal Import Method: *Import Normals*.

**B3. LOD.** Buka `SK_Jayadwara`, lalu LOD Settings → LOD Import:
- Pilih *LOD 1*, ambil `SK_Jayadwara_LOD1.fbx`. Ulangi untuk LOD 2 dan 3.
- Screen Size: 1,0 / 0,5 / 0,25 / 0,12 (titik awal, tuning di level uji).
- Fallback kalau impor LOD bermasalah: *LOD Settings → Number of LODs 4* (reduksi bawaan UE). Hasilnya kurang terkontrol, misalnya berlian lutut bisa pecah.

**B4. Material.**
- Buat `M_Jayadwara_Master` sesuai docs/15 bagian 2. Rumusnya:
  - Base Color = lerp(lerp(lerp(`Color_Black`, `Color_Red`, Mask.R), `Color_Gold`, Mask.G), `Color_White`, Mask.A) × BC × ORM.R.
  - Roughness = ORM.G, Metallic = ORM.B, Normal = N.
  - Emissive = `Emissive_Color` × Emit.R × `Emissive_Intensity` × `Emissive_Enable`.
  - Centang *Used with Skeletal Mesh*.
- Buat 4 MI (`MI_Jayadwara_Body/Armor/Cloth/Face`) dan isi parameter tekstur per slot.
- Cloth: *Material Property Overrides → Two Sided*. Face: `Emissive_Enable = 1`.
- Pasang MI ke slot dengan nama yang sama di `SK_Jayadwara`.

**B5. Socket.** Di Skeleton Tree, *Add Socket* pada tulang berikut. Posisi di tabel dalam cm skala model 1,90 m; kalikan `export_scale` (≈23,68), atau pakai nilai `ue_component_cm` di JSON. Pindahkan socket ke titik ini dengan gizmo:

| Socket | Tulang | Posisi komponen (cm, skala 1) |
|---|---|---|
| `hand_l` / `hand_r` | `hand_l` / `hand_r` | lihat `SK_Jayadwara_sockets.json` |
| `foot_l` / `foot_r` | `foot_l` / `foot_r` | 〃 |
| `chest_sun` | `spine_05` | (0; 17,6; 148) |
| `eye_l` / `eye_r` | `head` | (±5; 12; 178) |
| `head_top` | `head` | (0; 0; 190) |
| `back_center` | `spine_04` | (0; −13; 145) |

**B6. Nama.** Rename `SK_Jayadwara_Skeleton` → `SKEL_Jayadwara`, `SK_Jayadwara_PhysicsAsset` → `PA_Jayadwara` (usulan konvensi docs/12).

## 6. Retarget animasi dari Mannequin

- Nama dan hierarki tulang mengikuti UE5 Mannequin (`pelvis`, `spine_01…05`, `neck_01…02`, `head`, `clavicle`/`upperarm`/`lowerarm`/`hand`, jari 3 ruas, twist, `ik_*`).
- Buat `IK_Jayadwara` (IK Rig: chain spine, neck, lengan, kaki, jari) dan `RTG_Mannequin_To_Jayadwara` (IK Retargeter, sumber `IK_Mannequin`).
- Pose rest Jayadwara: **A-pose lengan 30°**. Samakan dengan pose referensi Mannequin di tab *Retarget Pose* sebelum menilai hasil.
- Tulang tambahan (`scarf_l/r_01…06`, `cloth_front/back_01…03`) tidak ada di Mannequin. Biarkan tanpa chain; nanti digerakkan Anim Dynamics/Rigid Body di ABP.

## 7. Checklist verifikasi (Iterasi 6)

Status 12 Okt 2026 (dicek Claude lewat Python + capture; detail di docs/13 Iterasi 6):

- [x] Karakter berdiri di z=0, menghadap **+Y** (sama seperti Mannequin), ±47,1 m (mesh ter-bake).
- [x] 4 LOD ada, screen size 1,0 / 0,5 / 0,25 / 0,12; tidak meloncat saat pindah LOD (dicek developer).
- [x] 4 slot material terpasang MI yang benar; emas tidak tampak silver; mata & permata dada menyala konstan (aturan IP).
- [x] Normal tidak terbalik (Flip Green on).
- [x] 9 socket di tulang yang benar (posisi dari JSON; konversi (x, −y, z) × 100 terverifikasi).
- [x] Physics asset dirapikan (20 kapsul, tanpa kain/selendang; `ue_setup_giant.py`).
- [x] Retarget animasi jalan/pukul dari Mannequin: posisi tulang selisih beberapa cm dari Manny (op Run IK Rig dimatikan); tangan tidak menembus badan (dicek developer).
- [x] Performa di `Test_GiantScale` 60 FPS (dicek developer).

## 8. Catatan & keterbatasan

- Pose lengan terangkat penuh: tutup pauldron sebagian masuk ke badan dan menempel ke kerah. Kandidat perbaikan: tulang bantu bahu atau corrective, setelah dilihat dengan animasi sungguhan (docs/13).
- LOD3 sedikit belang di paha karena normal halus ikut di-decimate. Masih wajar untuk jarak jauh.
- Tekstur masih versi otomatis (hand-paint belum).
- File Blender sumber: `Art/Blender/jayadwara/jayadwara_giant_v05_revisi.blend`. Untuk membangun ulang paket: `Art/Scripts/16_make_lods.py` (urutan lengkap di `Art/README.md`).

## 9. Tuyul (16 Okt 2026)

Paket Tuyul di `Art/Export/`: `SK_Tuyul`, `SK_TuyulBesar`, `SK_TuyulRaksasa` (+ `_LOD1..3`), `SK_Tuyul*_sockets.json` (8 socket, `ue_component_cm` sudah dikali skala), dan `Textures_Tuyul/T_Tuyul_{Color,N,ORM,Emit}.png`. Ukuran di-bake di FBX (100 cm / 2700 cm / 4500 cm), **bukan** skala actor. Skeleton 52 tulang bernama Mannequin + `jaw`, tangan 3 jari. Impor lewat `Tools/ue_import_tuyul.py` lalu `Tools/ue_setup_tuyul.py`; kombinasi wajib sama seperti Aksa2 (`BAKE_CM`=100 di FBX, importer FBX lama, Compatible Skeleton SK_Mannequin tersimpan di `SKEL_Tuyul`). Detail, uji, dan risiko: [docs/27](../../docs/27-rencana-model-tuyul.md).
