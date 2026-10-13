# Audio — sumber SFX & musik (di luar `Content/` Unreal)

Sama seperti `Art/`, folder ini berisi file sumber. Unreal hanya membaca `Content/`; hasil import ada di `/Game/Jayadwara/Audio/`.
Kebutuhan audio Ep 1: [docs/18 bagian E](../docs/18-kebutuhan-episode-1.md#e-audio).

| File / folder | Isi |
|---|---|
| `KANDIDAT.md` | Daftar kandidat per slot (sumber, lisensi, ukuran teknis) — **mulai dari sini** |
| `Kandidat/<NN_slot>/` | WAV 48 kHz 16-bit untuk didengarkan: `k1`–`k3` per slot |
| `kandidat.json` | Data yang sama untuk script |
| `pilihan.json` | Pilihan developer per slot (`k1`/`k2`/`k3`) → dibaca `Tools/ue_import_audio.py` |

## Alur
1. Dengarkan `Kandidat/<slot>/`, isi `pilihan.json`.
2. Import: `python Tools/ue_remote.py Tools/ue_import_audio.py` (editor terbuka).
3. Rangkai Sound Cue (`SC_`) di editor: set Kenney → node *Random*; langkah raksasa → layer boom + debris + pitch turun.
4. Untuk aset final dari Freesound, ganti preview MP3 dengan file asli (login Freesound) — nama slot tetap.

Kandidat diperbarui dengan `python3 Tools/sfx_shortlist.py --kenney <ekstrak pack Kenney> --cache <folder cache>`.

## Lisensi
Hanya sumber yang boleh dipakai komersial tanpa syarat:
- **Kenney** (kenney.nl) — CC0 1.0. Kredit opsional.
- **Freesound** — hanya file berlisensi **CC0 1.0**. Kredit opsional; penulis tetap dicatat di `KANDIDAT.md`.

Jangan memasukkan: CC-BY-NC, BBC Sound Effects (RemArc, non-komersial), rip YouTube/film/tokusatsu, pack "reference only".
Sonniss GDC Bundle (royalty-free, boleh komersial) didownload manual oleh developer — situsnya menolak akses otomatis; catat file yang dipakai di tabel bawah.

### Sumber lain yang dipakai (isi manual)
| Slot | File | Sumber | Lisensi |
|---|---|---|---|
| | | | |
