---
name: jd-blender-skrip
description: Dipakai saat menjalankan, menyalin, atau menulis skrip Python Blender (bpy) untuk JAYADWARA — modeling, rig, bobot, UV, tekstur, LOD, export FBX. Berisi cara menjalankan headless dengan aman, menyalin skrip proyek yang berpath tetap, versi file, kontrak export, dan jebakan bpy yang sudah merusak hasil sebelumnya.
---

# Skrip Blender di JAYADWARA

## Menjalankan
- **Headless**: `blender --background <file.blend> --python <skrip.py> -- <argumen>` (scene kosong: `--factory-startup` tanpa .blend).
- Jangan pakai MCP Blender (mengendalikan Blender developer yang terbuka), kecuali developer menyuruh; sebelum menyimpan, cek `bpy.data.filepath` ada di `jayadwara_hermes\Hermes\Art\`.
- Baca output sampai habis. `Traceback`/`Error` = langkah gagal, jangan lanjut.

## File & versi
- Tidak pernah menimpa: `<topik>_v05.blend` → simpan `<topik>_v06_<isi>.blend` (`bpy.ops.wm.save_as_mainfile(filepath=..., copy=False)` ke path BARU).
- Mulai dari file proyek di `Art/Blender/`: buka, lalu langsung save-as ke `Hermes/Art/<topik>/Blender/` sebelum mengubah apa pun.
- Output (FBX, PNG) ke `Hermes/Art/<topik>/{Export,Render,Audit,Diagnosa}/`.

## Skrip proyek di `Art/Scripts/`
- Boleh dipanggil langsung hanya yang menerima input/output lewat argumen dan read-only terhadap file proyek: `audit_karakter.py`, `banding_karakter.py`, `diagnosa_mesh.py`, `perbaiki_mesh.py` (dengan `--out` ke sandbox), `validate_aksa.py`, `aksa_spike_compare.py`, `aksa_12_compare_sheet.py`.
- Lainnya: salin ke `Hermes/Tools/<topik>_NN_<nama>.py`, ganti **setiap** `C:\repository\unreal_engine\jayadwara` → path worktree, arahkan output ke sandbox. Cek: `findstr /s /i "unreal_engine\\jayadwara" Hermes\Tools\*.py` hanya boleh menemukan `jayadwara_hermes`.
- Skrip yang sudah terbukti untuk masalah serupa ada di riwayat (`jayadwara2_25_ketiak.py` jahit ketiak, `jayadwara2_22_rig_r3.py` bobot leher/kain, `15_body_fit.py` lapisan pas badan). Baca dulu sebelum menulis dari nol.

## Kontrak export FBX (docs/19 §6.4)
Salinan armature + mesh dikali 100 dan di-apply (data cm), objek armature bernama `Armature`, `FBX_SCALE_ALL`, tanpa empty, tanpa animasi, socket lewat `<mesh>_sockets.json`, LOD sebagai file terpisah. Pakai skrip export proyek (salinan `aksa_14_export.py` / `jayadwara2_14_export.py`), jangan export default.

## Jebakan bpy (sudah pernah merusak hasil)
```python
# 1. Menghapus grup vertex sambil membaca v.groups -> bobot lama tertinggal
for gi in [g.group for g in me.vertices[i].groups]:     # ambil indeks dulu
    obj.vertex_groups[gi].remove([i])
# 2. Setelah bpy.ops.import_scene.* rujukan Python bisa basi -> ambil ulang
obj = bpy.data.objects[NAMA]; me = obj.data
# 3. Segitiga luas nol (Tripo, decimate) -> barisentrik NaN -> bobot NaN
if not all(math.isfinite(x) for x in bc): ...           # fallback ke vertex terdekat
# 4. Ekor tulang hasil impor FBX tidak sejajar anggota badan -> arah salah
#    pakai kepala anak utama (bukan twist/ik) sebagai ujung tulang
# 5. Decimate dengan vertex_group: bobot 1 = DIDECIMATE -> pakai invert_vertex_group=True untuk melindungi
# 6. Nama node shader dilokalkan -> cari node lewat n.type == "BSDF_PRINCIPLED", bukan nama
```
- Bobot setelah diubah: ≤ 4 influence, dinormalisasi, tidak ada vertex tanpa bobot.
- Skeleton Manny (manusia) **tidak boleh diubah** posisinya/orientasinya; mesh yang dipaskan ke tulang.
- Ukur sebelum dan sesudah setiap skrip (jumlah vertex/tris, tepi terbuka, bobot per tulang) dan tulis di laporan.
