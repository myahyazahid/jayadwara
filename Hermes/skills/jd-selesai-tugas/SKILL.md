---
name: jd-selesai-tugas
description: Dipakai sebelum commit, sebelum push, dan sebelum mengatakan tugas JAYADWARA selesai atau melapor ke developer. Checklist bukti, cek sandbox, laporan lengkap, commit & push ke hermes/<topik> tanpa merge.
---

# Selesai tugas

Jangan bilang "selesai" atau "sudah bagus" sebelum semua kotak ini tercentang **dengan bukti di laporan**.

## Checklist bukti
- [ ] Setiap langkah di tabel progres laporan punya: status LULUS/GAGAL, **angka**, dan **path** log/gambar.
- [ ] Model: validator PASS (output ditempel), `banding.md` VONIS LULUS (ditempel), deskripsi setiap pose dari `banding_pose.png`.
- [ ] Perbaikan: diagnosa `--sebelum` ditempel, regangan ≤ pembanding + 5 poin, warna penanda hilang dari tempat keluhan.
- [ ] Gambar benar-benar dilihat. Tidak bisa melihat gambar → tertulis jelas di laporan.
- [ ] Yang GAGAL/belum selesai ditulis apa adanya (angka tiap percobaan + dugaan penyebab), bukan disembunyikan.
- [ ] "Usulan perubahan di luar sandbox" terisi kalau hasil butuh perubahan file/aset proyek (tidak dikerjakan sendiri).

## Cek sandbox (wajib LULUS)
```
python -I Tools/hermes_cek_sandbox.py
```
GAGAL → kembalikan file yang disebut (perintahnya dicetak skrip). File sudah ter-commit di luar sandbox → **jangan force-push**; commit baru yang mengembalikannya, tulis di laporan.

## Commit & push
```
python -I Tools/hermes_cek_sandbox.py      # harus LULUS dulu; baru setelah itu git add -A aman
git add -A
git lfs status
git commit -m "[hermes] <topik> <langkah>: <ringkas>"
git push -u origin hermes/<topik>
```
- Biner (`.uasset .umap .fbx .png .blend .glb`) harus muncul di `git lfs status` sebagai LFS.
- Tidak pernah: push ke `development`/`main`, merge, membuat PR, `--force`.

## Pesan ke developer (singkat)
1. Apa yang dikerjakan + branch.
2. Hasil dengan angka (mis. "regangan tangkis 2062 % → 28,5 %, sama dengan model sehat").
3. Cara mencoba (file/level, pose/animasi yang dilihat).
4. Yang belum beres + pertanyaan.
Developer yang mencoba, lalu meminta Claude me-review dan memindahkan ke proyek.
