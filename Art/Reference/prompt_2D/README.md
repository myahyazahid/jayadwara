# Prompt gambar 2D (Ep 1)

Prompt siap salin untuk **gambar konsep 2D** Ep 1: pembuka wayang, potret dialog, stinger, dan kartu judul/episode. Pasangan untuk aset 3D: [`../prompt_Assets/`](../prompt_Assets/README.md) dan [`../prompt_karakter/`](../prompt_karakter/README.md).

> **Status: usulan (16 Okt 2026), untuk eksplorasi konsep.** Isi adegan dari [docs/17](../../../docs/17-skenario-arc-1.md#episode-1--gerbang-yang-retak); bentuk UI (DIALOG vs KOMS) dari [docs/17 Alur Adegan](../../../docs/17-skenario-arc-1.md#alur-adegan) dan [docs/12](../../../docs/12-technical-design.md) (dialog = teks + potret). **Gaya wayang dan siapa pembuatnya (K3, [docs/18](../../../docs/18-kebutuhan-episode-1.md#6-keputusan-yang-perlu-diambil)) belum diputuskan**; hasil generate di sini untuk membantu memutuskan, bukan aset final. Kalau K3 = commission, gambar ini jadi brief untuk ilustrator.

## Daftar

| File | Isi | Adegan |
|---|---|---|
| [`ep01_wayang_pembuka.md`](ep01_wayang_pembuka.md) | Kelir + blencong, wayang Dwarapala, makhluk Kala, gunungan (2 gaya untuk dibandingkan) | 1 |
| [`ep01_potret_dialog.md`](ep01_potret_dialog.md) | Potret Aksa, Bagas, Sekar, Nadia, Yahyo, Ki Sastro, mandor + ikon Sang Penjaga | 2–9 |
| [`ep01_stinger_gunadi.md`](ep01_stinger_gunadi.md) | Gambar diam Gunadi + arca kanan di gudang | 10 |
| [`ep01_kartu.md`](ep01_kartu.md) | Latar kartu judul JAYADWARA + 3 potongan "Episode berikutnya" | 6, 11 |

## Aturan umum

1. **Rasio:** layar penuh 16:9 (1920×1080 atau lebih). Potret 1:1 atau 3:4.
2. **Tanpa teks di gambar.** AI tidak bisa menulis huruf dengan benar; judul, nama, dan subtitle ditambahkan di UI (UMG) atau aplikasi grafis.
3. **Wayang untuk parallax = satu objek per gambar** di latar polos supaya mudah dipotong jadi layer PNG transparan. Satu gambar komposisi utuh boleh dibuat untuk acuan mood.
4. **Potret = satu gaya untuk semua tokoh.** Generate Aksa dulu, lalu pakai sebagai referensi gaya (image reference/style reference) untuk tokoh lain.
5. Aturan IP dan konten tetap berlaku ([docs/01](../../../docs/01-konsep-dan-pilar.md#wajib-dihindari), [docs/16 2.7](../../../docs/16-panduan-arc-1.md#27-aturan-konten)): Jayadwara tanpa gelang/alat di lengan, tangan tidak diangkat di atas bahu; energi Kala **merah gelap**, tanpa biru, tanpa gore.
6. Penampilan tokoh mengikuti prompt karakter yang sudah ada di [`prompt_karakter/`](../prompt_karakter/README.md), supaya potret cocok dengan model 3D nanti.

## Setelah gambar jadi

Simpan di `docs/concept-art/2d/<file>_v01.png`. Pilihan gaya wayang dan keputusan K3 dicatat di [docs/18](../../../docs/18-kebutuhan-episode-1.md#6-keputusan-yang-perlu-diambil).
