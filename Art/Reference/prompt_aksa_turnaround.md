# Prompt referensi Aksa (untuk generator gambar)

Dasar: `docs/concept-art/Aksa versi Final.png`, dengan perubahan: **Transformation Device dibuang** (terlalu mirip Mebius Brace, docs/01) dan diganti **kalung pecahan arca**. Tujuannya referensi ortografis untuk modeling, seperti `Art/Reference/` Jayadwara.

## 1. Turnaround badan (rasio 2:1)

```
Character turnaround model sheet for a stylized 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same character, same scale, feet aligned on one ground line, evenly spaced, plain flat light-gray background, flat even studio lighting, no shadows on the background, no text, no labels, no logos.

Character: Aksa, a 25-year-old Indonesian man, former national pencak silat athlete. Lean athletic build, about 7.5 heads tall. Warm brown skin, short messy black hair, thick straight eyebrows, brown eyes, calm neutral expression, mouth closed.

Pose: neutral A-pose for 3D modeling, standing straight, arms straight and angled about 35 degrees away from the body, palms facing the thighs, fingers relaxed and slightly apart, feet shoulder-width apart, looking straight ahead. Identical pose in all three views.

Outfit: dark navy waist-length field jacket worn open, high stand-up collar lined with a brown-and-gold Javanese batik pattern, sleeves rolled up to mid-forearm, small gold stitched accents on the shoulders, a small gold ornamental emblem embroidered on the upper back. Plain black crew-neck t-shirt underneath. A gold necklace with a small pendant: a fragment of carved gray stone set in a simple gold frame, resting on the chest. Black leather belt with a simple gold buckle. Dark charcoal cargo pants with side pockets and thin straps on the thighs. A long dark-brown batik sash with gold pattern tied at the left hip, hanging down to the knee. Plain black fingerless leather gloves. Black lace-up combat boots with thin gold trim.

Important: bare forearms and wrists apart from the gloves. No gauntlet, no bracer, no bracelet, no wristband, no armor, no device on the arms. No glowing parts anywhere. No silver or metallic chrome, no blue light.

Style: clean stylized semi-realistic game character concept art, crisp readable silhouette, consistent proportions and outfit details across all three views, suitable as an orthographic modeling reference.
```

## 2. Kepala depan + samping (rasio 2:1)

```
Head and face model sheet for a stylized 3D game character, two orthographic views side by side: FRONT view and SIDE view (left profile), same scale, eyes and chin aligned on the same horizontal lines, plain flat light-gray background, flat even lighting, no text, no labels.

Character: Aksa, a 25-year-old Indonesian man, warm brown skin, short messy black hair with a few strands falling over the forehead, thick straight eyebrows, brown eyes, straight nose, defined jaw, calm neutral expression, mouth closed, looking straight ahead. Visible: head, neck, and the high batik-lined collar of a navy jacket.

Style: clean stylized semi-realistic game character concept art, consistent features between the two views, suitable as an orthographic modeling reference.
```

## Hasil yang diharapkan
- Pose A identik di ketiga view, kaki sejajar di satu garis tanah (bisa dinormalisasi `Art/Scripts/make_reference_planes.py`).
- Tidak ada alat di lengan; kalung terlihat di depan.
- Simpan hasilnya di `docs/concept-art/` (mis. `aksa_turnaround_v01.png`, `aksa_head_v01.png`).
