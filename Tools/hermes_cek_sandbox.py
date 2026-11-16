"""Cek isolasi kerja Hermes (AGENTS.md): semua perubahan harus di dalam sandbox.

Pakai (Python sistem, dari folder repo/worktree Hermes):
  python -I Tools/hermes_cek_sandbox.py            # bandingkan dengan origin/development
  python -I Tools/hermes_cek_sandbox.py --base origin/development
Memeriksa file yang berubah di commit branch ini (sejak titik cabang dari base), staged, belum di-stage, dan untracked.
Exit code 0 = semua di sandbox, 1 = ada file di luar sandbox (dicetak), 2 = bukan branch hermes/* atau git error.
Tidak mengubah apa pun.
"""
import argparse
import subprocess
import sys

SANDBOX = ("Content/Hermes/", "Source/Jayadwara/Hermes/", "Hermes/", "mixamo/asset/")   # mixamo/: mixamo/README.md
INSTRUKSI = ("Hermes/aksa_hermes.md", "Hermes/panduan_model_3d.md", "Hermes/panduan_kerja_claude.md")   # di dalam sandbox tapi milik Claude: read-only
# instruksi khusus model lain dari Claude juga read-only: Hermes/<model>_hermes.md, dan semua skill di Hermes/skills/
# aset rawan: kalau berubah, hampir pasti merusak proyek (insiden SK_Mannequin 13-14 Okt 2026, docs/25 R7)
RAWAN = ("Hermes/skills/", "Hermes/aksa_hermes.md", "Hermes/panduan_model_3d.md", "Hermes/panduan_kerja_claude.md", "Content/Characters/Mannequins/", "Content/Jayadwara/", "Config/", "Jayadwara.uproject", "Source/Jayadwara/",
         "Source/JayadwaraEditor/", "Art/Blender/", "Art/Export/", "docs/", ".gitattributes", ".gitignore")


def git(*args):
    r = subprocess.run(["git", "-c", "core.quotePath=false", *args], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        print(f"git {' '.join(args)} gagal:\n{r.stderr}", file=sys.stderr)
        sys.exit(2)
    return [line for line in r.stdout.splitlines() if line.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="origin/development")
    a = ap.parse_args()

    branch = git("rev-parse", "--abbrev-ref", "HEAD")[0]
    if not branch.startswith("hermes/"):
        print(f"GAGAL: branch aktif '{branch}', harus hermes/<topik>. Jangan kerja di branch lain.")
        sys.exit(2)

    changed = {}
    for p in git("diff", "--name-only", f"{a.base}...HEAD"):
        changed[p] = "commit"
    for p in git("diff", "--name-only", "--cached"):
        changed.setdefault(p, "staged")
    for p in git("diff", "--name-only"):
        changed.setdefault(p, "belum di-stage")
    for p in git("ls-files", "--others", "--exclude-standard"):
        changed.setdefault(p, "untracked")

    luar = sorted((p, s) for p, s in changed.items() if not p.startswith(SANDBOX) or p in INSTRUKSI or p.startswith("Hermes/skills/")
                  or (p.startswith("Hermes/") and p.count("/") == 1 and p.endswith("_hermes.md")))
    print(f"branch {branch}, base {a.base}: {len(changed)} file berubah, {len(luar)} di luar sandbox")
    for p, s in luar:
        tanda = "  !! RAWAN" if p.startswith(RAWAN) else ""
        print(f"  LUAR SANDBOX ({s}): {p}{tanda}")
    if luar:
        print("\nGAGAL. Kembalikan file di atas sebelum commit:")
        print("  file lama yang berubah : git restore --source=" + a.base + " --staged --worktree -- <path>")
        print("  file baru di luar sandbox: pindahkan ke sandbox (lihat AGENTS.md §2) atau hapus")
        print("  sudah ter-commit       : JANGAN force-push; buat commit baru yang mengembalikannya, lalu tulis di laporan")
        sys.exit(1)
    print("LULUS: semua perubahan di dalam sandbox.")


if __name__ == "__main__":
    main()
