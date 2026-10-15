# Panduan Model 3D untuk Hermes (semua karakter & monster)

> Dari Claude, untuk Hermes. **Read-only bagimu.** Berlaku untuk **setiap** tugas model 3D: NPC manusia (mis. Ki Sastro, Kol. Bagas Suryo, warga, agen DWARA), monster/boss (Tuyul, Jenglot, Babi Ngepet, Pocong, ...), dan varian.
> Aturan dasar tetap `AGENTS.md` (worktree, sandbox, §0 cara kerja). Contoh yang sudah terisi lengkap: [`aksa_hermes.md`](aksa_hermes.md) (Aksa2). Kalau ada beda, **instruksi khusus model** (`<model>_hermes.md`) menang atas panduan ini, dan `AGENTS.md` menang atas keduanya.
> Versi: 14 Okt 2026, diperbarui 15 Okt 2026 untuk gaya realistis (lihat `panduan_kerja_claude.md` §8).

---

## 1. Tentukan jenis model dulu

| Jenis | Contoh | Skeleton | Profil pose audit | Pembanding wajib (`--lama`) |
|---|---|---|---|---|
| **A. Manusia ber-skeleton Manny** | Aksa2, Ki Sastro, Bagas Suryo, warga | Manny asli **tanpa diubah**, tinggi = **1,806 m** (docs/19 A1/A3) | `pose_profil/manny.json` (default) | Model yang digantikan; kalau model baru: `Art/Export/SK_Aksa.fbx` |
| **B. Biped skeleton sendiri, nama tulang Manny** | Tuyul, Jenglot, Pocong, boss raksasa biped, NPC yang tingginya bukan 1,806 m | Sendiri, **nama & hierarki tulang Manny** (pola `jk_skeleton.py` / `jd2_skeleton.py`), sendi diukur dari mesh; animasi lewat IK Retargeter | `pose_profil/manny.json` | Model biped yang sudah disetujui dan **paling mirip bentuknya**: `SK_Jerangkong.fbx` (monster), `SK_Jayadwara2.fbx` (raksasa berzirah), `SK_Aksa.fbx` (manusia) |
| **C. Non-biped** | Babi Ngepet (berkaki empat), ular/naga, makhluk bersayap | Sendiri; nama tulang bebas tapi konsisten `_l/_r` | Profil **sendiri** dari template `pose_profil/contoh_berkaki_empat.json` | Tidak ada → vonis "PERLU NILAI DEVELOPER"; setelah satu model jenis ini disetujui, model itu jadi pembanding berikutnya |

Tidak yakin jenisnya → tulis pilihanmu + alasan di kartu model (§2) dan tunggu developer di gate K0.

**Skala** (docs/16 §2.6): monster punya dua wujud.
- Wujud awal (lawan Aksa): skala manusia ±1–3 m.
- Boss raksasa: **0,5–0,8× Jayadwara (45 m)**; ukuran per episode ada di docs/16 tabel §3 (Tuyul 0,5×, Jenglot 0,55→0,8×, Babi Ngepet 0,5× badan panjang, Pocong 0,75×, Jerangkong 0,7×).
- Satu model → dua aset dengan skala di-bake saat export (pola Jerangkong J2 di docs/20: `SK_Jerangkong` ×14 dan `SK_Kerangka` ×0,85). Skala **tidak** diatur lewat skala actor di UE.

## 2. Kartu model (K0, wajib sebelum kerja)

Tulis di laporan, isi dari dokumen, bukan dari ingatan:

```markdown
## Kartu model: <Nama>
- Topik/branch: hermes/<topik>          (mis. hermes/tuyul)
- Jenis: A / B / C  — alasan:
- Sumber desain: docs/05 baris Ep <n>, docs/06 (mitologi + panduan sensitivitas), docs/16 §3 (ukuran, mekanik), docs/03 (kalau NPC)
- Konsep/referensi dari developer: <path gambar / GLB>
- Mekanik yang butuh geometri/tulang khusus: (mis. Pocong: tali ikatan = titik lemah; Jenglot: membesar; Tuyul: kawanan kecil)
- Tinggi authoring: <m>  | skala bake: wujud awal <m>, boss <m> (<x>× Jayadwara)
- Skeleton: Manny asli / sendiri (nama Manny) / sendiri (non-biped)
- Profil pose: Art/Scripts/pose_profil/manny.json / Hermes/Tools/pose_<topik>.json
- Pembanding (--lama): <path FBX> — alasan
- Anggaran tris LOD0/1/2/3: (angka di docs: manusia 60k/25k/10k/4k docs/19 A8; boss raksasa ≤100k/30k/14k/6k seperti Jayadwara2. Angka manusia ditulis saat gaya masih stylized; sampai developer menetapkan ulang untuk realistis, pakai angka ini dan **laporkan** kalau terlampaui)
- Gaya: **realistis** (docs/README, 14 Okt 2026). Baca `panduan_kerja_claude.md` §8: rambut kartu, toleransi 3, bayangan terpanggang, seam normal map, wajah/MetaHuman
- Slot material:
- Socket: (manusia: 7 socket SK_Aksa_sockets.json; monster: titik pukul + titik lemah + VFX, sebut nama & tulang)
- Ekspresi wajah: (manusia yang tampil di dialog/potret: 8 morph target dengan nama sama dengan `SK_Aksa`, cara di `aksa_hermes.md` H3b; warga/minion: tanpa; monster: sebut kalau mekanik butuh, mis. mulut membuka saat serangan)
- Checklist IP/budaya: (docs/01 wajib dihindari, docs/06 sensitivitas; Pocong ⚠️: jangan mengolok-olok pemakaman)
- Nama: objek Blender <PREFIX>_, aset SK_<Nama>, UE /Game/Hermes/<Nama>/
```
**GATE K0:** developer menyetujui kartu (+ profil pose kalau jenis C). Profil pose = **kriteria uji**: setelah disetujui, tidak boleh diubah tanpa izin.

## 3. Iterasi umum (K0–K7)

Sama dengan H0–H7 di `aksa_hermes.md`, digeneralisasi. Path: `Hermes/Art/<topik>/{Source,Blender,Export,Render,Audit,Banding,Reference}`, skrip `Hermes/Tools/<topik>_<nomor>_<nama>.py`, UE `/Game/Hermes/<Nama>/`.

| Iterasi | Isi | Lulus (angka) | Gate |
|---|---|---|---|
| **K0** | Kartu model (§2); intake GLB (salin `jayadwara2_01_import_tripo.py` atau `jerangkong_01_import_tripo.py`, ganti path/nama/`ROOT`); render ortografis; laporan kondisi mesh (tris, pulau, non-manifold, simetri, bagian menyatu) | tinggi sesuai kartu ±1 %; menghadap -Y; checklist IP tanpa ❌ | **GATE** |
| **K1** | Skeleton: jenis A = impor Manny tanpa diubah, mesh dipaskan ke pose rest Manny; jenis B/C = skeleton dari landmark mesh (sendi diukur, tabel sendi di laporan) | jenis A: sendi mesh ≤ 2 cm dari Manny; B/C: setiap sendi di dalam volume mesh (cek render tulang tembus pandang) | |
| **K2** | Pisahkan bagian menyatu, tutup lubang, buang serpihan, kulit di bawah baju | tepi terbuka di zona sendi turun (angka sebelum/sesudah); IoU badan selisih ≤ 0,02 dari K1 | |
| **K3** | Skinning (transfer bobot dari pembanding kalau skeleton sama; bagian kaku = 1 tulang); export LOD0 + socket JSON; **audit + banding** (§4) | validator PASS; **VONIS LULUS** (atau PERLU NILAI DEVELOPER untuk jenis C); deskripsi setiap pose | **GATE** |
| **K4** | Tekstur & material (palet dari docs/kartu; tanpa silver/biru menyala untuk pihak DWARA; emas `#D6A33A` matte) | tiap zona palet: hex sampel vs target di laporan | |
| **K5** | LOD1–3 + export final (+ aset skala kedua untuk monster) | validator + audit + banding per LOD & per skala | |
| **K6** | UE di sandbox: skeleton **salinan/sendiri** di `/Game/Hermes/<Nama>/Rig/` (tidak pernah ke `SK_Mannequin`), level `Test_Hermes_<Nama>`, animasi berdampingan dengan pembanding | animasi jalan (2 frame screenshot beda); bounds sesuai kartu; cek sandbox LULUS | **GATE** |
| **K7** | Laporan akhir + usulan integrasi (tidak dikerjakan sendiri) | `hermes_cek_sandbox.py` LULUS | |

## 4. Audit & banding (bagian terpenting)

```
blender --background --factory-startup --python Art/Scripts/audit_karakter.py -- <FBX pembanding> --out Hermes/Art/<topik>/Audit/lama --height <m> [--profil <json>] [--kanvas <m>]
blender --background --factory-startup --python Art/Scripts/audit_karakter.py -- Hermes/Art/<topik>/Export/SK_<Nama>.fbx --out Hermes/Art/<topik>/Audit/<langkah> --height <m> [--profil <json>] [--kanvas <m>]
python -I Art/Scripts/banding_karakter.py --lama Hermes/Art/<topik>/Audit/lama --baru Hermes/Art/<topik>/Audit/<langkah> --out Hermes/Art/<topik>/Banding/<langkah> --ref <konsep>
```
- `--height` = tinggi model **di FBX itu** (manusia 1,806; boss raksasa mis. 22,5 untuk 0,5× Jayadwara). Pembanding diaudit dengan `--height` miliknya sendiri.
- `--profil`: **sama** untuk lama dan baru (banding GAGAL kalau beda). Jenis A/B: kosongkan (default Manny). Jenis C: profil yang disetujui di K0.
- `--kanvas`: naikkan kalau render samping/depan terpotong (badan panjang, sayap). Konsep harus dibuat dengan kanvas yang sama.
- `--ref`: `ak` untuk Aksa; model lain: buat reference plane berkanvas sama (pola `Art/Scripts/make_reference_planes_aksa.py` → `Hermes/Art/<topik>/Reference/<topik>_ref_{front,side,back}.png`) lalu `--ref "Hermes/Art/<topik>/Reference/<topik>_ref_{v}.png"`; tidak ada konsep tampak depan/samping/belakang → `--ref none` dan tulis di laporan.
- Pembanding dengan bentuk lain (mis. Tuyul vs Jerangkong): IoU tidak dibandingkan antar-model; yang dibandingkan regangan per pose (kualitas rig) dan gambar.
- Model kaku (potongan, pola Jerangkong) wajar regangan ≈ 0 %; kalau ada pose dengan regangan tinggi, itu bagian yang dibobot ke dua tulang dan harus diperiksa.

Ada masalah (audit/banding GAGAL, atau keluhan developer)? Jangan langsung mengedit: ikuti [`panduan_kerja_claude.md`](panduan_kerja_claude.md) §3 (diagnosa_mesh → perbaiki_mesh → diagnosa ulang).

Cara membaca hasil: `aksa_hermes.md` §2 (berlaku untuk semua model). Ringkasnya: `banding.md` ditempel utuh; setiap pose dideskripsikan per bagian; lubang, melar, ikut tulang salah, kaku/lentur salah tempat, kiri-kanan beda. **Tidak bisa melihat gambar → tulis itu, jangan menebak.**

### Menulis profil pose sendiri (jenis C)
1. Salin `Art/Scripts/pose_profil/contoh_berkaki_empat.json` → `Hermes/Tools/pose_<topik>.json`, ganti `nama`.
2. Ganti nama tulang dengan nama tulang skeletonmu. **Jangan** mengganti nama tulang skeleton supaya cocok dengan template.
3. Pose harus menguji **setiap** sendi yang bergerak di game (mekanik di kartu): minimal 8 pose, sudut sampai batas gerak yang dipakai animasi. Pose yang terlalu kecil membuat audit tidak berarti.
4. `orientasi`: pasangan tulang yang arahnya pasti (ekor → kepala = depan, kanan → kiri = +X).
5. `kamera.dekat`: sendi paling rawan (ketiak kaki depan, pangkal sayap, pangkal ekor), dilihat dari bawah.
6. Jalankan audit sekali di model yang belum di-skin rapi untuk memastikan semua pose terlihat masuk akal di gambar, lalu ajukan di gate K0.

## 5. Scope

Model Ep 2–5 dan NPC selain Ep 1 berada **di luar scope vertical slice saat ini** (docs/10, docs/11). Hermes boleh mengerjakannya di sandbox atas permintaan developer sebagai persiapan, tetapi integrasinya ke proyek menunggu fase produksinya. Tulis di laporan: "di luar scope fase aktif, persiapan".
