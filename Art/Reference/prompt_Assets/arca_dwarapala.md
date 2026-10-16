# Arca Dwarapala (kiri & kanan)

| | |
|---|---|
| **Episode** | 1 (adegan 4, 6, 9); arca kanan kembali di Ep 40 |
| **Fungsi** | Prop cerita: arca kiri tempat Aksa terpental lalu pecah saat transformasi; arca kanan diangkut truk Adikara |
| **Prioritas** | **Ep 1, F2** (keputusan K2 masih terbuka) |
| **Ukuran** | Arca ±4 m (posisi berlutut satu kaki) di atas alas ±1 m ([30](../../../docs/30-desain-level-ep01.md#koordinat-greybox-meter-titik-nol--tengah-dasar-galian)) |
| **Rig** | Tidak. Static mesh + versi pecah |
| **Sumber** | [02](../../../docs/02-setting-dunia.md#candi-lawang-sapta--arca-kembar), [06](../../../docs/06-referensi-mitologi.md), [17 adegan 4, 6, 9](../../../docs/17-skenario-arc-1.md#adegan-6--kebangkitan--seq), [18 B1](../../../docs/18-kebutuhan-episode-1.md#b1-model) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- **Satu model untuk kedua arca** (dicerminkan). Dwarapala tradisional berpasangan dan hampir identik; arca kanan cukup mirror + sedikit beda pose gada kalau mau.
- Varian dibuat di Blender dari model utuh, bukan dari prompt terpisah:
  - **Kiri retak** (adegan 4) dan **retak besar** (adegan 6): retak sebagai potongan geometri + decal; versi **hancur** = fracture menjadi pecahan yang berputar saat transformasi.
  - **Kanan dililit tali derek** (adegan 4): tali sebagai curve/tube terpisah + stiker inventaris Adikara (decal).
  - **Kanan berterpal** (adegan 6): kain terpal dari cloth sim di atas model, lalu dibekukan jadi static mesh.
- **Alas** dimodel terpisah (lihat [gerbang_prasasti.md](gerbang_prasasti.md)) karena alas kanan harus tetap ada saat arcanya hilang (adegan 9).
- Kalung Aksa adalah **pecahan arca ini** ([kalung_aksa.md](kalung_aksa.md)); samakan warna dan tekstur batunya.
- Wajah garang tapi **tidak seram berlebihan**: ia pelindung yang ambigu, bukan monster. Hiasan tengkorak tradisional (Singosari) **dihilangkan** supaya aman untuk rating remaja dan konsisten dengan aturan "tanpa gore". Penggambaran tetap menunggu review budayawan ([17 cek budaya](../../../docs/17-skenario-arc-1.md#cek-ip--budaya-ep-1)).
- Gada bersandar ke tanah dan menyatu dengan tangan (padat, tanpa celah tipis).

## Prompt

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: an ancient Javanese Dwarapala temple guardian statue carved from a single block of weathered gray andesite volcanic stone, about 4 meters tall. A stocky muscular giant guardian in a half-kneeling pose: the right knee on the ground and the left foot planted forward. A large round face with big bulging round eyes, a wide flat nose, a broad grim mouth with two short fangs at the corners, thick curly stone hair falling to the shoulders in large carved curls, a simple crown band. Round stone ear ornaments, thick armbands and anklets, a simple carved cloth wrap around the waist ending above the knees. The right hand rests on top of a heavy short club (gada) whose head stands on the ground beside the right knee; the left hand rests on the left knee. The statue sits on a square stone slab that is part of the carving.

Shape: compact solid mass with large readable forms, the club touching both the hand and the ground, no thin protruding parts, no gaps narrower than a hand.

Important: protective and stern rather than horrifying. No skulls, no snakes, no blood, no glowing parts, no cracks, no moss, no paint. Plain stone only.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/arca_dwarapala_v01.png`, potong jadi `arca_dwarapala_front/left/back/top.png`. Target UE: `SM_ArcaDwarapala` (utuh), `SM_ArcaDwarapala_Retak`, versi pecah untuk transformasi, `SM_ArcaDwarapala_Terpal`.
