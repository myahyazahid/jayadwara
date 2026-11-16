# Truk derek Adikara

| | |
|---|---|
| **Episode** | 1 (adegan 3, 6); dipakai ulang di Arc 2 |
| **Fungsi** | Parkir di ujung plato (adegan 3–4); di wide shot adegan 6 melaju pergi lewat jalan proyek membawa arca kanan berterpal |
| **Prioritas** | **Ep 1, F2** |
| **Ukuran** | ±10 × 2,5 × 3,5 m (usulan, truk bak + crane lipat kelas menengah) |
| **Rig** | Tidak. Static mesh; roda dipisah kalau mau berputar di Sequencer |
| **Sumber** | [17 adegan 6](../../../docs/17-skenario-arc-1.md#adegan-6--kebangkitan--seq), [18 B1](../../../docs/18-kebutuhan-episode-1.md#b1-model), [30](../../../docs/30-desain-level-ep01.md) |

Aturan umum dan cara potong: [README](README.md).

## Catatan

- Jenis truk = usulan Claude: truk bak datar dengan **crane lipat di belakang kabin**, cukup kuat mengangkat arca ±4 m. Bak kosong di gambar; arca berterpal dipasang di level/Sequencer.
- Warna perusahaan Adikara = usulan: putih dengan aksen oranye, logo matahari terbit abstrak di pintu (sama dengan rompi [mandor](../prompt_karakter/mandor.md)). **Tanpa merek truk nyata** (gril, emblem).
- Lengan crane dalam posisi terlipat supaya siluetnya ringkas; versi terbuka (mengangkat) bisa dibuat dengan memutar potongan crane di Blender.
- Pisahkan: kabin, bak, crane (2–3 segmen), roda ×6. Kaca kabin gelap (tidak tembus).

## Prompt

```
Orthographic model reference sheet for a realistic 3D action game, four views arranged in a grid: FRONT view, SIDE view (left side), BACK view, TOP view. Same object, same scale, all views aligned on one ground line, wide empty space between views.

Object: a medium heavy-duty flatbed truck with a folding knuckle-boom crane, about 10 meters long, used by a big Indonesian mining and infrastructure company. White cab-over-engine cab with orange stripes along the sides, dark tinted windows, a simple bold abstract sunrise logo on each door. Behind the cab, a sturdy orange hydraulic knuckle-boom crane folded compactly. A long empty steel flatbed with low side rails, six large black wheels with dusty mud splashes on the lower body, side mirrors, a front bumper with plain rectangular headlights.

Important: no real truck brand, no badges, no license plate text, no driver, nothing loaded on the flatbed.

Plain flat light-gray background, flat even unlit lighting, no cast shadows, no ambient occlusion, no text, no labels, no logos other than the door emblem. True orthographic projection with no perspective distortion. Realistic materials, simple bold shapes, no fine detail, consistent across all views, suitable as a modeling reference for a 3D artist.
```

## Setelah gambar jadi

Simpan sheet di `docs/concept-art/truk_derek_v01.png`, potong per view. Target UE: `SM_TrukDerek` (+ `SM_TrukDerek_Roda`).
