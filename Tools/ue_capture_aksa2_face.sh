#!/usr/bin/env bash
# Tangkap netral + 8 morph wajah Aksa2 lewat PIE (Git Bash). Editor terbuka, belum Play, level Test_Combat_Aksa2 aktif.
cd "$(dirname "$0")/.." || exit 1
P="$(pwd -W)/Tools/ue_capture_aksa2_face.py"
run() { python Tools/ue_remote.py -c "$1; exec(open(r'$P').read())" 2>&1 | tail -1; }
run "STAGE='cam'"
python Tools/ue_remote.py -c "unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()" >/dev/null 2>&1
sleep 8
run "STAGE='view'"
sleep 3
for m in None "'ak_blink_L'" "'ak_blink_R'" "'ak_smile'" "'ak_angry'" "'ak_mouth_open'" "'ak_brow_up'" "'ak_wince'" "'ak_sad'"; do
  run "STAGE='morph'; MORPH=$m"
  sleep 3
done
python Tools/ue_remote.py -c "unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()" >/dev/null 2>&1
sleep 4
run "STAGE='clean'"
