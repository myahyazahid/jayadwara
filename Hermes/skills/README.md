# Skill Hermes untuk JAYADWARA

Ditulis Claude dari cara kerjanya di proyek ini. Format standar `SKILL.md` (folder + frontmatter `name`/`description`), jadi bisa dipasang sebagai skill di Hermes Agent atau dibaca langsung. **Read-only untuk Hermes** (`hermes_cek_sandbox.py` menolak perubahan di folder ini); usul perubahan ditulis di laporan.

| Skill | Dipakai saat |
|---|---|
| [`jd-mulai-tugas`](jd-mulai-tugas/SKILL.md) | Awal **setiap** tugas: worktree & branch, baca aturan & riwayat, rencana berangka |
| [`jd-perbaiki-model`](jd-perbaiki-model/SKILL.md) | Ada yang rusak: "lengan robek", "ketiak bolong", "wajah meleh", audit GAGAL |
| [`jd-audit-model`](jd-audit-model/SKILL.md) | Setiap FBX baru / hasil perbaikan: validator, audit, banding, cara membaca |
| [`jd-blender-skrip`](jd-blender-skrip/SKILL.md) | Menjalankan/menulis skrip Blender: headless, versi file, kontrak export, jebakan bpy |
| [`jd-unreal-sandbox`](jd-unreal-sandbox/SKILL.md) | Apa pun di Unreal Editor: editor worktree, `/Game/Hermes/`, salinan skeleton, bukti tidak merusak |
| [`jd-selesai-tugas`](jd-selesai-tugas/SKILL.md) | Sebelum commit/push/lapor: checklist bukti, cek sandbox, pesan ke developer |

Skill ini ringkasan. Rincian ada di `AGENTS.md`, `Hermes/panduan_kerja_claude.md`, `Hermes/panduan_model_3d.md`, dan instruksi khusus model (`Hermes/<model>_hermes.md`).

## Memasang di Hermes Agent
Hermes Agent membaca skill dari folder skill-nya (biasanya `~/.hermes/skills/`; cek dokumentasi versi Hermes yang dipakai). Salin keenam folder `jd-*` ke sana. Contoh dari folder worktree:

```
# Linux / macOS / WSL
mkdir -p ~/.hermes/skills && cp -r Hermes/skills/jd-* ~/.hermes/skills/
# Windows PowerShell (kalau Hermes berjalan native di Windows)
Copy-Item -Recurse -Force Hermes\skills\jd-* $HOME\.hermes\skills\
```

Ulangi penyalinan setiap kali skill di repo diperbarui (`git merge origin/development` di worktree, lalu salin lagi). Kalau Hermes tidak memuat skill dari folder, `AGENTS.md` tetap menunjuk ke file `SKILL.md` ini, jadi Hermes bisa membacanya langsung.

## Kenapa skill bawaan Anthropic tidak disertakan
Skill dokumen Anthropic (docx, pdf, pptx, xlsx) berlisensi tertutup (hanya untuk dipakai lewat layanan Anthropic), jadi tidak boleh disalin ke repo. Skill contoh lain berlisensi terbuka, tetapi isinya tidak terkait proyek ini (belanja, reimbursement, gif, dll.). Yang membuat hasil Claude di proyek ini bagus adalah cara kerjanya, dan itu yang dituangkan di skill-skill ini.
