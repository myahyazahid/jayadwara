# Maps Ep 1 **v02** (greybox diperbesar + area baru) — Instruksi Kerja untuk Hermes

> Dari Claude, untuk Hermes. **File ini read-only bagimu**; progres ditulis di `Hermes/Laporan/YYYY-MM-DD-maps_ep1_v02.md`.
> Ini **lanjutan** dari [`maps_ep1_hermes.md`](maps_ep1_hermes.md) (v01, M0–M7 sudah kamu kerjakan). Semua aturan dan konvensi di sana **tetap berlaku** (bagian 2: koordinat, alas objek, jenis objek, material) kecuali yang diubah di file ini. `AGENTS.md` menang atas keduanya.
> Desain: [`docs/30-desain-level-ep01.md`](../docs/30-desain-level-ep01.md) bagian 2a (v02). Pratinjau tampak atas: `docs/visual/ep01_layout_v02_atas.png`.
> Versi: 16 Okt 2026. **Jalur paralel Level/Map** (keputusan developer 16 Okt 2026).

---

## 0. Kenapa v02

Developer mencoba v01 sebagai Jayadwara (45 m) dan map terasa **terlalu kecil**. v02:
- **Jarak antarzona ±1,7×**, tapi **ukuran objek tetap ukuran asli** (rumah tetap 10 × 8 × 6 m, undakan tetap 2,5 m, tangga tetap 25 m). Jangan menskalakan objek.
- **Area baru:** desa sebagai **titik mulai Aksa**, **base camp Adikara**, **area pilar tol**, **hutan + reruntuhan candi perwara**.
- **Pembanding skala:** 775 pohon dan 30 tiang listrik (instanced), siluet bukit dan kota di horizon.

| | v01 | v02 |
|---|---|---|
| Medan | 800 × 700 m | **1400 × 1220 m** |
| Arena | ±530 × 550 m | **1190 × 1025 m** |
| Plato candi | ±120 m | **200 m** |
| Galian | 140 × 120 m | **220 × 190 m** |
| Galian → desa | ≥150 m | **≥255 m** |
| Rute Aksa START → ★3 | ±290 m (±1 mnt) | **±735 m (±2,4 mnt)** |
| START | garis polisi di bukit | **desa** (mobil DWARA lewat jalan desa) |

### Sumber data (read-only, jangan disunting)
| File | Isi |
|---|---|
| `Art/Level/ep01_medan_v02.py` | `elev(x, y)` dan **`zona_material(x, y)`** (slot medan), konstanta area. Uji: `python -I Art/Level/ep01_medan_v02.py` → `SEMUA LULUS` |
| `Art/Level/ep01_layout_v02.json` | 88 objek, 775 pohon (6 kelompok), 30 tiang, 13 penanda, 4 zona, batas arena, 8 kamera, cahaya, `rute_aksa`. **Dibuat** oleh `Art/Level/buat_layout_ep01_v02.py` |
| `docs/visual/ep01_layout_v02_atas.png` | Pratinjau tampak atas (acuan untuk mencocokkan render C5 dan M2_atas) |

Ada yang salah di data? **Jangan ubah file di `Art/Level/`.** Tulis di laporan ("Usulan perubahan di luar sandbox") dengan angka + gambar. Claude yang memperbaiki lewat generator.

### Yang tidak berubah
v01 (level `Test_Hermes_MapsEp1`, aset, render) **dibiarkan** sebagai pembanding. v02 dibuat di sampingnya.

---

## 1. Git & lokasi

Worktree sama: `C:\repository\unreal_engine\jayadwara_hermes_maps_ep1`. Branch **baru** dari branch v01 milikmu (skrip v01 ada di sana), lalu ambil data v02 dari `development`:

```
cd C:\repository\unreal_engine\jayadwara_hermes_maps_ep1
git status                                  # harus bersih; v01 sudah di-commit & di-push
git fetch origin
git switch -c hermes/maps_ep1_v02 hermes/maps_ep1
git merge origin/development                # boleh: menggabungkan ke branch MILIKMU sendiri
git lfs pull
python -I Art/Level/ep01_medan_v02.py       # SEMUA LULUS
python -I Art/Level/buat_layout_ep01_v02.py # SEMUA LULUS (menulis ulang JSON yang sama; git status harus tetap bersih)
```
Merge konflik → **berhenti dan lapor** (jangan pilih sisi sendiri). `git status` tidak bersih setelah menjalankan generator → lapor (berarti data di repo beda dengan generator).

| Apa | Path v02 |
|---|---|
| Level | `/Game/Hermes/MapsEp1/Maps/Test_Hermes_MapsEp1_v02` |
| Mesh | `/Game/Hermes/MapsEp1/Meshes/SM_Ep01_Medan_v02`, `SM_Ep01_Tangga_v02` |
| Material | **pakai ulang** `M_Hermes_Greybox` + 15 `MI_Ep01_*` v01 |
| Skrip | salin skrip v01 → `Hermes/Tools/maps_ep1_v02_<NN>_<nama>.py` (skrip v01 jangan diubah) |
| Blender / render | `Hermes/Art/maps_ep1/v02/` (`Export/`, `Render/`) |
| Commit | `[hermes] maps_ep1_v02 V<n> <ringkas>` |

---

## 2. Perubahan konvensi v02

1. **Modul medan:** impor `ep01_medan_v02` (JSON `"medan_modul"`). Jangan impor `ep01_medan` (v01).
2. **Slot material medan:** panggil `zona_material(x, y)` dari modul (tidak lagi aturan teks di JSON). Slot: `Air`, `Galian`, `Jalan`, `Plato`, `Sawah`, `Desa`, `Hutan`.
3. **`"z"` di objek = tinggi alas absolut** (dipakai gelagar tol `z: 40` dan latar jauh `z: 0`). Tanpa `"z"`: alas otomatis seperti v01.
4. **Jenis baru `kerucut`:** `/Engine/BasicShapes/Cone` diskala `[diameter, diameter, tinggi]`, alas di `z`. Dipakai `LATAR_Bukit*` (di luar medan, tidak bisa didatangi).
5. **Tag baru:** objek dengan `"milik": "Adikara"` diberi tag **`adikara`** (selain `hancur`). Artinya hancur **tanpa penalti** meter. Objek `hancur` tanpa `milik` = penalti (desa).
6. **`"tanpa_tabrakan": true`** → collision NoCollision (garis polisi, latar jauh).
7. **Pohon** (`pohon_kelompok`, 6 kelompok): satu actor per kelompok, label `POHON_<Kelompok>`, folder `POHON`, berisi **dua InstancedStaticMeshComponent**:
   - `Batang`: `/Engine/BasicShapes/Cylinder`, diameter 0,6 m × tinggi 8 m, `MI_Ep01_Kayu`, collision **BlockAll**
   - `Tajuk`: `/Engine/BasicShapes/Cone`, diameter 7 m × tinggi 9 m, alas 6 m di atas tanah, `MI_Ep01_Hutan`, **NoCollision**
   - Tiap titik `[x, y, s]`: ukuran dikali `s`, alas = `elev(x, y)`.
8. **Tiang listrik** (`tiang_listrik.titik`): satu actor `TIANG_Listrik` dengan satu ISM silinder Ø0,3 m × 9 m, `MI_Ep01_Kendaraan`, BlockAll.
9. **Cahaya `sore` v02** lebih tinggi dan netral (pitch −25°) supaya warna zona terbaca. Uji main pakai `sore`.

---

## 3. Langkah V0–V7

Sama dengan M0–M7 v01. Yang ditulis di bawah hanya bedanya dan **angka lulus v02**. Satu langkah → cek → laporan → commit.

### V0 — Persiapan
Bagian 1 di atas. **Lulus:** kedua perintah uji mencetak `SEMUA LULUS`, generator mencetak `objek 88 (hancur 30, milik Adikara 20), pohon 775, tiang 30, penanda 13, zona 4, kamera 8` dan `rute Aksa START -> ★3: 735 m`. Tempel keluarannya.

### V1 — Cek layout
Skrip cek v01 disesuaikan ke v02. **Lulus:** 88 objek, 13 penanda, 4 zona, 8 kamera, 775 pohon, 30 tiang; `DESA_*` alas 0,0 m; `CANDI_*` (kecuali tangga) alas 35,0 m; `BASECAMP_*` alas 25,0 m. Temuan selisih tanah > 2 m dicatat (diketahui: `TOL_Pilar7` ±2,8 m, boleh).

### V2 — Medan + tangga (Blender headless)
- Grid `x` −620…780, `y` −580…640, sel **2,5 m** → **561 × 489 = 274.329 vertex**.
- Slot per muka dari `zona_material` di titik tengah muka.
- Tangga dari objek `CANDI_Tangga` v02: (0; 142; 28) → (0; 167; 35), lebar 10, 28 anak tangga.
- Render `Render/V2_atas.png` (ortografis, utara di atas) dan `Render/V2_miring.png`.
- **Lulus:** jumlah vertex 274.329; **14 titik uji** (`TITIK_UJI` di modul v02) mesh = `elev` ± 0,05 m; `V2_atas.png` cocok dengan `docs/visual/ep01_layout_v02_atas.png`: posisi galian, mulut ke selatan, plato, base camp, sawah, desa barat daya, kali, jalan akses dan jalan desa. Uraikan per bagian.

### V3 — Level UE v02
- Level baru dari template → `Test_Hermes_MapsEp1_v02`. Impor medan + tangga v02, **Use Complex as Simple**, pasang MI v01 per slot. GameMode Override `BP_JDGameMode`.
- DirectionalLight = setelan `sore` v02.
- **Lulus:** bounds medan ±140.000 × 122.000 cm; line trace 14 titik uji = `elev × 100` ± 5 cm; cek sandbox LULUS.

### V4 — Objek, pohon, tiang
- 88 objek (jenis baru `kerucut`, `z` absolut, tag `adikara`), 6 actor pohon, 1 actor tiang.
- **Lulus:**
  - 88 objek ada; alas actor = alas hitungan ± 5 cm (kecuali `z` absolut: = `z` ± 5 cm)
  - tag `hancur` = **30**, di antaranya `adikara` = **20** dan `cadangan` = 2
  - `DESA_Musala`, `CANDI_*`, `DESA_RumahLatar*` tanpa `hancur`
  - jumlah instance pohon total **775** (batang dan tajuk sama), tiang **30**
- Screenshot: desa dari START, base camp dari jalan akses, area pilar tol, hutan perwara.

### V5 — Penanda, zona, batas
- 13 penanda: PlayerStart di **desa** menghadap gerbang; `LORE_*` diberi teks warna biru (opsional/usulan).
- 4 zona TriggerBox. Batas arena tinggi **120 m** (x −470…720, y −525…500) + 4 dinding tepi medan.
- **Lulus:** 1 PlayerStart, 8 titik, 4 area, 4 zona, 8 dinding; PlayerStart di Z = `elev(−160, −425) × 100` + setengah kapsul ± 10 cm.

### V6 — Kamera C1–C8
8 kamera dari JSON (2 baru: `C7_BaseCamp`, `C8_PilarTolRaksasa`) → `Render/<id>_<cahaya>.png` 1920 × 1080.

| Kamera | Harus terlihat |
|---|---|
| C1 START desa | Rumah desa di dekat kamera; bukit, galian dan gerbang candi jauh di atas sebagai tujuan |
| C2 Bibir galian barat | Undakan lebar turun ke dasar galian; ram barat |
| C3 Gerbang ke timur | Jalan proyek turun ke base camp; truk derek di dekat gerbang |
| C4 Mata Jayadwara | Galian, sawah luas, desa jauh di kiri bawah; pohon sebagai pembanding |
| C5 Tampak atas | Sama dengan `ep01_layout_v02_atas.png` |
| C6 Dari sawah | Bukit, galian, candi; siluet senja |
| C7 Base camp | Kontainer, gudang, truk; galian di belakang |
| C8 Pilar tol (45 m) | Deretan pilar 40 m dan 2 gelagar; bukit candi di kejauhan |

### V7 — Rute, perbandingan, daftar uji
- Panjang rute dari `rute_aksa` (JSON) di permukaan medan: target **±735 m**, waktu pada 500 cm/s. Cetak per ruas.
- **Lembar perbandingan v01 vs v02:** C4 v01 dan C4 v02 berdampingan (`Render/banding_C4_v01_v02.png`).
- Daftar uji developer (jangan diisi sendiri):
  1. Play di `Test_Hermes_MapsEp1_v02`: muncul di desa; jalan setapak ke galian terbaca?
  2. Rute ke ★1 → ★2 → ★3: catat waktu; terasa terlalu panjang atau pas?
  3. Transformasi di halaman candi (**T**): arena sekarang terasa cukup luas sebagai Jayadwara? Desa terasa jauh? Pohon membantu rasa skala?
  4. Coba bertarung di base camp dan area pilar tol: ruangnya enak?
  5. Bandingkan dengan v01: mana yang lebih baik, apa yang masih kurang.
- Cek sandbox LULUS → push `hermes/maps_ep1_v02`. **Jangan merge.**

---

## 4. Bukti wajib di laporan

| Langkah | Bukti |
|---|---|
| V0 | Keluaran 3 perintah uji |
| V1 | Tabel 88 objek + jumlah pohon/tiang |
| V2 | 274.329 vertex, tabel 14 titik, `V2_atas.png`, `V2_miring.png` + uraian |
| V3 | Bounds, tabel line trace 14 titik, cek sandbox |
| V4 | Tabel alas, jumlah tag (30 / 20 / 2), jumlah instance, 4 screenshot |
| V5 | Jumlah actor per jenis, tinggi PlayerStart, screenshot tampak atas |
| V6 | 8 PNG + tabel cocok/tidak |
| V7 | Rute per ruas, `banding_C4_v01_v02.png`, daftar uji kosong, cek sandbox |
