---
name: jd-audit-model
description: Dipakai setiap kali ada FBX karakter/monster baru atau hasil perbaikan di JAYADWARA, sebelum menyatakan model bagus atau lanjut ke langkah berikutnya. Menjalankan validator, audit_karakter.py (17 pose uji, ketiak dari bawah) dan banding_karakter.py (lama vs baru vs konsep) lalu membaca vonis dan gambar dengan benar.
---

# Audit & banding model

Detail: `Hermes/panduan_model_3d.md` §4 dan `Hermes/aksa_hermes.md` §2.

## 1. Validator kontrak FBX (manusia skeleton Manny)
```
blender --background --factory-startup --python Art/Scripts/validate_aksa.py -- <FBX> --max-tris <anggaran LOD> --require-uv --slots <slot1,slot2>
```
Semua harus PASS. Tempel output lengkap ke laporan.

## 2. Audit pembanding (sekali) dan model
```
blender --background --factory-startup --python Art/Scripts/audit_karakter.py -- <FBX pembanding> --out Hermes/Art/<topik>/Audit/lama --height <m>
blender --background --factory-startup --python Art/Scripts/audit_karakter.py -- <FBX model> --out Hermes/Art/<topik>/Audit/<langkah> --height <m>
```
- `--height`: tinggi di FBX itu (manusia 1.806; boss raksasa mis. 22.5).
- `--profil`: sama untuk keduanya. Kosong = Manny. Non-biped: profil yang sudah disetujui developer.
- `--kanvas <m>`: naikkan kalau render depan/samping terpotong (badan panjang/sayap).

## 3. Banding
```
python -I Art/Scripts/banding_karakter.py --lama Hermes/Art/<topik>/Audit/lama --baru Hermes/Art/<topik>/Audit/<langkah> --out Hermes/Art/<topik>/Banding/<langkah> --ref <ak | "path/ref_{v}.png" | none>
```

## 4. Membaca hasil (bagian yang paling sering dilewati)
1. `banding.md` ditempel utuh ke laporan. **VONIS GAGAL tidak boleh dilewati** dengan mengubah toleransi atau skrip.
2. `banding_ortho.png`: kolom lama vs baru vs konsep. Merah = ada di konsep tapi tidak di model, cyan = sebaliknya. Lengan wajar beda (pose rest Manny), yang dinilai badan, kepala, kaki.
3. `banding_pose.png`, **setiap baris** (18 pose), satu kalimat per pose:
   `<pose>: <beda dengan lama>; masalah: <tidak ada / lubang di ... / kulit tembus di ... / melar di ... / ikut tulang salah ...>`
   Cari: latar biru-abu terlihat menembus badan (lubang; paling sering di ketiak, selangkangan, leher, siku dalam, lutut belakang), paku/tenda, bagian ikut tulang yang salah, kaku di sendi, kiri-kanan tidak simetris pada pose simetris.
4. **Tidak bisa melihat gambar** → tulis "TIDAK BISA MELIHAT GAMBAR — perlu dicek developer". Jangan mengarang deskripsi.
5. Ada GAGAL / masalah → skill `jd-perbaiki-model`. Jangan langsung mengedit.

## Arti angka
- Regangan p99 (%) = dasar vonis, tidak bergantung kerapatan mesh. Peregangan maks (cm) = penunjuk LOKASI ("PERIKSA <tulang>").
- Model potongan kaku (Jerangkong) wajar ≈ 0 %.
- Exit code banding: 0 LULUS, 1 GAGAL, 3 tanpa pembanding (perlu nilai developer).
