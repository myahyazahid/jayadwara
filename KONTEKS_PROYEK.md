# Konteks Proyek JAYADWARA (untuk Claude di akun/sesi lain)

> Ringkasan per **16 Oktober 2026**. Tempel file ini di awal percakapan (atau masukkan ke Project Knowledge) supaya Claude langsung paham proyek, cara kerja, dan keputusan yang sudah dikunci.
> **Sumber kebenaran tetap folder `docs/` di repo.** Kalau file ini bertentangan dengan `docs/`, yang berlaku `docs/`. Mulai dari `docs/README.md`.

---

## 1. Proyek singkat

| | |
|---|---|
| Judul | **JAYADWARA: Guardian of the Seven Gates** |
| Genre | Action-adventure episodik, *kyodai hero* (manusia berubah jadi raksasa lawan monster), linear semi-open-world |
| Inspirasi | Struktur serial **Ultraman Mebius**, tapi **tanpa IP Tsuburaya** (lihat §3) |
| Dunia | Mitologi **Nusantara**, kota fiksi **Arunapura** (Jawa) |
| Engine | **Unreal Engine 5.6.1**, C++ + Blueprint |
| Platform | PC (Steam). Keyboard-mouse utama, gamepad PS/Xbox/generik wajib bisa |
| Gaya visual | **Realistis** (game-realistis, PBR, Lumen + Nanite), diputuskan 14 Okt 2026, menggantikan stylized |
| Tim | **Solo developer** (Muhammad Yahya Zahid) + Claude, sambilan ±10–15 jam/minggu |
| Struktur | **50 episode, 5 arc**; rilis per season. Season 1 = Arc 1 (Ep 1–10) sebagai Early Access |
| Bahasa | Audio/teks Indonesia + subtitle Inggris |
| Repo | `C:\repository\unreal_engine\jayadwara` (GitHub `myahyazahid/jayadwara`), Git + Git LFS |

**Logline:** Aksa Jaya Mangkubumi, agen baru lembaga rahasia DWARA, menyatu dengan roh **Dwarapala** (penjaga gerbang kuno yang dulu dianggap monster). Saat segel Tujuh Gerbang Nusantara retak dan makhluk mitologi bangkit sebagai raksasa, Aksa harus melindungi kota sambil menjaga agar kegelapan Kala di dalam dirinya tidak ikut bangun.

---

## 2. Cara kerja dengan developer (WAJIB diikuti)

- **Bahasa:** Indonesia santai (boleh "bro", "aku/kamu").
- **Pembagian kerja:** logic inti di **C++** (Claude). Blueprint/editor untuk merangkai, tuning, visual (developer). Claude **tidak bisa membaca/mengedit `.uasset`/`.umap`**, jadi aset UE dibuat/diubah lewat **skrip Python editor di `Tools/`** (dijalankan via `python Tools/ue_remote.py <file.py>` di editor yang terbuka). Developer lebih suka Claude yang mengerjakan langkah editor lewat skrip daripada memberi instruksi klik-klik.
- **Scope:** kerjakan hanya yang masuk fase aktif (`docs/10-roadmap.md`, `docs/11-vertical-slice-spec.md`, `docs/23-rencana-fase-1.md`). Ide di luar scope → catat ke backlog, jangan dikerjakan.
- **Keputusan desain berubah → perbarui dokumen `docs/` yang relevan.** Keputusan yang butuh pilihan developer ditulis sebagai daftar bernomor (mis. Q1–Q18, R1–R10, E1–E7) lalu ditanyakan.
- **Git:**
  - Claude **tidak commit, push, merge, atau membuat PR** kecuali developer minta eksplisit untuk tugas itu. Jangan juga menawarkan "mau aku commit?". Cukup selesaikan perubahan di working tree dan laporkan file apa saja yang berubah.
  - Kalau diminta: kerja di branch `claude/<topik>` dari `development`, PR ke `development`. **Tidak pernah push langsung ke `development`/`main`.** Author commit `Muhammad Yahya Zahid <myahyazahid11@gmail.com>`; pesan commit & PR **hanya isi perubahan**, tanpa baris atribusi Claude.
  - Jangan commit `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`.
- **Model/aset lama jangan dihapus atau ditimpa.** Versi baru selalu dibuat paralel dengan nama baru (pola `Jayadwara` → `Jayadwara2`, `Aksa` → `Aksa2`), dan pergantian model aktif harus bisa dibalik (mis. `ACTIVE_GIANT` di `Tools/ue_setup_transform.py`, `ACTIVE_AKSA` di `Tools/ue_setup_aksa2.py`).
- **Bukti, bukan klaim:** setiap hasil model/rig dinilai dengan angka (validator, IoU, tris, jumlah tulang, cm regangan) + render/screenshot, dibandingkan berdampingan dengan konsep dan model lama.

---

## 3. Batas IP & budaya (dicek di setiap aset/episode)

**Wajib dihindari (IP Tsuburaya / Ultraman, juga Bima Satria Garuda):**
- Tubuh merah-perak, lampu/timer di dada, **permata dada yang berkedip/berubah** (permata Jayadwara **statis**)
- Asal-usul alien / "negeri cahaya"
- Alat transformasi berupa **gelang/gauntlet** (mirip Mebius Brace) → di game diganti **kalung pecahan arca**
- Pose/nama jurus mirip Specium Ray, pose L
- **Batas waktu transformasi 3 menit** → diganti meter sinkronisasi
- Kristal dahi, bilah kembar di kepala, mata lensa besar, emblem garuda; nama tim/kaiju mirip aslinya
- Faceplate putih Jayadwara adalah titik paling dekat ke Ultra: bentuk mulut/pipi harus beda

**Budaya:** ikuti panduan sensitivitas di `docs/06`. Legenda di pembuka wayang = versi rakyat; adaptasi game disebut efek energi Kala. Rating target remaja: seram boleh, gore tidak. Rumah adat/tempat ibadah tidak boleh hancur.

---

## 4. Cerita & dunia (ringkas)

- **Sapta Dwara:** tujuh gerbang segel di Nusantara (Gerbang Induk = **Candi Lawang Sapta**, Arunapura; lalu Sumatra, Kalimantan, Sulawesi, Nusa Tenggara, Maluku–Papua, Bali).
- **Energi Kala** bocor dari segel retak; makhluk gaib yang menyerapnya **membesar jadi raksasa**. Sumbernya **Batara Kala** (final boss). Adikara Group ingin memanennya lewat **Proyek Fajar**.
- **Dwarapala** menyegel monster dengan **memakannya**, jadi sifat Kala ikut tersimpan → tema "apa benar dia pahlawan?". Dibongkar di Ep 30. Di Arc 1 hanya foreshadowing lewat mata/aura (bukan permata dada).
- Gerbang candi dijaga **dua arca**: arca pertama hancur di Ep 1 dan menyatu dengan Aksa → **Jayadwara**; arca kedua diangkut truk Adikara (payoff Ep 40, Dwarapala Kembar).

**Tokoh:**
- **Aksa Jaya Mangkubumi** (25), codename **Lawang**, mantan atlet silat nasional, agen baru DWARA. Silat keluarganya = jurus Dwarapala versi manusia (alasan satu sistem combat untuk dua skala). Gestur transformasi **"Lawang Terbuka"**: kalung digenggam di dada, lengan dibuka seperti pintu gerbang, gerbang paduraksa cahaya di belakangnya. Merahasiakan dirinya "Entitas D".
- **Ki Zahid** (kakek, inang Dwarapala sebelumnya, hilang 10 tahun), **Dimas** (sepupu, rival, inang Dwarapala Kembar).
- **DWARA** (Divisi Warisan dan Riset Anomali), markas bunker di bawah Museum Arunapura: Kol. (Purn.) **Bagas Suryo** (kepala), Dr. **Nadia Prameswari** (fisikawan, pencipta scanner **Netra** & meter sinkronisasi), Prof. **Yahyo Sasmito** (filolog), **Ratna Dewantari** (DPR), **Ki Sastro** (dalang, pembuka wayang tiap episode), **Bayu Saputra** (rekan lapangan), **Sekar** (operator/peretas).
- Antagonis: **Gunadi Adikara** (CEO Adikara Group), Dimas, Batara Kala.
- Easter egg: Ki Zahid & Prof. Yahyo dari nama creator.

**Arc:** 1 Kebangkitan (Ep 1–10) · 2 Gelombang Nusantara (11–20) · 3 Bangsa Buto (21–30) · 4 Penguasa Wilayah (31–40) · 5 Gerhana (41–50).

**Arc 1 (arc tutorial, tiap episode = satu mekanik baru):**

| Ep | Judul | Boss (ukuran × Jayadwara) | Lokasi | Mekanik baru |
|---|---|---|---|---|
| 1 | Gerbang yang Retak | Jerangkong (0,7×) | Situs Lawang Sapta | Semua dasar |
| 2 | Tangan-Tangan Kecil | Tuyul (1,0×; fase 2 0,6× ×3) | Kampung Kali | Kejar-kejaran + kawanan |
| 3 | Lapar Listrik | Jenglot | Distrik Adikara | Objektif lingkungan saat boss |
| 4 | Lilin di Pasar Malam | Babi Ngepet | Kampung Kali (pasar) | Investigasi warga/dialog |
| 5 | Tali yang Belum Dilepas | Pocong ⚠️ | Kota Lama | Serangan area bertelegraf |
| 6 | Api di Lereng | Kemamang | Lereng Gunung | Meter sinkronisasi penuh, api menyebar |
| 7 | Bayang di Atas Atap | Kalong Wewe | Kota Lama (malam) | Musuh udara |
| 8 | Kentongan Tengah Malam | Wewe Gombel | Lereng Gunung | Zona larangan pukul |
| 9 | Yang Tak Kasatmata | Genderuwo | Pelabuhan Utara | Musuh tak terlihat |
| 10 | Prasasti Tujuh Gerbang | Banaspati | Seluruh Arunapura | Kota terbakar, 3 fase |

Aturan skala: Jayadwara ±45 m (placeholder); boss Arc 1 = 0,5–1,0× Jayadwara. Progres antar-arc = kekuatan & teknik naik (Ep 20 Geunteut = lawan setara pertama).

---

## 5. Gameplay inti

**Loop episode (20–30 menit):** pembuka wayang → briefing → investigasi (3 petunjuk, min. 2 wajib) → konfrontasi skala manusia → transformasi → boss raksasa (2 fase) → penyegelan + debrief.

- **Mode manusia (porsi terbesar):** traversal, **scanner Netra**, investigasi (membuka **kelemahan boss**), combat **pencak silat** melee.
- **Mode raksasa:** combat yang **sama** (GAS ability yang sama, beda `UJDCombatProfile`). Sejak 16 Okt 2026 gerak raksasa **gesit "ala Mebius"**: serangan secepat manusia, berbalik cepat, lompat tinggi; rasa berat datang dari impact (hit-stop, camera shake, debu, suara, gedung runtuh), bukan animasi lambat.
- **Meter sinkronisasi** (pengganti timer): turun kalau gedung/warga kena, naik kalau melindungi warga, habis = transformasi berakhir paksa.
- **Syarat transformasi:** energi transformasi penuh (tombol **T** / **L1+R1**). Kalah sebagai Jayadwara → kembali jadi Aksa di tempat; Aksa mati → checkpoint.
- Kelemahan tidak ditemukan → boss tetap bisa dikalahkan (lebih lama), tidak pernah soft-lock.
- **Jubah upacara** Jayadwara: dipakai di luar combat, lepas otomatis saat lock-on/serangan pertama (buyar jadi serpihan emas), kembali saat boss kalah.

---

## 6. Teknis

- Module `Jayadwara`, **prefix class `JD`** (`AJDHumanCharacter`, `UJDCombatComponent`).
- Plugin: GAS, Enhanced Input, StateTree, Chaos Destruction (Geometry Collection), Niagara, Motion Warping.
- **Transformasi = ganti pawn** (`AJDPlayerController` UnPossess manusia → Possess raksasa; pawn manusia disembunyikan).
- Hirarki: `AJDCharacterBase` (ASC + `UJDAttributeSet` + `UJDCombatComponent`) → `AJDHumanCharacter` (Aksa), `AJDGiantCharacter` (Jayadwara); rencana `AJDEnemyBase` → `AJDBossBase`.
- Atribut: Health, Stamina, Poise, Sync, TransformEnergy (+Max), meta `IncomingDamage/IncomingPoiseDamage`.
- Combat: semua serangan = Gameplay Ability (`UJDGA_LightAttack/HeavyAttack/Dodge/Block`), hit lewat Anim Notify State trace dari socket, combo lewat tag `State.Combat.ComboWindow`. GE ditulis di C++ supaya bisa direview.
- C++ & montage hanya memakai **nama tulang Mannequin** (`hand_r`, `foot_l`). Semua animasi untuk skeleton Mannequin.
- Penamaan aset: `BP_ SM_ SK_ SKEL_ M_ MI_ T_ ABP_ AM_ NS_ WBP_ DA_ DT_ GA_ GE_ IA_ IMC_ LS_ PA_ IK_ RTG_`.
- Folder kode sekarang: `Source/Jayadwara/{Abilities, Animation, Characters, Combat, Core, UI}`; modul UncookedOnly `JayadwaraAnimNodes` untuk node AnimGraph (jangan taruh di modul Editor).
- Build: Build Tools 2022 + MSVC v14.38 + .NET Framework 4.8 SDK (tanpa IDE penuh). Setelah ubah header/UPROPERTY: tutup editor → `Build.bat JayadwaraEditor Win64 Development` → buka lagi. Claude boleh menutup/membuka editor sendiri. Isi `.cpp` saja boleh Live Coding.
- Target performa: 1080p 60 FPS PC kelas menengah.

**Pipeline aset karakter (gaya realistis):** developer membuat konsep + model dasar di **Tripo AI** (lisensi komersial) → Claude membersihkan, memisah bagian, rig (skeleton Mannequin), bobot, tekstur/mask zona, LOD, validator di **Blender 5.2** (skrip di `Art/Scripts/`, file kerja `Art/Blender/<karakter>/`) → impor & setup UE lewat `Tools/ue_import_*.py` + `Tools/ue_setup_*.py`.

---

## 7. Status saat ini (16 Okt 2026)

**Fase aktif: Fase 0 (setup, hampir selesai) + Fase 1 prototype greybox dikerjakan lebih awal.** Roadmap: F1 Des 2026–Mar 2027, F2 vertical slice Ep 1 Apr–Des 2027, F3 Steam page & demo, F4 Ep 2–10, F5 Early Access ±akhir 2029.

Iterasi Fase 1 (`docs/23` §11):

| Iter | Isi | Status |
|---|---|---|
| 1 | Fondasi GAS, HUD debug, cheat | ✅ (gamepad menyusul) |
| 2 | Combo ringan + hit | ✅ diuji developer |
| 2b | Combat Jayadwara = Aksa (paritas animasi) | 🟡 skrip siap 18 Okt (`ue_setup_giant_mixamo.py` → `ue_setup_giant_combo.py`), menunggu build + uji tangan |
| 3 | Berat, dodge, tangkis, parry | 🟡 C++ jadi, sisa uji tangan + animasi Mixamo |
| 4 | Hit react, stagger, target, warp | ⬜ |
| 5 | Minion, gelombang, checkpoint | ⬜ |
| 6 | Transformasi & combat raksasa | 🟡 combo raksasa + kelincahan ala Mebius (16 Okt) menunggu build + uji developer |
| 7 | Gedung hancur + meter sinkronisasi | ⬜ |
| 8 | Boss Jerangkong greybox | ⬜ |
| 9 | Loop utuh + playtest | ⬜ |

**Aset karakter:**
- **Jayadwara2** (Tripo) = model raksasa **aktif** sejak 13 Okt; model lama (stylized, dari skrip) disimpan sebagai cadangan. Desain: merah + hitam + emas + faceplate putih, tanduk emas, ornamen dada surya dengan permata statis, tanpa silver.
- **Jubah Jayadwara2** (docs/26): J1–J4 disetujui di Play, sisa pemicu lock-on (ganti tombol Y sementara) dan J5 (F2).
- **Aksa2** (Tripo, dikerjakan Hermes lalu dikoreksi Claude): terpasang paralel (`BP_Aksa2`, level `Test_Combat_Aksa2`) + 8 morph wajah; `BP_Aksa` lama utuh. Wajah Tripo + morph, tanpa MetaHuman untuk Ep 1.
- **Jerangkong** (boss Ep 1, 30,7 m) + **Kerangka** (minion 1,86 m): terpasang di UE dengan 14 potongan untuk mekanik rontok/susun ulang.
- **Tuyul** (Ep 2): rencana docs/27, backlog Fase 4.

**Level:** satu map per episode ala Resident Evil 4 (docs/28). Desain Ep 1 `Ep01_LawangSapta` (docs/30) dan Ep 2 `Ep02_KampungKali` (docs/31) disetujui; greybox UE Ep 1 jalur paralel, dikerjakan Hermes (branch `hermes/maps_ep1`) dari data `Art/Level/ep01_*`.

---

## 8. Agen lain: Hermes

Developer juga memakai agen **Hermes** sebagai pembantu eksperimen. Aturannya di `AGENTS.md`: kerja di worktree `C:\repository\unreal_engine\jayadwara_hermes`, branch `hermes/<topik>`, hanya menulis di sandbox (`Content/Hermes/`, `Source/Jayadwara/Hermes/`, `Hermes/`). Instruksi tugas dari Claude ada di `Hermes/<model>_hermes.md`, laporan Hermes di `Hermes/Laporan/`.

Saat developer minta review/implementasi hasil Hermes: baca laporannya, **ukur ulang sendiri** (`audit_karakter.py`, `banding_karakter.py`, `diagnosa_mesh.py --sebelum`) karena angka laporan Hermes pernah salah, cek `git diff origin/development...origin/hermes/<topik> --stat` untuk file di luar sandbox, lalu implementasikan ke `development` (C++ dipindah ke modul yang benar dengan prefix `JD`), bukan merge mentah.

---

## 9. Selera developer & pelajaran penting

- Model harus **mirip konsep**; developer menilai dari depan, **samping, atas, dan belakang**. Sensitif terhadap celah, lipatan/garis melintang, kesan "tempelan" atau "kotak", zirah yang mengambang/punuk di bahu.
- Developer menguji sendiri di **Play** (PIE). Editor yang di latar belakang jalan ±3 fps, jadi uji gerak/animasi remote tidak representatif; bug dari Play harus direproduksi dulu (di Blender/PIE) sebelum diperbaiki.
- **Cek PIE sebelum menjalankan skrip UE** (skrip impor yang jalan saat Play bisa menghapus aset).
- **Jangan impor mesh ke `SK_Mannequin`** (merusak skeleton; versi sehat = 171 tulang). Pakai salinan skeleton + Compatible Skeleton.
- Jangan hapus lalu impor ulang aset dengan nama sama (reimport ke objek mati); impor di tempat.
- Material Tripo harus diredam di UE (metalik/kekasaran/normal) atau terlihat basah.
- Fitur baru saat main → backlog, bukan langsung dikerjakan.

---

## 10. Peta dokumen `docs/`

| No | Isi |
|---|---|
| README | Indeks + ringkasan keputusan final |
| 01–06 | Konsep & pilar, dunia, karakter, skenario 5 arc, daftar 50 episode & boss, referensi mitologi |
| 07 | Gameplay & sistem |
| 08 | Requirement produksi + keputusan terbuka |
| 09 | Product brief (target pemain, USP, risiko) |
| 10 | Roadmap Fase 0–5 |
| 11 | Spesifikasi vertical slice Ep 1 (batas scope) |
| 12 | Technical design (arsitektur, folder, penamaan) |
| 13–15, 25–26 | Model Jayadwara lama, model sheet, material, redesign Jayadwara2, jubah |
| 16–18 | Panduan Arc 1, skenario Arc 1 (Ep 1 lengkap), kebutuhan Ep 1 |
| 19, 21–22 | Model Aksa, model sheet, material |
| 20, 24 | Model Jerangkong, model sheet |
| 23 | **Rencana Fase 1** (iterasi, gate, status) |
| 27 | Model Tuyul (backlog) |
| 28–31 | Struktur level per episode, Arc 2, desain level Ep 1 & Ep 2 |

---

## 11. Cara Claude sebaiknya merespons

1. Baca `docs/` yang relevan dulu sebelum mengusulkan perubahan desain; rujuk nomor dokumen dan kode keputusan (mis. "S1 di docs/17").
2. Cek usulan terhadap scope fase aktif dan daftar larangan IP.
3. Usulan yang butuh keputusan → tulis opsi bernomor + rekomendasi, biar developer tinggal pilih.
4. Kalau tidak punya akses repo (mis. chat biasa), minta developer menempelkan isi dokumen terkait; jangan mengarang nama aset, path, angka, atau status.
5. Laporan akhir: apa yang berubah, apa yang belum diuji, apa yang menunggu developer.
