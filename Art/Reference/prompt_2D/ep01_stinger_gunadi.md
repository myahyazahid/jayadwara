# Stinger Ep 1: arca kedua

| | |
|---|---|
| **Adegan** | 10 · gambar diam · ±30 detik (opsional) |
| **Isi** | Gudang gelap Adikara; terpal ditarik dari arca Dwarapala kanan; Gunadi menatapnya, lalu menatap tablet berisi rekaman Jayadwara |
| **Dialog** | *"Satu sudah bangun."* · *"Yang ini... punya kita."* (teks di UI, bukan di gambar) |
| **Keputusan** | S4: cukup **gambar diam**, tanpa model Gunadi atau set gudang 3D ([17](../../../docs/17-skenario-arc-1.md#adegan-10--stinger-arca-kedua--gambar-diam)) |

Aturan umum: [README](README.md).

## Catatan

- Satu ilustrasi 16:9. Kalau mau sedikit hidup, buat **2 gambar** (Prompt 1 lalu Prompt 2) dan beri gerakan kamera pelan (pan/zoom) di UE.
- Arca harus **sama** dengan arca Dwarapala di [`ep01_arca_dwarapala.md`](../prompt_Assets/ep01_arca_dwarapala.md) (pose berlutut, gada, batu andesit abu-abu) dan **masih dililit tali derek**, supaya pemain langsung mengenalinya.
- Wajah Gunadi = [`gunadi.md`](../prompt_karakter/gunadi.md). Dibuat setengah gelap: tokoh ini antagonis bayangan, belum perlu wajah yang terlalu jelas.
- Rekaman di tablet: siluet Jayadwara (merah, hitam, emas) di senja merah, buram seperti rekaman drone.

## Prompt 1: terpal dibuka

```
Cinematic still for a realistic Indonesian action game, wide 16:9 frame, low camera angle. Inside a dark cavernous industrial warehouse at night, a single shaft of cold white light from a half-open loading door on the left. In the center, a 4-meter ancient gray andesite temple guardian statue (Dwarapala) kneeling on one knee and holding a heavy club, still wrapped with thick yellow tow straps, a large dusty canvas tarpaulin being pulled off it and falling to the floor. Standing in front of the statue, seen from behind at three-quarter, a tall man in his late 50s in a tailored charcoal suit with slicked-back gray-black hair, looking up at the statue. Wooden shipping crates and steel shelves fade into darkness around them, dust floating in the light.

Moody, quiet and ominous. Realistic digital painting with photographic lighting. No text, no letters, no logos, no blue glow, no blood.
```

## Prompt 2: tablet

```
Cinematic close-up still for a realistic Indonesian action game, 16:9 frame. In a dark warehouse, the side of a calm confident Indonesian businessman in his late 50s, slicked-back gray-black hair, charcoal suit, a small gold sunrise-shaped lapel pin, his face half in shadow and lit only by the glow of a tablet he holds. On the tablet screen, blurry drone footage of a giant armored red, black and gold warrior standing in a hill village under a blood-red dusk sky. Behind him, out of focus, the stone face of an ancient temple guardian statue with yellow straps.

Moody, ominous, a faint satisfied smile. Realistic digital painting with photographic lighting. No readable text on the screen, no letters, no logos, no blue glow.
```

## Setelah gambar jadi

Simpan di `docs/concept-art/2d/stinger_ep01_<1|2>_v01.png`. Target UE: `T_Stinger_Ep01_01/02`, diputar oleh `LS_Ep01_Stinger` atau widget gambar.
