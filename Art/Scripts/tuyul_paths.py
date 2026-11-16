"""Path bersama skrip Tuyul (dipindah dari sandbox Hermes ke struktur proyek, Okt 2026).

Semua skrip tuyul_*.py / validate_tuyul.py memakai modul ini, jadi tidak ada path tetap ke mesin tertentu.
Perantara (tidak di-commit): Art/Export/Textures_Tuyul/_work/ dan T_Tuyul_Color_src.png (lihat .gitignore).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "Art" / "Scripts"
BLENDER = ROOT / "Art" / "Blender" / "tuyul"           # tuyul_v05_skin.blend, tuyul_v09_smooth.blend (final)
EXPORT = ROOT / "Art" / "Export"                       # SK_Tuyul*.fbx + *_sockets.json
TEX = EXPORT / "Textures_Tuyul"                        # T_Tuyul_Color/N/ORM/Emit.png
WORK = TEX / "_work"                                   # perantara tekstur & render (di-ignore)
SOURCE = ROOT / "Art" / "Source" / "tuyul_tripo_v01.glb"
REFERENCE = ROOT / "docs" / "character" / "tuyul.png"  # konsep turnaround
