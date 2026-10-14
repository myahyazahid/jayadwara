# Prompt karakter Arc 1 (Ep 1–10) untuk Tripo

> **Status: usulan (14 Okt 2026).** Daftar diambil dari [docs/03](../../docs/03-karakter.md), [docs/05](../../docs/05-daftar-episode-boss.md#arc-1--kebangkitan-ep-110), [docs/16](../../docs/16-panduan-arc-1.md) bagian 6–7, dan [docs/18](../../docs/18-kebutuhan-episode-1.md). Desain tokoh yang belum dikunci di docs (penampilan anggota DWARA, warga, bentuk boss Ep 2–10) adalah **usulan Claude**; ubah bebas, lalu catat keputusan finalnya di docs terkait.
>
> **Scope:** yang dibutuhkan sekarang hanya kelompok **A (Ep 1)**. Ep 2–10 baru diproduksi di Fase 4 ([docs/10](../../docs/10-roadmap.md)), jadi prompt B–D disiapkan lebih awal saja; tidak perlu digenerate sekarang.

Pola prompt mengikuti [`prompt_aksa_turnaround.md`](prompt_aksa_turnaround.md) dan [`prompt_jerangkong.md`](prompt_jerangkong.md).

---

## 0. Aturan umum (berlaku untuk semua prompt)

Pelajaran dari Aksa, Jayadwara2, dan Jerangkong:

1. **Generate 1 sheet berisi 3 view** (depan, samping hadap kiri, belakang) supaya konsisten, lalu **potong jadi 3 file** dengan kanvas, skala, dan posisi telapak yang sama. Masukkan ke Tripo **mode Multiview** (Front / Left / Back). Satu sheet langsung ke mode single image = Tripo membuat 3 karakter.
2. **Celah tembus di siluet**: lengan menjauh dari badan (±40–45°), kaki terbuka, jari lurus agak renggang. Untuk makhluk berkaki empat atau bersayap, aturan setaranya ditulis di prompt masing-masing.
3. **Tidak ada kain/aksesori menjuntai yang menempel ke badan atau kaki** (selendang, sabuk kain, tali panjang). Bagian berayun dibangun terpisah dengan rantai tulang.
4. **Flat unlit**, tanpa bayangan pekat, latar abu-abu polos, **tanpa teks/label**.
5. **Corak besar dan sederhana.** Motif halus dibuat ulang di material UE.
6. Monster: energi Kala **merah gelap**, **tanpa gore**, **tanpa cahaya biru** ([docs/16](../../docs/16-panduan-arc-1.md#27-aturan-konten)).
7. Setelah Tripo: taruh `.glb` di repo → Claude menjalankan gate ukur (celah, pulau mesh, non-manifold, simetri) **sebelum** rig.

Kalimat penutup yang dipakai di semua prompt manusia (sudah tertulis di tiap prompt):

```
Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Simple bold patterns, no fine detail, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

---

## Daftar

| # | Karakter | Episode | Jenis | Tripo? | Catatan |
|---|---|---|---|---|---|
| — | Aksa | semua | Hero manusia | ✅ selesai input | `aksa_turnaround_v02` (tanpa selendang) |
| — | Jayadwara2 | semua | Hero raksasa | ✅ sudah | [docs/25](../../docs/25-rencana-redesign-jayadwara.md) |
| — | Jerangkong + minion kerangka | 1, 10 | Boss + minion | ✅ sudah | [docs/20](../../docs/20-rencana-model-jerangkong.md) |
| A1 | Warga desa ×3 (bapak petani, ibu, pemuda) | 1 (+ semua) | NPC | ✅ | Juga jadi **preman** Ep 4 (ganti tekstur) |
| A2 | Mandor Adikara | 1 | NPC | ✅ | |
| B1 | Kol. (Purn.) Bagas Suryo | 2+ (hub) | Tokoh | ✅ | Ep 1 cukup potret 2D |
| B2 | Dr. Nadia Prameswari | 2+ | Tokoh | ✅ | |
| B3 | Prof. Yahyo Sasmito | 2+ | Tokoh | ✅ | |
| B4 | Ki Sastro | 2+ (ritual Ep 5, 8) | Tokoh | ✅ | Kain jarik → kaki menyatu, lihat catatan |
| B5 | Sekar | 2+ | Tokoh | ✅ | |
| B6 | Bayu Saputra | 2+ (lapangan Ep 7, 9) | Tokoh | ✅ | |
| B7 | Ratna Dewantari | 3, 7, 10 (opsional) | Tokoh | ⚪ | Bisa cukup potret/siaran TV |
| B8 | Gunadi Adikara | opsional | Tokoh | ⚪ | Bisa cukup potret |
| C1 | Tuyul | 2 | Boss + minion | ✅ | Satu model untuk boss & tuyul kecil (pola Jerangkong) |
| C2 | Jenglot | 3 | Boss | ✅ | |
| C3 | Babi Ngepet | 4 | Boss (berkaki empat) | ✅ | |
| C4 | Pocong ⚠️ | 5 | Boss | ✅ | Pedoman sensitivitas |
| C5 | Kemamang | 6 | Boss | ❌ VFX | Bola api + anak api = Niagara, bukan mesh |
| C6 | Kalong Wewe | 7 | Boss (bersayap) | ✅ | |
| C7 | Wewe Gombel | 8 | Boss | ✅ | Zona tubuh tempat anak disembunyikan |
| C8 | Genderuwo | 9 | Boss | ✅ | Grup rig "Buto" (dipakai ulang Arc 3) |
| C9 | Banaspati | 10 | Boss | ✅ (sebagian) | Kepala + tangan = mesh, api = VFX |
| D1 | Kabel hidup | 3 | Minion | ✅ | |
| D2 | Akar hidup | 8 | Minion | ✅ | |
| D3 | Bayang-bayang | 5, 9 | Minion | ❌ | Manny + material siluet gelap |
| D4 | Api kecil | 6, 10 | Minion | ❌ VFX | |
| D5 | Preman | 4 | Minion | ❌ | Pakai ulang A1 + tekstur |

---

## A. Episode 1 (dibutuhkan sekarang)

### A1. Warga desa (3 variasi, satu sheet per variasi)

```
Character turnaround model sheet for a stylized semi-realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same character, same scale, feet aligned on one ground line, wide empty space between views.

Character: an Indonesian village farmer in his 50s, Central Java. Average build, warm brown sun-tanned skin, short gray-black hair, calm neutral expression, mouth closed. Wide conical woven bamboo hat (caping), faded loose button-up work shirt with rolled sleeves, plain dark knee-length shorts, simple rubber sandals.

Pose: strict A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso from armpit to wrist, hands open with fingers straight and slightly spread, palms facing the thighs, feet shoulder-width apart with a clear gap between the legs. Identical pose in all three views.

Important: nothing hanging from the waist, no scarf, no sash, no bag, no tools in hand.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Simple bold patterns, no fine detail, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

Ganti paragraf **Character** untuk variasi lain:

- **Ibu:** `an Indonesian village woman in her 40s, Central Java. Average build, warm brown skin, black hair in a low bun, calm neutral expression, mouth closed. Simple fitted long-sleeve blouse in a plain muted color, ankle-length fitted batik skirt with a large simple pattern, simple flat sandals.` — rok panjang membuat kaki menyatu; terima saja (rig sebagai rok, bobot ke paha) atau ganti `knee-length skirt over plain trousers`.
- **Pemuda:** `an Indonesian village young man around 20, slim build, warm brown skin, short messy black hair, calm neutral expression, mouth closed. Plain t-shirt, open short-sleeve flannel shirt, dark jeans, sneakers.`

### A2. Mandor Adikara

```
Character turnaround model sheet for a stylized semi-realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same character, same scale, feet aligned on one ground line, wide empty space between views.

Character: an Indonesian construction site foreman in his 40s working for a big mining and infrastructure company. Stocky build, warm brown skin, short black hair with a thin mustache, stern neutral expression, mouth closed. White hard hat, orange high-visibility safety vest over a dark gray work shirt, the vest has a simple bold geometric company logo (an abstract stylized sunrise shape, not any real brand), dark cargo work pants, black steel-toe boots. A walkie-talkie clipped tightly on the vest chest.

Pose: strict A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso from armpit to wrist, hands open with fingers straight and slightly spread, palms facing the thighs, feet shoulder-width apart with a clear gap between the legs. Identical pose in all three views.

Important: nothing hanging from the belt, no lanyard, no tools in hand.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos other than the vest emblem. Simple bold patterns, no fine detail, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

---

## B. Anggota DWARA & tokoh (Fase 4, Ep 2+)

Semua memakai blok **Pose** dan penutup yang sama seperti A1. Hanya paragraf **Character** yang berbeda. Penampilan di bawah adalah usulan; docs/03 baru mengunci peran dan sifat.

**Template:**

```
Character turnaround model sheet for a stylized semi-realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same character, same scale, feet aligned on one ground line, wide empty space between views.

Character: <ISI DARI DAFTAR DI BAWAH>

Pose: strict A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso from armpit to wrist, hands open with fingers straight and slightly spread, palms facing the thighs, feet shoulder-width apart with a clear gap between the legs. Identical pose in all three views.

Important: nothing hanging from the waist, no scarf, no sash, no long coat tails, nothing held in the hands.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Simple bold patterns, no fine detail, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

**B1. Kol. (Purn.) Bagas Suryo**
```
Colonel (retired) Bagas Suryo, head of a secret Indonesian anomaly research agency, 55 years old, former military officer. Tall broad build, straight upright posture, warm brown skin, short gray crew-cut hair, gray mustache, strong jaw, stern calm expression, mouth closed. Fitted dark olive field jacket closed with a zipper, plain dark shirt collar visible, dark tactical trousers tucked into black boots, a plain black leather belt, a simple wristwatch. No medals, no rank insignia, no weapons.
```

**B2. Dr. Nadia Prameswari**
```
Dr. Nadia Prameswari, Indonesian energy physicist, 32 years old. Slim build, light-brown skin, shoulder-length straight black hair tied in a low ponytail, thin rectangular glasses, sharp skeptical neutral expression, mouth closed. Short fitted white lab jacket worn closed over a dark turtleneck, a small handheld scanner device clipped flat on the hip, slim dark trousers, simple flat shoes.
```
(Opsional: ganti rambut dengan `a plain dark hijab neatly tucked into the collar`.)

**B3. Prof. Yahyo Sasmito**
```
Professor Yahyo Sasmito, Indonesian historian and philologist, 68 years old. Slightly thin build, slight stoop, warm brown skin, neat white hair and short white beard, round glasses, kind but secretive neutral expression, mouth closed. Long-sleeve batik shirt with a large simple brown pattern, a plain dark vest over it, plain dark trousers, brown leather shoes.
```

**B4. Ki Sastro** — kain jarik panjang akan menyatukan kedua kaki. Pilihan: jarik selutut + celana panjang hitam (dipakai di prompt), atau jarik penuh lalu di-rig sebagai rok.
```
Ki Sastro, Javanese cultural elder and wayang shadow puppet master (dalang), 70 years old. Small slim build, warm brown skin, wrinkled kind face, thin white mustache, gentle neutral expression, mouth closed. Dark batik blangkon headcloth, closed dark beskap jacket with a high collar and simple buttons, a knee-length brown batik jarik cloth wrapped tightly around the waist over plain black trousers, simple dark sandals. No keris, no weapon.
```

**B5. Sekar**
```
Sekar, youngest member of the agency, Indonesian hacker and mission operator, 19 years old. Petite slim build, light-brown skin, short black bob haircut with straight bangs, lively curious neutral expression, mouth closed. A compact wireless headset with a small mic on one ear, oversized dark gray hoodie with the hood down and a simple bold geometric print, dark slim cargo pants, chunky white sneakers.
```

**B6. Bayu Saputra**
```
Bayu Saputra, field agent and former police intelligence officer, 28 years old. Athletic medium build, warm brown skin, short undercut black hair, light stubble, relaxed friendly neutral expression, mouth closed. Fitted olive-green bomber jacket closed with a zipper, plain gray t-shirt collar visible, dark jeans, brown leather work boots, fingerless driving gloves.
```
(Bedakan siluet dari Aksa: jaket hijau zaitun tertutup, bukan navy terbuka.)

**B7. Ratna Dewantari (opsional)**
```
Ratna Dewantari, Indonesian member of parliament and government liaison, 45 years old. Slim upright build, light-brown skin, professional cold neutral expression, mouth closed. Black hair in a neat bun, a fitted dark maroon blazer closed with one button over a plain cream blouse, slim matching trousers, low black heels, a small gold lapel pin.
```

**B8. Gunadi Adikara (opsional)**
```
Gunadi Adikara, CEO of a large Indonesian mining and infrastructure group, 58 years old. Tall build with a slight belly, warm brown skin, slicked-back gray-black hair, confident calm neutral expression, mouth closed. Tailored charcoal suit, closed jacket, plain white shirt, dark tie, a small abstract sunrise-shaped gold lapel pin, polished black shoes.
```

---

## C. Boss Ep 2–10 (Fase 4)

Boss digenerate dalam skala manusia dulu (seperti Jerangkong). Ukuran raksasa diatur di UE ([docs/16](../../docs/16-panduan-arc-1.md#26-aturan-skala)).

### C1. Tuyul (Ep 2) — boss + minion satu model

```
Monster character turnaround sheet for a stylized semi-realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, feet aligned on one ground line, wide empty space between views.

Creature: Tuyul, a small mischievous goblin spirit from Javanese folklore, enlarged by dark red cursed energy. Short stocky body, about 3.5 heads tall, completely bald oversized head, large pointed ears, big round glowing dark red eyes, wide cheeky grin with closed mouth, small sharp nose. Grayish olive-green skin with a few darker blotches. Wears only a plain faded brown loincloth wrapped tightly at the waist. Thin dark red glowing veins on the back of the head.

Pose: A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso, hands open with long fingers spread, legs apart with a clear gap.

Important: playful and creepy, not a human child, clearly a goblin creature. No gore, no blood. No blue light. Nothing held in the hands.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Chunky simplified shapes, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

### C2. Jenglot (Ep 3)

```
Monster character turnaround sheet for a stylized semi-realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, feet aligned on one ground line, wide empty space between views.

Creature: Jenglot, a tiny dried mummified charm figure from Javanese folklore, grown huge by absorbing electricity and dark red cursed energy. Thin hunched humanoid body, dry dark brown leathery skin stretched over bones, extremely long straight black hair falling down the back to the knees as one thick solid mass, long thin fingers with long dark nails, small fangs visible, glowing dark red eyes. Thick black electrical cables wrapped tightly around the arms, legs, and torso like bandages, with broken plugs and small transformer parts stuck in the back. Cracks in the skin glow dark red with bright yellow-white electric sparks.

Pose: A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso, fingers spread, legs apart with a clear gap. Hair stays a solid mass behind the back, not touching the arms.

Important: eerie, not gory. No blood, no exposed organs. No blue light: electricity is yellow-white, cursed energy is dark red. No cables hanging loose.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Chunky simplified shapes, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

### C3. Babi Ngepet (Ep 4) — berkaki empat

```
Monster creature turnaround sheet for a stylized semi-realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, hooves aligned on one ground line, wide empty space between views.

Creature: Babi Ngepet, a cursed black wild boar from Javanese black-magic folklore, created by a greedy wealth ritual and enlarged by dark red cursed energy. Long low muscular body (body length about 2.5 times its shoulder height), thick black bristly hide shaped as large chunky clumps, short curved yellowish tusks, small glowing dark red eyes, a ridge of stiff black bristles along the spine. Faint dark red glowing cracks on the flanks shaped like dripping candle wax. A short tail.

Pose: neutral standing pose, all four legs straight and vertical, front legs apart and hind legs apart with clear gaps between all legs, head straight forward, mouth closed, tail held away from the hind legs.

Important: menacing but not gory. No blood. No blue light. No saddle, no ropes, no candles on the body.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Chunky simplified shapes, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

### C4. Pocong (Ep 5) ⚠️

Pedoman: tanpa olok-olok terhadap kafan atau pemakaman, tanpa wajah busuk, nada sedih dan khidmat ([docs/06](../../docs/06-referensi-mitologi.md#catatan-per-boss-️), [docs/16](../../docs/16-panduan-arc-1.md#ep-5--tali-yang-belum-dilepas--pocong-️)). Bentuknya satu badan terbungkus, jadi bebas masalah celah lengan/kaki. Tiga simpul = titik lemah (mekanik bidik bagian tubuh).

```
Spirit creature turnaround sheet for a stylized semi-realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same figure, same scale, base aligned on one ground line, wide empty space between views.

Creature: a restless wrapped spirit from Javanese folklore whose shroud ties were never untied, enlarged by dark red cursed energy. A tall upright body fully wrapped in old off-white cloth, slightly weathered and dusty, smooth simplified fabric folds, no arms or legs visible. Three large thick knotted ties: one above the head, one around the neck, one around the ankles, each knot glowing softly dark red as a clear weak point. The face area is a deep calm shadow with two faint glowing dark red eyes, no visible rotting flesh.

Pose: standing perfectly straight and still, feet together inside the wrapping.

Important: solemn, sorrowful and eerie, not comedic and not grotesque. No blood, no decay, no gore, no exposed skin. No blue light. No grave or tombstone in the image.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Simple bold shapes, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

### C5. Kemamang (Ep 6) — tidak lewat Tripo

Bola api + anak api lebih cocok dibuat sebagai Niagara (VFX) di atas mesh inti sederhana (bola + retakan), bukan mesh Tripo. Kalau butuh referensi visual untuk VFX:

```
Concept art of Kemamang, a floating will-o'-the-wisp fire spirit from Javanese folklore, enlarged by dark red cursed energy: a large sphere of orange-yellow fire with a darker red molten core and two hollow glowing eyes, surrounded by many small floating fireballs. Hovering over a forest river at night. Single 3/4 view, stylized semi-realistic game concept art, no text, no blue fire.
```

### C6. Kalong Wewe (Ep 7) — bersayap

```
Monster creature turnaround sheet for a stylized semi-realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, feet aligned on one ground line, wide empty space between views.

Creature: Kalong Wewe, a giant cursed bat spirit from Sundanese folklore, enlarged by dark red cursed energy. Hunched humanoid bat body with digitigrade legs and clawed feet, large pointed ears, flat bat nose, glowing dark red eyes, mouth closed. Short thick dark brown fur shaped as large chunky clumps on the body. Huge leathery wings attached to the arms, wingspan about 3 times its height, thin dark gray-brown membrane with clear finger bones, tattered edges at the tips only. Faint dark red glowing veins in the wing membranes.

Pose: standing upright, wings fully spread horizontally to the sides, wings not overlapping the body or legs, legs apart with a clear gap.

Important: menacing, not gory. No blood. No blue light. The creature is sensitive to light: its eyes are small and squinting.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Chunky simplified shapes, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

### C7. Wewe Gombel (Ep 8)

Legenda versi rakyat menonjolkan tubuh perempuan tua dengan payudara menjuntai; **tidak dipakai** (rating remaja). Sisi simpatik: ia menyembunyikan anak terlantar. Zona tubuh tempat anak disembunyikan harus terbaca jelas (mekanik zona larangan pukul).

```
Monster character turnaround sheet for a stylized semi-realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, feet aligned on one ground line, wide empty space between views.

Creature: Wewe Gombel, a tall gaunt forest spirit from Central Javanese folklore who hides neglected children, enlarged by dark red cursed energy. Very tall thin hunched figure with long arms, gray-brown bark-like skin, a sad tired old face with deep-set glowing dark red eyes, mouth closed. Very long gray-black hair falling down the back as one thick solid mass merging into a long cloak of tangled roots, vines and dry leaves that covers the body like a fitted robe. Three clearly visible woven nest-like hollows on the body (on the chest, the belly, and the back), each lined with soft warm yellow light, where children are hidden safely inside.

Pose: A-pose, long arms straight and angled 45 degrees away from the body, clear empty space between arms and torso, long fingers spread, legs apart with a clear gap under the robe.

Important: sorrowful and eerie, sympathetic, not grotesque and not sexualized. No exposed breasts, no gore, no blood. No children visible in the image, only the glowing hollows. No blue light.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Chunky simplified shapes, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

### C8. Genderuwo (Ep 9) — grup rig Buto

Rig dipakai ulang untuk Buto Arc 3, jadi proporsinya **humanoid raksasa** standar (bisa diretarget ke Manny).

```
Monster character turnaround sheet for a stylized semi-realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, feet aligned on one ground line, wide empty space between views.

Creature: Genderuwo, a huge hairy ape-like spirit from Javanese folklore that lives in old buildings and big trees and can turn invisible, enlarged by dark red cursed energy. Massive broad humanoid body about 7 heads tall, heavy shoulders and long powerful arms, thick legs. Covered in long coarse dark reddish-brown fur shaped as large chunky clumps, the fur lies close to the body. Heavy brow, flat wide nose, small tusks from the lower jaw, glowing dark red eyes, mouth closed. Dark gray skin visible on the face, chest, palms and soles. A few faint dark red glowing streaks in the fur.

Pose: A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso from armpit to wrist, hands open with fingers spread, feet shoulder-width apart with a clear gap between the legs.

Important: intimidating, not gory. No blood. No blue light. No clothing, no weapons, nothing held in the hands.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Chunky simplified shapes, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

### C9. Banaspati (Ep 10, finale)

Mesh = kepala besar + dua lengan; api = VFX di UE. Jalan dengan tangan, kepala di bawah.

```
Monster creature turnaround sheet for a stylized semi-realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, hands aligned on one ground line, wide empty space between views.

Creature: Banaspati, a fire demon from Javanese folklore that walks on its hands with its head down, enlarged by dark red cursed energy. A huge round demonic head made of cracked dark volcanic stone with glowing orange-red molten cracks, large glowing eyes, a wide mouth with big stone fangs, wild flame-shaped stone hair. Two massive long muscular arms grow from the top of the head and plant into the ground like legs, with big clawed stone hands flat on the ground. No torso, no legs.

Pose: standing upside down on its two hands, arms straight and spread wide apart with a clear gap between them, the head hanging between and above the arms.

Important: draw the body as solid stone and lava shapes only, no separate loose flames or smoke. No blood, no gore. No blue fire.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Chunky simplified shapes, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

---

## D. Minion baru (Fase 4)

### D1. Kabel hidup (Ep 3)

```
Minion creature turnaround sheet for a stylized semi-realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, feet aligned on one ground line, wide empty space between views.

Creature: a human-sized living tangle of thick black electrical cables shaped like a thin humanoid, animated by dark red cursed energy. The cables are bundled tightly into limbs and a torso, a broken electrical junction box as the head with one glowing dark red slot as an eye, plugs and sockets on the shoulders, small yellow-white sparks at the joints.

Pose: A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso, cable fingers spread, legs apart with a clear gap.

Important: no loose cables hanging from the body. No blue light.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Chunky simplified shapes, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

### D2. Akar hidup (Ep 8)

```
Minion creature turnaround sheet for a stylized semi-realistic 3D action game, three orthographic views side by side: FRONT view, SIDE view (left profile), BACK view. Same creature, same scale, feet aligned on one ground line, wide empty space between views.

Creature: a human-sized walking bundle of tree roots and dry branches shaped like a hunched humanoid, animated by dark red cursed energy from a hill forest. Thick roots twisted tightly into limbs and a torso, a knotted wooden head with two glowing dark red hollows as eyes, a few dry leaves and moss stuck on the shoulders.

Pose: A-pose, arms straight and angled 45 degrees away from the body, clear empty space between arms and torso, twig fingers spread, legs apart with a clear gap.

Important: no thin loose twigs sticking out, keep the silhouette chunky. No blue light.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. Chunky simplified shapes, consistent across all three views, suitable as an orthographic reference for image-to-3D generation.
```

### D3–D5

- **Bayang-bayang (Ep 5, 9):** skeleton/mesh Manny + material siluet gelap berasap (Claude bisa siapkan master material-nya). Tidak lewat Tripo.
- **Api kecil (Ep 6, 10):** Niagara, sama dengan Kemamang.
- **Preman (Ep 4):** pakai ulang mesh warga A1 (pemuda) dengan tekstur jaket kulit/kaos gelap.

---

## Setelah gambar jadi

- Simpan sheet di `docs/concept-art/` (`<nama>_v01.png`), lalu potong jadi 3 file (`<nama>_front/left/back.png`, kanvas & skala sama, label dibuang).
- Cek cepat sebelum Tripo: celah lengan-badan & antar kaki tembus di ketiga view, tidak ada kain menempel ke kaki, tinggi kepala & telapak sama di ketiga view.
- Boss & tokoh yang sudah final: buat model sheet (pola [docs/21](../../docs/21-model-sheet-aksa.md), [docs/24](../../docs/24-model-sheet-jerangkong.md)) sebelum modeling.
