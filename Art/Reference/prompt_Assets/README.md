# Prompt aset (Ep 1, tanpa rig)

Satu file per aset. Tiap file berisi status, ukuran dunia nyata, catatan modeling, dan prompt siap salin untuk **gambar turnaround**. Gambar dipakai sebagai **referensi modeling manual** (image plane di Blender), bukan input Tripo. Pasangan untuk karakter ber-rig: [`../prompt_karakter/`](../prompt_karakter/README.md).

> **Status: usulan (16 Okt 2026).** Daftar dari [docs/18 B1 & C](../../../docs/18-kebutuhan-episode-1.md#b1-model), [docs/17](../../../docs/17-skenario-arc-1.md#episode-1--gerbang-yang-retak), dan [docs/30 bagian 2 & 4](../../../docs/30-desain-level-ep01.md#4-daftar-bangunan-dan-prop-arena). Ukuran dari docs/30; penampilan yang belum dikunci di docs (mobil DWARA, Netra, musala, prop proyek) adalah **usulan Claude**. Ubah bebas, lalu catat keputusan finalnya di docs terkait.
>
> **Keputusan K2** ([18](../../../docs/18-kebutuhan-episode-1.md#6-keputusan-yang-perlu-diambil)) arca Dwarapala dibuat sendiri atau dari Fab masih terbuka. Prompt arca ditulis dengan asumsi dibuat sendiri.

## Daftar

| File | Aset | Adegan | Ukuran (m) | Catatan |
|---|---|---|---|---|
| **A. Prop cerita (prioritas)** | | | | |
| [`arca_dwarapala.md`](arca_dwarapala.md) | Arca Dwarapala (kiri & kanan) | 4, 6, 9 | tinggi ±4 + alas 1 | 1 model; varian retak, tali derek, terpal dibuat di Blender |
| [`gerbang_prasasti.md`](gerbang_prasasti.md) | Gerbang candi + alas arca + prasasti retak | 4, 6, 9 | gerbang lebar 8 | Tidak bisa hancur; prasasti = clue 3 |
| [`truk_derek_adikara.md`](truk_derek_adikara.md) | Truk derek Adikara | 3, 6 | ±10 × 2,5 × 3,5 | Membawa arca kanan di cutscene |
| [`mobil_dwara.md`](mobil_dwara.md) | Mobil DWARA | 2, 3 | ±5 × 1,9 × 1,9 | Titik mulai pemain |
| [`kalung_aksa.md`](kalung_aksa.md) | Kalung pecahan arca | 6 | liontin ±5 cm | Inti kekuatan; mesh terpisah dari Aksa |
| [`netra.md`](netra.md) | Scanner Netra | 4 | ±20 cm | Dipegang tangan |
| **B. Lingkungan candi** | | | | |
| [`candi_induk.md`](candi_induk.md) | Candi induk Lawang Sapta | latar 3–9 | 18 × 18 × 20 | Tidak bisa hancur |
| **C. Bangunan desa** | | | | |
| [`rumah_bata.md`](rumah_bata.md) | Rumah bata genteng (D1–D4) | 7 | 10 × 8 × 6 | Bisa hancur; 1 mesh + 2 variasi atap |
| [`warung.md`](warung.md) | Warung kayu/seng (D5–D6) | 7 | 6 × 5 × 4 | Bisa hancur |
| [`menara_air.md`](menara_air.md) | Menara air besi (D7) | 7 | 4 × 4 × 15 | Bisa hancur |
| [`gardu_ronda.md`](gardu_ronda.md) | Gardu ronda + kentongan (D8) | 7 | 3 × 3 × 4 | Bisa hancur |
| [`musala.md`](musala.md) | Musala desa | 7 | ±9 × 9 × 8 | **Tidak** bisa hancur (aturan budaya) |
| **D. Prop proyek Adikara** | | | | |
| [`prop_proyek_adikara.md`](prop_proyek_adikara.md) | Ekskavator, buldoser, kantor kontainer, lampu sorot, papan proyek, pagar seng, tenda kerja | 3–9 | per item | Dipakai ulang di Arc 2; kandidat kuat Fab |

**Tanpa prompt:** batu latihan (batu datar biasa; cukup scan/Fab), tiang listrik, pohon, dan kit batu candi modular (Fab).

---

## 0. Aturan umum (berlaku untuk semua prompt)

1. **Satu aset per gambar.** Sheet berisi **4 view**: depan, samping kiri, belakang, atas. View atas dari AI sering kurang akurat; kalau meleset, cukup pakai 3 view lainnya.
2. **Ortografis**, tanpa perspektif, tanpa sudut kamera miring. Semua view berdiri di satu garis tanah dengan skala sama, supaya bisa langsung dipasang sebagai image plane.
3. **Flat unlit**, latar abu-abu polos, **tanpa teks/label**. Bayangan dan AO di gambar akan menipu bentuk saat modeling.
4. **Bentuk besar dan jelas, detail halus tidak perlu.** Lumut, noda, retak halus, dan karat dibuat di material/tekstur UE, bukan di mesh.
5. **Logo hanya abstrak.** Adikara = matahari terbit geometris (sama dengan rompi [mandor](../prompt_karakter/mandor.md)); kendaraan tanpa merek nyata.
6. **Bangunan yang bisa hancur** ([23 Iterasi 7](../../../docs/23-rencana-fase-1.md#iterasi-7--gedung-hancur--meter-sinkronisasi)): dinding tebal tertutup (bukan bidang tipis), bagian besar terpisah (dinding, atap, tiang) supaya fracture Geometry Collection rapi.
7. **Gaya: realistis** (keputusan 14 Okt 2026), candi batu andesit, tanah merah galian, desa Jawa sederhana ([30](../../../docs/30-desain-level-ep01.md)).

Kalimat penutup yang dipakai di semua prompt (sudah tertulis di tiap prompt):

```
Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/<aset>_v01.png`, potong jadi `<aset>_front/left/back/top.png` dengan kanvas dan skala yang sama, lalu pasang sebagai image plane di Blender sesuai ukuran di tabel. Penamaan aset UE mengikuti [12](../../../docs/12-technical-design.md) (`SM_` untuk static mesh; prefix Geometry Collection belum ada di tabel docs/12, jadi tentukan saat Iterasi 7).
