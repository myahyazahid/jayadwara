# Mobil DWARA

| | |
|---|---|
| **Episode** | 1 (adegan 2 briefing di kabin, adegan 3 titik mulai); dipakai ulang di episode lain |
| **Fungsi** | Kendaraan lapangan DWARA; diparkir di garis polisi ([30](../../../docs/30-desain-level-ep01.md#koordinat-greybox-meter-titik-nol--tengah-dasar-galian)) |
| **Prioritas** | **Ep 1, F2** |
| **Ukuran** | ±5 × 1,9 × 1,9 m (usulan, SUV besar) |
| **Rig** | Tidak. Static mesh |
| **Sumber** | [17 adegan 2–3](../../../docs/17-skenario-arc-1.md#adegan-2--briefing-di-jalan--dialog), [30](../../../docs/30-desain-level-ep01.md) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- Penampilan = usulan Claude. DWARA badan rahasia, jadi mobilnya **polos tanpa tanda**: SUV abu-abu gelap yang terlihat seperti mobil dinas biasa.
- Adegan 2 berupa DIALOG (potret di UI), jadi **interior tidak perlu dimodel**; kaca gelap.
- **Tanpa merek nyata.** Bentuk generik, gril sederhana.

## Prompt

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: an unmarked government field vehicle, a large boxy four-door SUV about 5 meters long, dark charcoal gray paint, dark tinted windows all around, black steel roof rack with no cargo, black plastic wheel arches, simple rugged off-road tires with dust on the lower body, a plain black front grille with no emblem, a black steel front bumper, a spare wheel mounted on the rear door. A small discreet antenna on the roof.

Important: no real car brand, no badges, no license plate text, no police markings, no lights bar, no people inside.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/mobil_dwara_v01.png`, potong per view. Target UE: `SM_MobilDwara`.
