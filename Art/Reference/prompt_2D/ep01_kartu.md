# Kartu judul + kartu "Episode berikutnya"

| | |
|---|---|
| **Adegan** | 6 (judul **JAYADWARA** setelah transformasi), 11 (kartu "Episode berikutnya", ±10 detik) |
| **Isi** | Latar untuk judul; 3 potongan gambar Ep 2 "Tangan-Tangan Kecil" |
| **Sumber** | [17 adegan 6 & 11](../../../docs/17-skenario-arc-1.md#adegan-11--kartu-episode-berikutnya--ui), [31](../../../docs/31-desain-level-ep02.md) |

Aturan umum: [README](README.md).

## Catatan

- **Huruf judul tidak di-generate.** Logo JAYADWARA dibuat terpisah (aplikasi grafis/UMG); AI hanya untuk latar.
- Di game, kartu judul adegan 6 kemungkinan besar dirender langsung dari kamera Sequencer (Jayadwara 3D asli + teks). Prompt 1 untuk **acuan komposisi** dan bahan trailer/poster.
- Kartu "Episode berikutnya" ala serial tokusatsu: 3 potongan cepat + judul. Tiap potongan = 1 gambar. Ep 2 bernada **siang terang, ringan, jahil** ([31](../../../docs/31-desain-level-ep02.md#1-ringkasan)), kontras dengan Ep 1.
- Tuyul **jangan** diperlihatkan jelas (desain belum dikunci, [27](../../../docs/27-rencana-model-tuyul.md)); cukup siluet/sekilas.

## Prompt 1: latar kartu judul

```
Cinematic key art for a realistic Indonesian tokusatsu action game, wide 16:9 frame, low heroic camera angle. A 45-meter-tall armored giant warrior stands in a low pencak silat horse stance (kuda-kuda) on a hilltop temple plateau, both hands at chest height in a guarding pose, never raised above the shoulders. Glossy deep red and black armor with antique gold trim, a white faceplate, golden horn crest on the helmet, a static gold gem on the chest, side cloth panels swaying. Behind him a blood-red dusk sky, an ancient Javanese stone temple gate silhouette, dust and small floating stone fragments in the air. Empty space across the lower third for a title.

Realistic, epic, cinematic lighting with warm rim light. No text, no letters, no logos, no bracelet or device on the arms, no blue light.
```

## Prompt 2–4: potongan "Episode berikutnya" (Ep 2)

```
Cinematic still for a realistic Indonesian action game, wide 16:9 frame. A narrow, dense urban kampung alley in bright midday sun, plastered houses with rusty corrugated metal roofs, laundry lines and tangled cables overhead, a yellow suspension footbridge visible at the far end over a river. Lively, warm, slightly playful mood.

Realistic photographic lighting. No people, no text, no letters, no logos.
```

```
Cinematic close-up still for a realistic Indonesian action game, 16:9 frame. On a whitewashed kampung house wall in daylight, a trail of small bare child-sized footprints climbing straight up the wall toward the rusty metal roof, the footprints glowing faintly dark red as if seen through a scanner, a thin red scan line passing across the wall.

Realistic photographic lighting. No people, no text, no letters, no logos, no blue light.
```

```
Cinematic still for a realistic Indonesian action game, wide 16:9 frame, late afternoon golden light. Rooftops of a dense kampung with rusty corrugated metal roofs, and on a distant roof a small mischievous goblin-like silhouette, bald with a round head and big ears, crouching and holding a small stolen metal cash box, backlit so only its shape is visible. Playful and sneaky mood.

Realistic photographic lighting. Silhouette only, no clear face, not a human child, no text, no letters, no logos.
```

## Setelah gambar jadi

Simpan di `docs/concept-art/2d/kartu_<judul|ep02_a|ep02_b|ep02_c>_v01.png`. Teks "Episode berikutnya" dan judul episode ditambahkan di widget UI.
