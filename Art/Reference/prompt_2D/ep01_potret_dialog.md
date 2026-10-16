# Potret dialog Ep 1

| | |
|---|---|
| **Adegan** | 2 (briefing), 3–5 dan 7 (KOMS), 9 (debrief) |
| **Pemakaian** | **DIALOG**: potret besar setengah badan di samping kotak teks, gameplay berhenti. **KOMS**: potret kecil (dipotong bulat/kotak) di pojok, gameplay jalan terus |
| **Tokoh** | Aksa, Kol. Bagas, Sekar, Dr. Nadia, Prof. Yahyo, Ki Sastro, mandor + ikon Sang Penjaga (Gunadi hanya di stinger) |
| **Sumber** | [17 Daftar Produksi](../../../docs/17-skenario-arc-1.md#karakter-yang-perlu-potret--suara), [18 F](../../../docs/18-kebutuhan-episode-1.md#f-ui--narasi), [12](../../../docs/12-technical-design.md) |

Aturan umum: [README](README.md).

## Catatan

- **Satu gaya untuk semua:** lukisan digital semi-realistis, setengah badan, menghadap 3/4 ke kanan (kotak teks di kanan), latar polos gelap. Satu potret bisa dipakai untuk DIALOG (penuh) dan KOMS (dipotong di wajah).
- Generate **Aksa dulu**, lalu pakai sebagai *style reference* untuk tokoh lain supaya seragam.
- Penampilan = deskripsi di [`prompt_karakter/`](../prompt_karakter/README.md) (diringkas di bawah); kalau diubah di sana, ubah juga di sini.
- **Ekspresi** yang dibutuhkan skenario Ep 1 (minimum):
  - Aksa: netral, terkejut/tegang (briefing: "Lawang Sapta"), fokus (combat), lelah + lecet (debrief, berselimut).
  - Sekar: ceria, panik (adegan 5 dan 7).
  - Bagas, Nadia, Yahyo: netral; Nadia curiga (debrief).
  - Ki Sastro, mandor: netral.
- Varian ekspresi: generate ulang dengan *seed*/referensi yang sama, ubah hanya bagian `Expression:`.

## Template

Salin, lalu ganti `[CHARACTER]` dan `[EXPRESSION]`:

```
Character portrait for a dialogue box in a realistic Indonesian action game, half-body bust from mid-chest up, three-quarter view facing slightly to the right, looking at the viewer. [CHARACTER] Expression: [EXPRESSION].

Style: semi-realistic digital painting, natural skin tones, soft cinematic key light from the upper left with a subtle warm rim light, painterly but clean edges, consistent character portrait series. Plain dark charcoal background with a soft vignette. No text, no letters, no frame, no logo, no hands in front of the face.
```

## Isi `[CHARACTER]`

| Tokoh | Teks |
|---|---|
| **Aksa** | `Aksa, a 25-year-old Indonesian man and former national pencak silat athlete, lean athletic build, warm brown skin, short messy black hair, thick straight eyebrows, brown eyes. Dark navy denim field jacket worn open with a high stand-up collar lined with brown-and-gold batik, plain black t-shirt, a gold necklace with a small diamond-shaped gray carved stone pendant in a gold frame on the chest.` |
| **Kol. Bagas** | `Colonel (retired) Bagas Suryo, 55 years old, head of a secret Indonesian anomaly agency, broad shoulders, upright posture, warm brown skin, short gray crew-cut hair, gray mustache, strong jaw. Fitted dark olive field jacket closed with a zipper, dark shirt collar. No medals, no insignia.` |
| **Sekar** | `Sekar, a 19-year-old Indonesian hacker and mission operator, petite, light-brown skin, short black bob haircut with straight bangs. A compact wireless headset with a small mic on one ear, oversized dark gray hoodie with the hood down.` |
| **Dr. Nadia** | `Dr. Nadia Prameswari, a 32-year-old Indonesian energy physicist, slim, light-brown skin, shoulder-length black hair in a low ponytail, thin rectangular glasses. Short fitted white lab jacket closed over a dark turtleneck.` |
| **Prof. Yahyo** | `Professor Yahyo Sasmito, a 68-year-old Indonesian historian and philologist, warm brown skin, neat white hair and short white beard, round glasses. Long-sleeve brown batik shirt with a plain dark vest over it.` |
| **Ki Sastro** | `Ki Sastro, a 70-year-old Javanese wayang puppet master (dalang), small and slim, warm brown skin, wrinkled kind face, thin white mustache. Dark batik blangkon headcloth, closed dark beskap jacket with a high collar.` |
| **Mandor** | `An Indonesian construction site foreman in his 40s, stocky, warm brown skin, short black hair, thin mustache. White hard hat, orange high-visibility safety vest with a simple abstract sunrise logo over a dark gray work shirt, walkie-talkie clipped on the vest.` |

Contoh `[EXPRESSION]`: `calm and neutral, mouth closed` · `startled and tense, eyes slightly widened` · `focused and determined` · `exhausted, with small scratches and dust on the face, a gray blanket over the shoulders` · `cheerful, small smile` · `panicked, eyebrows raised` · `skeptical, one eyebrow slightly raised`.

## Ikon Sang Penjaga

Sang Penjaga **tidak pernah tampil** ([17](../../../docs/17-skenario-arc-1.md#sang-penjaga-suara-roh-dwarapala)); cukup ikon suara. Usulan: mata Dwarapala dari batu retak yang berpendar emas samar.

```
A square icon for a mysterious spirit voice in a game dialogue box. A close-up of a single large round bulging eye carved in weathered gray andesite stone, from an ancient Javanese temple guardian statue, thin cracks across the stone, a faint warm antique-gold glow inside the cracks and around the eye. Dark charcoal background with a soft vignette, centered, simple and readable at small size.

No face beyond the eye area, no text, no letters, no frame, no blue light, no red glow.
```

## Setelah gambar jadi

Simpan di `docs/concept-art/2d/potret_<tokoh>_<ekspresi>_v01.png`. Target UE: `T_Potret_<Tokoh>_<Ekspresi>`, dipakai `DT_Dialogue_Ep01`.
