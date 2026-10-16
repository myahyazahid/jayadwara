# Scanner Netra

| | |
|---|---|
| **Episode** | 1 (adegan 2 diperkenalkan, adegan 4 tutorial scan); semua episode investigasi |
| **Fungsi** | Alat investigasi ciptaan Dr. Nadia: scan jejak energi Kala, tulang, prasasti |
| **Prioritas** | **Ep 1, F2** |
| **Ukuran** | ±20 × 9 × 4 cm (usulan) |
| **Rig** | Tidak. Static mesh dipegang di socket tangan Aksa saat pose scan |
| **Sumber** | [03](../../../docs/03-karakter.md), [07](../../../docs/07-gameplay-sistem.md), [17 adegan 2, 4](../../../docs/17-skenario-arc-1.md#adegan-4--tiga-petunjuk--main--koms) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- Penampilan = usulan Claude; docs baru mengunci fungsi. "Prototipe, jangan dijatuhin" (Nadia) → alat genggam yang kelihatan buatan tangan dan rapuh, bukan produk komersial.
- **Dipegang tangan, bukan di lengan.** Alat di lengan dilarang karena terlalu mirip Mebius Brace ([01](../../../docs/01-konsep-dan-pilar.md#wajib-dihindari), [03](../../../docs/03-karakter.md#aksa-jaya-mangkubumi-aksa)).
- Layar dan lensa menyala saat scan = material emissive; gambar **tanpa cahaya**. Warna glow nanti jangan biru (aturan konten).

## Prompt

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, wide empty space between views, shown large and centered.

Object: a handheld prototype scanning device about 20 centimeters long, shaped like a rugged compact tablet with two thick rubber-gripped handles on the sides. Dark gray matte casing with exposed screws and a slightly handmade engineering look, a small rectangular screen on the back face facing the user, a single large round camera lens with a metal ring on the front face, a short stubby antenna at the top corner, a small cluster of three tiny sensor lenses beside the main lens, one strip of yellow-black hazard tape on one handle.

Important: screen off and blank, no glow, no brand, no wrist strap, nothing attached to the arm.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/netra_v01.png`, potong per view. Target UE: `SM_Netra`.
