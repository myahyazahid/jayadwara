# Import Jayadwara ke Unreal Engine 5.6

> Hasil **Iterasi 5** ([docs/13](../../docs/13-rencana-model-jayadwara.md)). **Belum diuji di Unreal**: ditulis sebelum UE terpasang. Verifikasi di Iterasi 6 dengan checklist di bagian 5, lalu perbarui dokumen ini.

## 1. Isi paket (`Art/Export/`)

| File | Isi |
|---|---|
| `SK_Jayadwara.fbx` | LOD0: skeletal mesh tunggal (51.808 tris, 4 slot material) + armature 89 tulang (gaya UE5 Mannequin) + empty socket |
| `SK_Jayadwara_LOD1.fbx` … `_LOD3.fbx` | LOD1 26.013 · LOD2 11.762 · LOD3 5.365 tris. Skeleton sama. |
| `SK_Jayadwara_sockets.json` | 9 socket: tulang induk + posisi. UE **tidak** membuat socket skeletal mesh dari empty FBX. |
| `Textures/T_Jayadwara_<Slot>_<Mask\|BC\|N\|ORM>.png` + `T_Jayadwara_Face_Emit.png` | Tekstur 4 slot (spesifikasi: [docs/15](../../docs/15-spesifikasi-material-jayadwara.md)) |
| `../../Tools/ue_import_jayadwara.py` | Skrip Unreal Python yang menjalankan semua langkah di bawah |

Semua FBX lolos `validate_jayadwara.py` 25/25 (nama/jumlah tulang, 1 root, tinggi 1,99 m, ≤4 influence, bobot ternormalisasi, 0 vertex tanpa bobot, UV 0–1, socket).

Spesifikasi export: Z-up, depan -Y (Blender), skala 1 m, tanpa leaf bone, tanpa animasi, tulang IK (`ik_foot_*`, `ik_hand_*`) ikut.

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
3. Impor `SK_Jayadwara` dengan **Import Uniform Scale ≈ 23,68** (lihat bagian 4) dan physics asset. Material dari FBX tidak diimpor.
4. Impor LOD1–3 ke slot LOD dan set screen size awal 1,0 / 0,5 / 0,25 / 0,12.
5. Pasang MI ke slot material, rename skeleton → `SKEL_Jayadwara` dan physics asset → `PA_Jayadwara`.
6. Buat socket dari `SK_Jayadwara_sockets.json`.

Kalau ada langkah gagal, Output Log menampilkan baris **`[Jayadwara][MANUAL]`** berisi langkah penggantinya (lihat opsi B).

**Asumsi yang belum diuji:**
- UE 5.5+ mengimpor FBX lewat **Interchange**. Skrip mematikannya sementara (`Interchange.FeatureFlags.Import.FBX 0`) supaya opsi FBX lama berlaku. Kalau CVar itu tidak ada, Interchange yang dipakai dan opsi skala/physics mungkin diabaikan: cek hasilnya.
- Nama API `SkeletalMeshEditorSubsystem.import_lod`, `SkeletalMesh.add_socket`, dan `AnimPoseExtensions` diambil dari UE 5.x. Skrip mengecek keberadaannya dulu.

## 4. Skala raksasa

- Model dibuat setinggi manusia: **1,90 m** (tanduk 1,99 m) = 190 cm di UE pada skala 1.
- docs/13 D4: skala raksasa diterapkan saat import (*Import Uniform Scale*). Tinggi game ±45 m masih **placeholder** sampai greybox, jadi skala = 45 / 1,90 ≈ **23,68**.
- Untuk menguji di skala manusia (misal retarget dibandingkan dengan Mannequin), set `IMPORT_UNIFORM_SCALE = 1.0` di skrip.
- Kalau tinggi game berubah, ubah `GIANT_HEIGHT_M` lalu impor ulang. Mesh, LOD, physics asset, dan socket ikut berubah bersama.
- Alternatif yang belum diputuskan: impor di skala 1, lalu skala di komponen mesh pada BP.

## 5. Opsi B: manual

**B1. Tekstur.** Seret semua `T_Jayadwara_*.png` ke `Textures/`, lalu atur:

| Akhiran | sRGB | Compression | Lainnya |
|---|---|---|---|
| `_BC` | on | Default | |
| `_N` | off | Normalmap | **Flip Green Channel** on |
| `_Mask`, `_ORM`, `_Emit` | off | Masks | |

**B2. Mesh.** Impor `SK_Jayadwara.fbx` ke `Mesh/`:
- Skeletal Mesh on; Import Uniform Scale ≈ 23,68 (bagian 4); Convert Scene on.
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

**B5. Socket.** Di Skeleton Tree, *Add Socket* pada tulang berikut. Posisi dalam ruang komponen di skala 1 (cm); kalikan dengan skala import. Pindahkan socket ke titik ini dengan gizmo:

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

- [ ] Karakter berdiri di z=0, menghadap **+Y** di viewport mesh (sama seperti Mannequin), tinggi ≈ 45 m (atau 1,99 m pada skala 1).
- [ ] 4 LOD ada; batas bawah LOD0 sama dengan LOD1–3 (skala LOD ikut). Pindah LOD tidak membuat posisi meloncat.
- [ ] 4 slot material terpasang MI yang benar; emas tidak tampak silver; mata & permata dada menyala **konstan** (aturan IP: tidak berkedip, tidak dikaitkan ke meter Sync).
- [ ] Normal tidak terbalik. Kalau relief kain tampak cekung, matikan Flip Green.
- [ ] 9 socket di tulang yang benar, posisinya sesuai (tangan di kepalan, `chest_sun` di permata dada).
- [ ] Physics asset tidak menahan pose; kapsul kain/selendang dimatikan atau disetel.
- [ ] Retarget animasi jalan/pukul dari Mannequin tanpa tangan menembus badan.
- [ ] Performa di level uji (gedung, target 60 FPS); screen size LOD disetel.

## 8. Catatan & keterbatasan

- Pose lengan terangkat penuh: tutup pauldron sebagian masuk ke badan dan menempel ke kerah. Kandidat perbaikan: tulang bantu bahu atau corrective, setelah dilihat dengan animasi sungguhan (docs/13).
- LOD3 sedikit belang di paha karena normal halus ikut di-decimate. Masih wajar untuk jarak jauh.
- Tekstur masih versi otomatis (hand-paint belum).
- File Blender sumber: `Art/Blender/jayadwara_giant_v05_revisi.blend`. Untuk membangun ulang paket: `Art/Scripts/16_make_lods.py` (urutan lengkap di `Art/README.md`).
