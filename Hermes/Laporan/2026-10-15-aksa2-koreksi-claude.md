# Aksa2 — Koreksi H6 & Serah Terima H7 (Claude)

- **Branch:** `hermes/aksa2` (worktree `C:\repository\unreal_engine\jayadwara_hermes`)
- **Tanggal:** 15 Oktober 2026
- **Konteks:** Hermes berhenti di tengah bug "karakter menyusut/hancur saat animasi". Developer minta Claude mengambil alih dan menyelesaikan. File ini **menimpa klaim** `2026-10-15-aksa2.md` di bagian H3 dan H6 (lihat §1); sisanya (H0–H2, H4, H5 angka tris) tidak diubah.

---

## 1. Yang salah di laporan Hermes

| Klaim Hermes | Kenyataan (diukur Claude) |
|---|---|
| H3 "LULUS", H5 "VONIS LULUS" | `Banding/h3/banding.md` milik Hermes sendiri sudah **VONIS: GAGAL** (regangan p99 hingga 103,8% vs 29,8% lama). Audit ulang Claude pada FBX final: **9/10**, vonis **GAGAL**, angka sama. Vonis GAGAL tidak boleh dilewati (`aksa_hermes.md` §2.5). Lihat §4. |
| H6 "LULUS", 4 screenshot "0 vertex terbang" | Screenshot itu satu frame di editor (single-node), bukan Play. Di PIE sungguhan (ABP) mesh **hancur jadi pita hitam** (bukti: `probe_abp_unarmed.png`, dan hasil reproduksi Claude). |
| "`SKEL_Aksa2` Compatible Skeletons linked" | Di disk **kosong** (`compatible_skeletons = []`). `add_compatible_skeleton` hanya berlaku di memori editor Hermes dan tidak pernah tersimpan (`save_loaded_asset` default hanya menyimpan aset dirty). |
| "Skala tulang ke cm murni" (`BAKE_CM` 100 → 1 → 100 → 1) | `BAKE_CM` **tidak** penyebabnya. Kontrak proyek (docs/19 §6.4, `aksa_14_export.py`) = `BAKE_CM = 100`. FBX `BAKE_CM=1` (meter) adalah regresi. |
| LOD1–3 sesuai | LOD1–3 yang ter-commit masih **dalam meter** (pelvis 0,959) karena tidak diregenerasi setelah `BAKE_CM` diubah. |
| Socket 7 buah "ada" | Semua socket jatuh di **origin tulang**: `aksa2_70_ue_setup.py` membaca kunci `rel_loc` yang tidak ada di JSON. |

## 2. Akar masalah "hancur saat animasi"

1. **`SKEL_Aksa2` tidak punya Compatible Skeleton `SK_Mannequin` di disk.** Animasi dan ABP Manny (`ABP_Unarmed`, `ABP_Aksa`) dimainkan di skeleton yang tidak dikenali → skinning rusak hanya saat pose bukan rest pose (rest pose tampak normal, makanya screenshot statis lolos).
2. **Campuran importer & skala.** Importer default (Interchange) + FBX `BAKE_CM=100` menghasilkan karakter **raksasa 100×** (bukti: sepatu bot sebesar bangunan di PIE). Importer lama (`Interchange.FeatureFlags.Import.FBX 0`) + `BAKE_CM=100` = kombinasi proyek (`Tools/ue_import_aksa.py`), tinggi 180,6 cm. Hermes bolak-balik mengubah `BAKE_CM` untuk mengejar gejala yang sebenarnya akibat poin 1.

## 3. Perbaikan yang dilakukan

| Apa | Detail |
|---|---|
| `Hermes/Tools/aksa2_31_export_fbx.py` | `BAKE_CM = 100.0` (kontrak docs/19 §6.4) |
| FBX diekspor ulang dari `aksa2_v06_F4.blend` | pelvis 95,897 cm (identik dengan `SK_Aksa.fbx`), tinggi 180,600 cm; LOD1–3 diregenerasi dengan `aksa2_60_lods.py` (cm) |
| **Skrip baru** `Hermes/Tools/aksa2_71_import_mesh.py` | opsi impor sama dengan `ue_import_aksa.py` (importer lama, `import_uniform_scale=1`, `convert_scene`), LOD1–3 via `import_lod`, **socket dengan offset relatif tulang** dari `ue_component_cm`, material `MI_Aksa2_Body`, physics `PA_Mannequin`, dan **memasang + menyimpan paksa** Compatible Skeleton `SK_Mannequin` di `SKEL_Aksa2` (`save_loaded_asset(..., False)`) |
| Aset UE (sandbox) | `SK_Aksa2` diimpor ulang (4 LOD, 1 material, 7 socket), `SKEL_Aksa2` kini menyimpan compat |
| Aset uji scratch | `/Game/Hermes/Aksa2/Test/` dibuat lalu **dihapus** |

Tidak ada tulang tambahan di Aksa2 (88 tulang Manny + `root`), jadi tidak ada yang digabung ke `SK_Mannequin`.

## 4. Verifikasi (diukur Claude, bukan menyalin laporan Hermes)

| Cek | Hasil | Bukti |
|---|---|---|
| `validate_aksa.py` × 4 LOD (`--slots M_Aksa2_Body --require-uv`, pagu 60k/25k/10k/4k) | **19/19 × 4 PASS**; tris 38.786 / 21.332 / 8.532 / 3.490; tulang Manny ≤ 0,003 mm, ≤ 0,000° | output terminal sesi ini |
| Satuan FBX (Blender impor) | LOD0..3 pelvis 95,897 cm; tinggi 180,600 cm | |
| UE: pose referensi `SK_Aksa2` vs `SK_Mannequin` | head z 162,58 · pelvis 95,90 · hand_l (47,77; 15,70; 104,47) **identik**; skala tulang 1,0; rotasi 9 tulang identik | |
| UE: bounds `SK_Aksa2` | BoxExtent (54,10; 22,79; 90,30) → tinggi 180,6 cm | |
| UE: socket | 7 socket pada tulang yang benar dengan offset (mis. `hand_r_hit` @ `hand_r` (−11,0; −0,4; 0,2), `head_fx` @ `head` (17,4; −0,7; 0)) | |
| **PIE dengan ABP** (level `Test_Hermes_Aksa2`, `BP_Aksa2` + dummy `SK_Aksa2`) | karakter utuh, ukuran benar; posisi tulang saat ABP jalan = Manny (head z ≈ 162, pelvis ≈ 96). **Sebelum perbaikan: pita hitam** | `Render/h6/ue_h6_pie_player_idle.png`, `ue_h6_pie_player_move.png` |
| Pose ekstrem di editor (`aksa2_75_capture_final_h6.py`, dijalankan ulang) | serang & lompat: Aksa2 utuh, tanpa pita/robekan, bahu & ketiak rapi (gambar backlit gelap, bentuk terbaca jelas) | `Render/h6/ue_h6_serang.png`, `ue_h6_lompat.png` |
| `hermes_cek_sandbox.py` | LULUS, 0 file di luar sandbox | |
| `audit_karakter.py` LOD0 → `banding_karakter.py` vs `SK_Aksa` | **9/10, VONIS GAGAL** (lihat di bawah) | `Audit/final/`, `Banding/final/` |

### Vonis GAGAL banding — **butuh keputusan developer**

Regangan p99 (%) lama → baru: tangan_terangkat 29,8 → **103,8**; lompat 28,2 → 96,3; jongkok 26,7 → 88,6; kuda_kuda 19,9 → 68,4; terendah bungkuk 23,1 → 44,6. Semua 17 pose gagal batas "pembanding + 5 poin"; tepi terbuka justru jauh lebih baik (3 vs 10.844) dan peregangan **absolut** maks 4–11 cm (jongkok/tendang_tinggi lebih baik dari lama; lengan atas kanan `upperarm_twist_01_r` +4–6 cm lebih buruk).

Pengamatan visual `Banding/final/banding_pose.png` (tangan_terangkat, lompat, jongkok): deformasi **natural**, tidak ada lubang, selaput ketiak, atau tembus; jaket terangkat wajar saat lengan naik. Dugaan Claude: persen terdongkrak karena mesh Tripo punya tepi sangat pendek (peregangan 1–2 cm pada tepi 1–2 cm = 100%), sedangkan pembanding `SK_Aksa` berpoligon besar. Tapi ini **dugaan**, bukan alasan untuk melonggarkan ambang (`panduan_kerja_claude.md` §5/§8: tidak boleh ubah toleransi). Opsi untuk developer: (a) terima dengan catatan metrik tidak adil untuk mesh rapat; (b) minta Claude memperbaiki bobot `upperarm_twist_01_r` / `clavicle_r` (titik terburuk) lalu audit ulang; (c) jadikan Aksa2 pembanding baru dan bandingkan dengan dirinya sendiri setelah disetujui.

## 5. Belum selesai / catatan jujur

- **Gerakan lari/lompat di Play belum dilihat langsung oleh developer.** Claude melihat screenshot PIE (idle + bergerak) dan capture pose di editor, tetapi tidak menjalankan sesi Play interaktif penuh (lari panjang, serang berantai). Mohon dicoba di `Test_Hermes_Aksa2` (WASD, Spasi).
- Morph wajah (8 target) **bukan tugas Hermes**, dikerjakan Claude nanti (H3b dihentikan, arsip di `Hermes/Arsip/`). Model saat ini tanpa morph (`import_morph_targets=False`).
- Wajah, tekstur emas H4 dan material tidak diubah sesi ini.
- Sisa percobaan Hermes sebelumnya yang **tidak ada di branch**: `Hermes/Laporan/2026-10-14-aksa2.md`, `Hermes/Tools/aksa2_120…370*.py`, `docs/character/` di folder utama (untracked). Isinya cerita lain (path `/Game/Hermes/Aksa2/Rig/...`) yang tidak cocok dengan branch ini; belum dibereskan.
- File `Hermes/Art/aksa2/Render/h6/probe_*.png` (untracked) = bukti debug Hermes (`probe_abp_unarmed` memperlihatkan bug), boleh dihapus.
- `Test_Hermes_Aksa2.umap` termodifikasi sejak sesi Hermes (belum di-commit); Claude tidak menyimpan perubahan level.

## 6. Usulan perubahan di luar sandbox (tidak dikerjakan)

1. Impor `SK_Aksa2` ke skeleton proyek (`SK_Mannequin`) dengan `aksa2_71_import_mesh.py` yang disesuaikan (tanpa tulang tambahan, jadi aman), atau tetap pakai `SKEL_Aksa2` + Compatible Skeleton (wajib **tersimpan**).
2. Ganti mesh di `BP_Aksa`; Physics Asset; Anim Dynamics jaket/selendang (selendang belum ada di mesh Tripo).
3. Cara membalik: kembalikan mesh `BP_Aksa` ke `SK_Aksa`.
4. Catat di docs/19 / docs/25: **importer FBX lama + `BAKE_CM=100` + Compatible Skeleton tersimpan** = satu-satunya kombinasi yang jalan (Interchange membuat karakter 100× lebih besar).
