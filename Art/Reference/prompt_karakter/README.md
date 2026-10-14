# Prompt karakter (Ep 1–10)

Satu file per karakter. Tiap file berisi status, catatan risiko Tripo, dan prompt siap salin.

> **Status: usulan (14 Okt 2026).** Daftar dari [docs/03](../../../docs/03-karakter.md), [docs/05](../../../docs/05-daftar-episode-boss.md#arc-1--kebangkitan-ep-110), [docs/16](../../../docs/16-panduan-arc-1.md) bagian 6–7, dan [docs/18](../../../docs/18-kebutuhan-episode-1.md). Penampilan tokoh yang belum dikunci di docs (anggota DWARA, warga, boss Ep 2–10) adalah **usulan Claude**; ubah bebas, lalu catat keputusan finalnya di docs terkait.
>
> **Scope:** yang dibutuhkan sekarang hanya kelompok **A (Ep 1)**. Ep 2–10 diproduksi di Fase 4 ([docs/10](../../../docs/10-roadmap.md)).

## Daftar

| File | Karakter | Episode | Jenis | Tripo |
|---|---|---|---|---|
| **A. Ep 1 (sekarang)** | | | | |
| [`aksa.md`](aksa.md) | Aksa | semua | Hero manusia | ✅ (wajah: MetaHuman?) |
| [`jayadwara.md`](jayadwara.md) | Jayadwara2 | semua | Hero raksasa | ✅ sudah |
| [`jerangkong.md`](jerangkong.md) | Jerangkong + minion kerangka | 1, 10 | Boss + minion | ✅ sudah |
| [`warga_petani.md`](warga_petani.md) | Warga: bapak petani | 1+ | NPC | ✅ |
| [`warga_ibu.md`](warga_ibu.md) | Warga: ibu | 1+ | NPC | ✅ |
| [`warga_pemuda.md`](warga_pemuda.md) | Warga: pemuda (+ preman Ep 4) | 1+ | NPC / minion | ✅ |
| [`mandor.md`](mandor.md) | Mandor Adikara | 1 | NPC | ✅ input siap |
| **B. Anggota DWARA & tokoh (Fase 4)** | | | | |
| [`bagas.md`](bagas.md) | Kol. (Purn.) Bagas Suryo | 2+ | Tokoh | ✅ |
| [`nadia.md`](nadia.md) | Dr. Nadia Prameswari | 2+ | Tokoh | ✅ |
| [`yahyo.md`](yahyo.md) | Prof. Yahyo Sasmito | 2+ | Tokoh | ✅ |
| [`ki_sastro.md`](ki_sastro.md) | Ki Sastro | 2+ | Tokoh | ✅ |
| [`sekar.md`](sekar.md) | Sekar | 2+ | Tokoh | ✅ |
| [`bayu.md`](bayu.md) | Bayu Saputra | 2+ | Tokoh | ✅ |
| [`ratna.md`](ratna.md) | Ratna Dewantari | 3, 7, 10 | Tokoh (opsional) | ⚪ |
| [`gunadi.md`](gunadi.md) | Gunadi Adikara | — | Tokoh (opsional) | ⚪ |
| **C. Boss Ep 2–10 (Fase 4)** | | | | |
| [`tuyul.md`](tuyul.md) | Tuyul | 2 | Boss + minion | ✅ |
| [`jenglot.md`](jenglot.md) | Jenglot | 3 | Boss | ✅ |
| [`babi_ngepet.md`](babi_ngepet.md) | Babi Ngepet | 4 | Boss berkaki empat | ✅ |
| [`pocong.md`](pocong.md) | Pocong ⚠️ | 5 | Boss | ✅ |
| [`kemamang.md`](kemamang.md) | Kemamang | 6 | Boss api | ❌ VFX |
| [`kalong_wewe.md`](kalong_wewe.md) | Kalong Wewe | 7 | Boss udara | ✅ |
| [`wewe_gombel.md`](wewe_gombel.md) | Wewe Gombel | 8 | Boss | ✅ |
| [`genderuwo.md`](genderuwo.md) | Genderuwo | 9 | Boss (rig Buto) | ✅ |
| [`banaspati.md`](banaspati.md) | Banaspati | 10 | Boss finale | ✅ sebagian |
| **D. Minion baru (Fase 4)** | | | | |
| [`minion_kabel.md`](minion_kabel.md) | Kabel hidup | 3 | Minion | ✅ |
| [`minion_akar.md`](minion_akar.md) | Akar hidup | 8 | Minion | ✅ |
| — | Bayang-bayang (Ep 5, 9) | | Minion | ❌ Manny + material siluet gelap |
| — | Api kecil (Ep 6, 10) | | Minion | ❌ VFX |

---

## 0. Aturan umum (berlaku untuk semua prompt)

Pelajaran dari Aksa, Jayadwara2, dan Jerangkong:

1. **Satu karakter per gambar**, figur minimal ±800 px tingginya (sheet berisi banyak karakter membuat tiap figur terlalu kecil). **Generate 1 sheet berisi 3 view** (depan, samping hadap kiri, belakang) supaya konsisten, lalu **potong jadi 3 file** dengan kanvas, skala, dan posisi telapak yang sama. Masukkan ke Tripo **mode Multiview** (Front / Left / Back). Satu sheet langsung ke mode single image = Tripo membuat 3 karakter.
2. **Celah tembus di siluet**: lengan menjauh dari badan (±40–45°), kaki terbuka, jari lurus agak renggang. Untuk makhluk berkaki empat atau bersayap, aturan setaranya ditulis di prompt masing-masing.
3. **Tidak ada kain/aksesori menjuntai yang menempel ke badan atau kaki** (selendang, sabuk kain, tali panjang). Bagian berayun dibangun terpisah dengan rantai tulang.
4. **Flat unlit**, tanpa bayangan pekat, latar abu-abu polos, **tanpa teks/label**.
5. **Corak besar dan sederhana.** Motif halus dibuat ulang di material UE.
6. Monster: energi Kala **merah gelap**, **tanpa gore**, **tanpa cahaya biru** ([docs/16](../../../docs/16-panduan-arc-1.md#27-aturan-konten)).
7. Setelah Tripo: taruh `.glb` di repo → Claude menjalankan gate ukur (celah, pulau mesh, non-manifold, simetri) **sebelum** rig.
8. **Gaya: realistis** (keputusan 14 Okt 2026). Render 3D realistis seperti sheet warga/mandor, tetap dengan cahaya rata. Tokoh manusia: pertimbangkan MetaHuman untuk wajah ([docs/08](../../../docs/08-requirement-produksi.md#keputusan-terbuka) #5); Tripo tetap untuk pakaian, monster, dan NPC.

Kalimat penutup yang dipakai di semua prompt manusia (sudah tertulis di tiap prompt):

```
Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic materials, simple bold patterns, no fine detail, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```
