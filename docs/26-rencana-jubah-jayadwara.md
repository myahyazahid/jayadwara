# 26 — Rencana Jubah Upacara Jayadwara

> **Status: v0.1 — usulan (13 Okt 2026), menunggu jawaban developer di bagian 4.**
> Desain: K9 di [14](14-model-sheet-jayadwara.md); alur gameplay: [07](07-gameplay-sistem.md#jubah-upacara); konsep: [`concept-art/jayadwara_jubah_upacara.webp`](concept-art/jayadwara_jubah_upacara.webp).
> Jadwal: masuk **Fase 2** bareng cutscene transformasi ([23](23-rencana-fase-1.md) "Tidak masuk"). J0–J3 (aset) boleh ditarik lebih awal sebagai jalur art paralel kalau developer mau; J4–J5 butuh lock-on (Fase 1 Iterasi 6) dan Sequencer (F2).

---

## 1. Tujuan & syarat selesai

- [ ] `SK_Jayadwara2_Cape` (mesh terpisah) mengikuti pose `SK_Jayadwara2` tanpa mengubah mesh, skeleton, atau bobot badan yang sudah final ([25](25-rencana-redesign-jayadwara.md)).
- [ ] Bentuk & warna sesuai konsep: merah-putih-emas, panel putih tengah & sisi, rantai emas, ujung runcing bermotif. **Kerah ≤ dagu, tidak mekar ke belakang kepala** (K9).
- [ ] Kain bergerak wajar saat idle, jalan, berbalik, angin; tidak menembus kaki/badan pada skala 45 m.
- [ ] Pakai/lepas: lepas ±2 s (lock-on pertama), lepas cepat ±0,5 s (aksi combat pertama, input tidak hilang), pakai kembali (menang/kepergian), bisa di-skip. Jubah buyar jadi cahaya, tidak jatuh ke tanah.
- [ ] Tidak ada biaya jubah saat combat (mesh disembunyikan, simulasi mati).
- [ ] LOD0–LOD2, satu slot material (pola R8 [25](25-rencana-redesign-jayadwara.md)), lulus validator.
- [ ] Dipakai di cutscene transformasi Ep 1 (Sequencer) dan disetujui developer di Play.

## 2. Titik awal

| Item | Kondisi |
|---|---|
| Badan | `SK_Jayadwara2` final (89 tulang, rantai `cloth_back_01…03` ada **tanpa mesh**), `ABP_Jayadwara2`, `BP_Jayadwara2` |
| Konsep | Satu sheet AI (front/side/back/3/4 + breakdown). Pauldron & rantai di sheet ikut model yang ada, bukan dibuat ulang |
| Pelajaran dari Jayadwara2 | Lembar kain yang menempel ke badan memecah skinning (R2–R3d); Anim Dynamics tanpa batas melempar kain (R3d). Jubah dibuat **terpisah dari awal** dan tidak menyentuh kulit |
| C++ | Belum ada apa pun untuk jubah. Lock-on & transformasi ada di rencana Fase 1 |

## 3. Arsitektur (usulan)

- **Mesh & skeleton terpisah:** `SK_Jayadwara2_Cape` dengan skeleton sendiri = tulang induk yang sama namanya dengan Jayadwara2 (`root`…`spine_05`, `clavicle_l/r`, `neck_01`) + rantai jubah baru `cape_c/l/r_01…06`. Skeleton badan **tidak diubah** (tidak perlu impor ulang `SK_Jayadwara2`).
- **Ikut pose:** `ABP_Jayadwara2_Cape` → *Copy Pose From Mesh* dari mesh badan, lalu simulasi di rantai `cape_*`.
- **Simulasi:** Chaos Cloth di mesh jubah dengan collider kapsul dari Physics Asset badan (paha, betis, pinggul, punggung). Cadangan: Anim Dynamics **berbatas kecil** di rantai `cape_*` (pelajaran R3d).
- **Rantai emas:** kaku, di-skin ke `spine_05`/`clavicle_*`, tidak disimulasi.
- **C++:** `UJDCapeComponent` di karakter raksasa: `SetCapeEquipped(bool, bInstant)`, state (`Equipped`, `Removing`, `Removed`, `Returning`), event untuk montage & Niagara. Pemicu dari lock-on pertama & aksi combat pertama (ability tag), pakai kembali dari event menang/cutscene. Logika di C++, montage/Niagara dirangkai di Blueprint.

## 4. Pertanyaan untuk developer (default dipakai kalau belum dijawab)

| # | Pertanyaan | Default |
|---|---|---|
| J-Q1 | Bentuk jubah dibuat dari mana? | **Developer buat di Tripo** dari sheet konsep (gaya sama dengan Jayadwara2, pola jalur B). Alternatif: Claude bangun dari skrip Blender (lebih rapi topologinya, gaya lebih kaku) |
| J-Q2 | Simulasi kain | **Chaos Cloth**; fallback Anim Dynamics berbatas |
| J-Q3 | Animasi lepas/pakai | Developer cari/keyframe di editor (Control Rig) dari referensi pose; Claude siapkan notify & montage lewat skrip. Placeholder: lepas = jubah langsung buyar tanpa gerak tangan |
| J-Q4 | Kapan mulai | **Fase 2** (default). Atau J0–J3 sekarang sebagai jalur art paralel |
| J-Q5 | Panjang jubah | Sesuai konsep (sampai mata kaki), karena tidak dipakai di combat |

## 5. Iterasi

| # | Iterasi | Isi | Claude | Developer | Gate | Estimasi |
|---|---|---|---|---|---|---|
| **J0** | Persiapan | Ukur titik kait di mesh Jayadwara2 rest (bawah pauldron, punggung atas, tengkuk); sheet ortografis jubah dari konsep; jawab J-Q1–Q5 | Ukur & render referensi Jayadwara2 depan/samping/belakang dengan garis bantu kait | Pilih jalur bentuk; (Tripo) buat jubah dari sheet | Titik kait & panjang disepakati | 2–4 j |
| **J1** | Spike bentuk + rig | Jubah kasar ditempel ke Jayadwara2, skeleton jubah + rantai `cape_*`, bobot, ekspor FBX, impor UE, Copy Pose From Mesh | Normalisasi skala/posisi, pisah dari kulit (jarak minimal ke badan), rig & bobot, skrip impor/setup UE | Nilai siluet di Play (idle, jalan) | Jubah ikut badan di idle & jalan tanpa celah/menembus; developer bilang lanjut | 6–10 j |
| **J2** | Bentuk final & tekstur | Panel putih, rantai emas kaku, ujung bermotif, tepi tertutup; satu material; LOD0–2 | Bersih-bersih mesh, UV, mask zona (merah/putih/emas), LOD, validator | Tuning warna di MI | Validator lulus, cek IP (kerah ≤ dagu) | 6–10 j |
| **J3** | Kain bergerak | Chaos Cloth + collider; uji idle, jalan, berbalik, angin, lompat | Setup cloth & collider lewat skrip sejauh API mengizinkan, uji tangkap layar | Tuning parameter kain di editor, nilai di Play | Tidak menembus kaki, tidak terlempar; FPS tidak turun berarti | 4–8 j |
| **J4** | Pakai/lepas | `UJDCapeComponent`, pemicu lock-on & aksi pertama, montage lepas/cepat/pakai, Niagara buyar/kembali, skip | C++ komponen + state + pemicu, notify, skrip montage, uji otomatis PIE | Animasi (J-Q3), efek Niagara, rasa timing | Alur [07](07-gameplay-sistem.md#jubah-upacara) jalan penuh; input serangan tidak hilang; tanpa jubah tidak ada biaya cloth | 8–12 j |
| **J5** | Cutscene & polish | Kedatangan berjubah di cutscene transformasi Ep 1, pose menang/kepergian, LOD layar | Bantu track Sequencer lewat skrip, cek LOD/FPS | Sutradarai cutscene | Developer setuju di Play | 3–6 j |

**Total ±29–50 jam.** J0–J3 tidak bergantung pada combat; J4 butuh lock-on (Fase 1 Iterasi 6); J5 butuh cutscene transformasi (F2).

## 6. Risiko

| Risiko | Mitigasi |
|---|---|
| Kain menembus kaki pada langkah lebar (seperti R3c) | Jubah tidak menyentuh kulit sejak J1; collider kapsul paha/betis; tidak dipakai di combat |
| Chaos Cloth susah diatur lewat skrip (Claude tidak bisa edit `.uasset` langsung) | Tuning di editor oleh developer; fallback Anim Dynamics berbatas |
| Animasi lepas tidak ada sumbernya | Placeholder buyar tanpa gerak (J-Q3) supaya alur C++ tetap bisa diuji |
| Mesh Tripo jubah menyatu/bertopologi berantakan | Pola Jayadwara2: pemisahan lembar via ketebalan, tutup tepi; atau jalur skrip (J-Q1) |
| Scope melebar ke Fase 1 | Jadwal default F2; Fase 1 tetap tanpa jubah ([23](23-rencana-fase-1.md)) |

## 7. Hasil iterasi

_(diisi saat iterasi berjalan)_
