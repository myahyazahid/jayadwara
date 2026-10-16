# Stadion + menara lampu, observatorium, lampu sorot mobil

| | |
|---|---|
| **Episode** | 7 |
| **Fungsi** | **Menara lampu stadion** = objektif boss (dinyalakan supaya Kalong Wewe silau dan jatuh); observatorium = lokasi clue ○; lampu sorot = alat Aksa di set-piece on-rails |
| **Prioritas** | Fase 4 |
| **Ukuran** | Menara lampu ±6 × 6 × 45 m (setinggi Jayadwara; usulan); tribun 1 sisi ±80 × 20 × 15 m; observatorium ±15 × 15 × 14 m; lampu sorot ±0,8 m |
| **Rig** | Tidak. Static mesh; kepala lampu menara dan lampu sorot boleh dipisah supaya bisa diputar |
| **Sumber** | [16 Ep 7](../../../docs/16-panduan-arc-1.md#ep-7--bayang-di-atas-atap--kalong-wewe), [28 Ep 7](../../../docs/28-struktur-level-episode.md#4-rancangan-map-per-episode-arc-1) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- Menara lampu harus **terbaca sebagai objek interaktif** dari kamera raksasa: panel lampu besar, warna rangka kontras. Dua kondisi: mati dan menyala (material).
- Tribun cukup 1 modul sisi yang dirangkai mengelilingi lapangan; lapangan rumput = material.
- Observatorium = bangunan kolonial kecil berkubah (sesuai kit Kota Lama). Bentuk = usulan.
- Lampu sorot dipasang di mobil DWARA ([ep01_mobil_dwara.md](ep01_mobil_dwara.md)), diarahkan Aksa (keputusan D3: tanpa sistem kendaraan bebas).

## Prompt 1: menara lampu stadion

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a tall stadium floodlight tower about 45 meters tall. A tapered square steel lattice mast painted light gray on a concrete footing, an internal ladder cage, and at the top a large rectangular steel frame tilted forward holding a grid of 24 big square floodlight panels in four rows, with a small service platform and railing behind the panels.

Shape: strong tapered silhouette, thick readable lattice beams, very large lamp head.

Important: lights off, no glow, no cables hanging, no text, no birds.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 2: modul tribun stadion

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: one straight section of an old municipal football stadium grandstand in an Indonesian city, about 80 meters long, 20 meters deep and 15 meters tall. Stepped concrete terraces with rows of simple plastic seats in faded blue, a flat cantilevered metal roof over the upper half supported by thick steel columns at the back, a plain gray concrete back wall with a few square openings and two stair entrances.

Shape: simple long stepped mass, repeating seat rows.

Important: no text, no advertising boards, no people, no flags, no lights on.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 3: observatorium kota

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a small colonial era city observatory, about 15 meters square and 14 meters tall. A two-story white plastered building with tall arched windows and green shutters, a cylindrical tower rising from the center of the roof topped by a large silver metal dome with a closed vertical slit, a small front porch with two columns and steps.

Shape: symmetrical, clean cylinder and dome on a box.

Important: no text, no signs, no plants, no people, no lights.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Prompt 4: lampu sorot di atap mobil

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, wide empty space between views, shown large and centered.

Object: a heavy-duty handheld-operated searchlight mounted on a vehicle roof rack, about 80 centimeters tall. A large round black metal lamp housing with a wide glass lens, a thick U-shaped yoke holding it, a rotating base plate with four bolts, and a single thick rear handle to aim it.

Important: light off, no glow, no cables, no text.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/<menara_lampu|tribun|observatorium|lampu_sorot>_v01.png`, potong per view. Target UE: `SM_MenaraLampuStadion`, `SM_TribunStadion`, `SM_Observatorium`, `SM_LampuSorotMobil`.
