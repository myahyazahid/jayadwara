# Prompt aset tanpa rig (Ep 1–10)

Satu file per aset atau kit, diawali nomor episode tempat aset itu **pertama** dibangun (`ep01_`, `ep02_`, ...); aset yang dipakai ulang tidak ditulis dua kali. Tiap file berisi status, ukuran dunia nyata, catatan modeling, dan prompt siap salin untuk **gambar turnaround**. Gambar dipakai sebagai **referensi modeling manual** (image plane di Blender), bukan input Tripo. Pasangan untuk karakter ber-rig: [`../prompt_karakter/`](../prompt_karakter/README.md).

> **Status: usulan (16 Okt 2026).** Ep 1 dari [docs/18 B1 & C](../../../docs/18-kebutuhan-episode-1.md#b1-model), [docs/17](../../../docs/17-skenario-arc-1.md#episode-1--gerbang-yang-retak), dan [docs/30 bagian 2 & 4](../../../docs/30-desain-level-ep01.md#4-daftar-bangunan-dan-prop-arena). Ep 2–10 dari kartu episode [docs/16](../../../docs/16-panduan-arc-1.md#6-kartu-episode), [docs/28](../../../docs/28-struktur-level-episode.md), dan [docs/31](../../../docs/31-desain-level-ep02.md). Ukuran dari docs/30–31 bila ada, sisanya usulan yang disebandingkan dengan Jayadwara (45 m). Penampilan yang belum dikunci di docs (mis. mobil DWARA, Netra, musala, prop proyek, menara Adikara, gardu listrik, prasasti Sapta Dwara) adalah **usulan Claude**. Ubah bebas, lalu catat keputusan finalnya di docs terkait.
>
> **Scope:** yang dibutuhkan sekarang hanya **Ep 1** (vertical slice). Ep 2–10 diproduksi di Fase 4 ([docs/10](../../../docs/10-roadmap.md)).
>
> **Keputusan K2** ([18](../../../docs/18-kebutuhan-episode-1.md#6-keputusan-yang-perlu-diambil)) arca Dwarapala dibuat sendiri atau dari Fab masih terbuka. Prompt arca ditulis dengan asumsi dibuat sendiri.

## Daftar

| File | Aset | Adegan | Ukuran (m) | Catatan |
|---|---|---|---|---|
| **Ep 1 — Situs Lawang Sapta (sekarang)** | | | | |
| *A. Prop cerita (prioritas)* | | | | |
| [`ep01_arca_dwarapala.md`](ep01_arca_dwarapala.md) | Arca Dwarapala (kiri & kanan) | 4, 6, 9 | tinggi ±4 + alas 1 | 1 model; varian retak, tali derek, terpal dibuat di Blender |
| [`ep01_gerbang_prasasti.md`](ep01_gerbang_prasasti.md) | Gerbang candi + alas arca + prasasti retak | 4, 6, 9 | gerbang lebar 8 | Tidak bisa hancur; prasasti = clue 3 |
| [`ep01_truk_derek_adikara.md`](ep01_truk_derek_adikara.md) | Truk derek Adikara | 3, 6 | ±10 × 2,5 × 3,5 | Membawa arca kanan di cutscene |
| [`ep01_mobil_dwara.md`](ep01_mobil_dwara.md) | Mobil DWARA | 2, 3 | ±5 × 1,9 × 1,9 | Titik mulai pemain |
| [`ep01_kalung_aksa.md`](ep01_kalung_aksa.md) | Kalung pecahan arca | 6 | liontin ±5 cm | Inti kekuatan; mesh terpisah dari Aksa |
| [`ep01_netra.md`](ep01_netra.md) | Scanner Netra | 4 | ±20 cm | Dipegang tangan |
| *B. Lingkungan candi* | | | | |
| [`ep01_candi_induk.md`](ep01_candi_induk.md) | Candi induk Lawang Sapta | latar 3–9 | 18 × 18 × 20 | Tidak bisa hancur |
| *C. Bangunan desa (kit Desa bukit, dipakai ulang Ep 6, 8)* | | | | |
| [`ep01_rumah_bata.md`](ep01_rumah_bata.md) | Rumah bata genteng (D1–D4) | 7 | 10 × 8 × 6 | Bisa hancur; 1 mesh + 2 variasi atap |
| [`ep01_warung.md`](ep01_warung.md) | Warung kayu/seng (D5–D6) | 7 | 6 × 5 × 4 | Bisa hancur |
| [`ep01_menara_air.md`](ep01_menara_air.md) | Menara air besi (D7) | 7 | 4 × 4 × 15 | Bisa hancur |
| [`ep01_gardu_ronda.md`](ep01_gardu_ronda.md) | Gardu ronda + kentongan (D8) | 7 | 3 × 3 × 4 | Bisa hancur |
| [`ep01_musala.md`](ep01_musala.md) | Musala desa | 7 | ±9 × 9 × 8 | **Tidak** bisa hancur (aturan budaya) |
| *D. Prop proyek Adikara* | | | | |
| [`ep01_prop_proyek_adikara.md`](ep01_prop_proyek_adikara.md) | Ekskavator, buldoser, kantor kontainer, lampu sorot, papan proyek, pagar seng, tenda kerja | 3–9 | per item | Dipakai ulang di Arc 2; kandidat kuat Fab |

| **Ep 2 — Kampung Kali (Fase 4)** | | | | |
| [`ep02_rumah_kampung.md`](ep02_rumah_kampung.md) | Rumah padat: 1 lantai, 2 lantai, panggung bantaran | E | 5 × 8 × 4,5–7,5 | Blok Chaos + tukar puing; atap dinaiki tuyul |
| [`ep02_jembatan_kali.md`](ep02_jembatan_kali.md) | Jembatan beton + jembatan bambu gantung | B, C, E | ±24 / ±12 panjang | Jalur evakuasi + jalan pintas kejar-kejaran |
| [`ep02_ruko_jalan_raya.md`](ep02_ruko_jalan_raya.md) | Ruko 3 lantai | E | 5 × 15 × 11 | Dipakai ulang Ep 3, 10 |
| [`ep02_properti_curian.md`](ep02_properti_curian.md) | Mobil warga + gerobak dorong | E (fase 1) | 4,2 / 1,8 panjang | Dicuri boss; gerobak dipakai ulang Ep 4 |
| [`ep02_prop_investigasi.md`](ep02_prop_investigasi.md) | Sesajen + umpan mainan + yuyu | B, C | < 0,5 | Clue ○, umpan tuyul |
| **Ep 3 — Distrik Adikara** | | | | |
| [`ep03_gedung_adikara.md`](ep03_gedung_adikara.md) | Menara Adikara + gedung kantor pengisi | A–E | 40 × 40 × 120 | Gedung generik lain: Fab |
| [`ep03_gardu_listrik.md`](ep03_gardu_listrik.md) | Gardu listrik ×3 | E | ±20 × 15 × 12 | **Objektif boss**; utuh + putus |
| [`ep03_jimat_jenglot.md`](ep03_jimat_jenglot.md) | Kotak jimat jenglot pecah | B | ±0,3 | Clue ★ |
| **Ep 4 — Pasar malam Kampung Kali** | | | | |
| [`ep04_pasar_malam.md`](ep04_pasar_malam.md) | Kios tenda, kios permanen, tiang lampu pasar | B, E | 3–4 per kios | Kit Kampung Kali + prop pasar |
| [`ep04_lilin_ritual.md`](ep04_lilin_ritual.md) | Lilin ritual (raksasa di atap + kecil) | C, E | ±8 tinggi / 0,25 | **Objektif boss**; 1 aset 2 skala |
| **Ep 5 — Kota Lama (makam)** | | | | |
| [`ep05_kota_lama.md`](ep05_kota_lama.md) | Gedung kolonial ×2, museum (hub), lampu jalan | A, E | 20 × 15 × 14 | Kit Kota Lama, dipakai ulang Ep 7, 10, hub |
| [`ep05_makam_tua.md`](ep05_makam_tua.md) | Gerbang + pagar makam, nisan ×3, rumah juru kunci | B, C | per item | ⚠️ Sensitif; zona larangan rusak |
| **Ep 6 — Lereng Gunung** | | | | |
| — | Hutan, sungai berbatu, jalan desa menanjak, air terjun | | | **Tanpa prompt baru**: vegetasi/batu Fab/Megascans + kit Desa bukit Ep 1 |
| **Ep 7 — Kota Lama malam** | | | | |
| [`ep07_stadion_observatorium.md`](ep07_stadion_observatorium.md) | Menara lampu stadion, tribun, observatorium, lampu sorot mobil | A–E | menara ±45 tinggi | **Menara lampu = objektif boss** |
| **Ep 8 — Bukit Kentongan** | | | | |
| [`ep08_kentongan_tampah.md`](ep08_kentongan_tampah.md) | Kentongan genggam + pemukul + tampah | A–E | < 0,5 | Dipegang warga; terasering/desa = kit lama |
| **Ep 9 — Pelabuhan Utara** | | | | |
| [`ep09_pelabuhan.md`](ep09_pelabuhan.md) | Gudang, derek kontainer, peti batu berisi alas arca | B–E | gudang 40 × 25 × 12; derek ±50 tinggi | Derek = samaran genderuwo; peti = clue arca kedua |
| **Ep 10 — Arunapura (finale)** | | | | |
| [`ep10_prasasti_sapta_dwara.md`](ep10_prasasti_sapta_dwara.md) | Prasasti Sapta Dwara (peta tujuh gerbang) | B, E | ±3 × 1 × 5 | Usulan prasasti baru; sisanya pakai ulang semua kit |

Kolom **Adegan** untuk Ep 2–10 memakai zona map A–E dari [docs/28](../../../docs/28-struktur-level-episode.md#2-anatomi-satu-map-episode).

**Tanpa prompt:** batu latihan (batu datar biasa; cukup scan/Fab), tiang listrik, pohon, kit batu candi modular, kontainer, dermaga, jalan layang, interior kantor/server, dan interior hub markas DWARA (Fab/Megascans).

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
