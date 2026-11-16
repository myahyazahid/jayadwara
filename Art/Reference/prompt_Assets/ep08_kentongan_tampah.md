# Kentongan + tampah (dibawa warga)

| | |
|---|---|
| **Episode** | 8 |
| **Fungsi** | Warga menabuh kentongan dan tampah untuk memanggil anak-anak pulang; memicu fase 2 Wewe Gombel |
| **Prioritas** | Fase 4 |
| **Ukuran** | Kentongan genggam ±40 cm; tampah ±50 cm diameter |
| **Rig** | Tidak. Static mesh di socket tangan warga |
| **Sumber** | [16 Ep 8](../../../docs/16-panduan-arc-1.md#ep-8--kentongan-tengah-malam--wewe-gombel), [28 Ep 8](../../../docs/28-struktur-level-episode.md#4-rancangan-map-per-episode-arc-1) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- Kentongan besar di gardu ronda sudah ada di [ep01_gardu_ronda.md](ep01_gardu_ronda.md); ini versi **genggam** yang dibagikan ke warga.
- Pemukul kentongan dibuat sebagai mesh terpisah (tongkat kayu pendek).
- Desa lereng dan terasering = kit Ep 1 + Ep 6 (tanpa prompt baru).

## Prompt

```
Orthographic model reference sheet for a realistic 3D action game, a set of three separate handheld objects, each shown in FRONT, SIDE and TOP orthographic views, arranged in three rows with wide empty space between them, same scale.

Objects: (1) a small handheld bamboo slit drum (kentongan) about 40 centimeters long, a thick section of yellowed bamboo with a long narrow slit cut along one side and a short handle loop of thick rope at the top; (2) a short wooden drumstick about 25 centimeters long; (3) a round flat woven bamboo winnowing tray (tampah) about 50 centimeters in diameter with a thick bamboo rim.

Important: no text, no hands holding them, no decorations.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/kentongan_tampah_v01.png`, potong per view. Target UE: `SM_KentonganGenggam`, `SM_PemukulKentongan`, `SM_Tampah`.
