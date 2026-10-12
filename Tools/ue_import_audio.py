"""Import SFX pilihan (Audio/pilihan.json) ke Unreal Engine 5.6 — Unreal Editor Python.

STATUS: BELUM DIUJI (ditulis 12 Okt 2026 tanpa editor). Kalau gagal, import manual: drag WAV dari Audio/Kandidat/
ke Content Browser /Game/Jayadwara/Audio/<Grup>/, lalu rename sesuai kolom "Nama aset UE" di Audio/KANDIDAT.md.

Alur:
  1. Dengarkan kandidat di Audio/Kandidat/<slot>/, isi Audio/pilihan.json: {"01_pukulan_ringan": "k1", ...}
  2. Editor terbuka: python Tools/ue_remote.py Tools/ue_import_audio.py
     atau Output Log -> Python: py "C:/repository/unreal_engine/jayadwara/Tools/ue_import_audio.py"
Hasil: /Game/Jayadwara/Audio/<Grup>/S_<Nama> (set Kenney: S_<Nama>_01.._05). Ambien/musik di-set Looping.
Sound Cue (SC_, mis. Random + pitch untuk raksasa) dirangkai di editor.
"""
import json
import os

import unreal

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ROOT = "/Game/Jayadwara/Audio"

with open(os.path.join(REPO, "Audio", "kandidat.json"), encoding="utf-8") as f:
    kandidat = {r["slot"]["id"]: r for r in json.load(f)}
with open(os.path.join(REPO, "Audio", "pilihan.json"), encoding="utf-8") as f:
    pilihan = {k: v for k, v in json.load(f).items() if not k.startswith("_") and v}

tasks, loops = [], []
for slot_id, pick in pilihan.items():
    r = kandidat.get(slot_id)
    if r is None:
        unreal.log_warning(f"[Audio] slot {slot_id} tidak ada di kandidat.json")
        continue
    idx = int(pick.lstrip("k")) - 1
    if not 0 <= idx < len(r["picks"]):
        unreal.log_warning(f"[Audio] {slot_id}: kandidat {pick} tidak ada")
        continue
    files = r["picks"][idx]["out"]
    dest = f"{ROOT}/{r['slot']['grp']}"
    for n, rel in enumerate(files, 1):
        name = r["slot"]["ue"] + (f"_{n:02d}" if len(files) > 1 else "")
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", os.path.join(REPO, rel))
        t.set_editor_property("destination_path", dest)
        t.set_editor_property("destination_name", name)
        t.set_editor_property("automated", True)
        t.set_editor_property("replace_existing", True)
        t.set_editor_property("save", True)
        tasks.append(t)
        if r["slot"]["kind"] == "loop":
            loops.append(f"{dest}/{name}")

unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
for t in tasks:
    unreal.log(f"[Audio] {os.path.basename(t.get_editor_property('filename'))} -> "
               f"{list(t.get_editor_property('imported_object_paths')) or 'GAGAL'}")
for path in loops:
    wave = unreal.EditorAssetLibrary.load_asset(path)
    if wave:
        wave.set_editor_property("looping", True)
        unreal.EditorAssetLibrary.save_asset(path)
unreal.log(f"[Audio] selesai: {len(tasks)} file, {len(loops)} di-set looping")
