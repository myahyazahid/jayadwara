# Aksa Jaya Mangkubumi

| | |
|---|---|
| **Episode** | Semua (tokoh utama) |
| **Peran** | Hero manusia |
| **Prioritas** | **Ep 1, sekarang** |
| **Tripo** | ✅ badan + pakaian; wajah final mungkin MetaHuman ([08](../../../docs/08-requirement-produksi.md#keputusan-terbuka) #5) |
| **Sumber** | [03](../../../docs/03-karakter.md), [21 model sheet](../../../docs/21-model-sheet-aksa.md) |

Aturan umum, cara potong, dan cek sebelum Tripo: [README](README.md).

## Catatan

- Konsep lama (`aksa_turnaround_v01`, versi tanpa selendang) bergaya ilustrasi anime: outline + cel shading akan terpanggang ke tekstur Tripo. Pakai **Prompt 2 (edit)** dengan gambar lama sebagai input supaya desain tidak berubah, atau Prompt 1 dari nol.
- **Tanpa selendang** di input. Selendang dibangun terpisah (rantai `sash_01..06`, spesifikasi D3 di [21](../../../docs/21-model-sheet-aksa.md)).
- Kalung kemungkinan jadi benjolan di dada; dibuat terpisah.
- Tepi depan jaket terbuka tipis, mungkin perlu dirapikan setelah generate.

## Prompt 1: turnaround dari nol

```
Character turnaround model sheet for a realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same character, same scale, feet aligned on one ground line, wide empty space between views.

Character: Aksa, a 25-year-old Indonesian man, former national pencak silat athlete. Lean athletic build, about 7.5 heads tall. Warm brown skin with natural texture, short messy black hair, thick straight eyebrows, brown eyes, calm neutral expression, mouth closed. Dark navy denim waist-length field jacket worn open, thick fitted fabric with visible edge thickness, high stand-up collar lined with a brown-and-gold Javanese batik pattern visible on the front and back, sleeves rolled up to mid-forearm, small gold stitched accents on the shoulders, a small gold ornamental emblem on the upper back. Plain black cotton crew-neck t-shirt. A gold necklace with a small pendant: a fragment of carved gray stone in a simple gold frame, resting on the chest. Black leather belt with a square gold buckle. Dark charcoal cargo pants with one flap cargo pocket on the outer side of each thigh, pockets tight against the leg. Black fingerless leather gloves. Black leather lace-up combat boots with thin gold trim.

Pose: strict A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso from armpit to wrist, hands open with fingers straight and slightly spread, palms facing the thighs, feet shoulder-width apart with a clear gap between the legs. Identical pose in all three views.

Important: no sash, no scarf, no cloth hanging from the belt, nothing dangling from the waist. Bare forearms and wrists apart from the gloves. No gauntlet, no bracer, no bracelet, no armor, no device on the arms. No glowing parts. No outlines, no cel shading, no anime style.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Realistic materials, simple bold patterns, no fine detail, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

## Prompt 2: edit dari konsep lama (image-to-image)

```
Convert this character into a realistic 3D game character render, keeping the exact same design, outfit, colors, pose and proportions. Realistic Indonesian man, 25 years old, realistic skin with natural texture, realistic face, short messy black hair with real hair strands. Navy denim field jacket with real fabric texture, brown-and-gold batik lining on the collar, gold trim stitching, black cotton t-shirt, charcoal cargo pants with real fabric folds, black fingerless leather gloves, black leather combat boots with gold trim, gold necklace with a gray carved stone pendant.

Turnaround: three orthographic views side by side, FRONT view, SIDE view (left profile), BACK view, same scale, feet aligned on one ground line, wide empty space between views. Strict A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso, hands open with fingers straight and slightly spread, palms facing the thighs, feet shoulder-width apart.

No outlines, no cel shading, no anime style. Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels. Like a clean 3D character render for image-to-3D generation.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/aksa_v01.png`, potong jadi `aksa_front/left/back.png` (kanvas, skala, dan telapak sama), lalu Tripo Multiview.
