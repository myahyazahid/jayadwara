"""Jalankan Python di Unreal Editor yang sedang terbuka, dari terminal (Python sistem, bukan Python UE).

Prasyarat: Project Settings > Plugins > Python > Enable Remote Execution (tersimpan di Config/DefaultEngine.ini).

Pakai:
  python Tools/ue_remote.py Tools/ue_setup_greybox.py     # jalankan file
  python Tools/ue_remote.py -c "print(unreal.SystemLibrary.get_engine_version())"
Output (print/log dari skrip) dicetak di terminal; exit code 1 kalau skrip melempar error.
"""
import argparse
import json
import os
import sys
import time

UE_ROOT = os.environ.get("UE_ROOT", r"C:\Program Files\Epic Games\UE_5.6")
sys.path.insert(0, os.path.join(UE_ROOT, r"Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python"))
import remote_execution  # noqa: E402


def _receive_message(self, expected_type):
    """Pengganti versi engine: aslinya berhenti saat satu recv() < buffer, sehingga output besar terpotong.
    Di sini baca terus sampai JSON lengkap."""
    data = b""
    while True:
        part = self._command_channel_socket.recv(1 << 20)
        if not part:
            break
        data += part
        try:
            json.loads(data.decode("utf-8"))
        except ValueError:                                       # JSON belum lengkap
            continue
        message = remote_execution._RemoteExecutionMessage(None, None)
        if message.from_json_bytes(data) and message.passes_receive_filter(self._node_id) and message.type_ == expected_type:
            return message
    raise RuntimeError("Remote party failed to send a valid response!")


remote_execution._RemoteExecutionCommandConnection._receive_message = _receive_message


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?")
    ap.add_argument("-c", dest="code")
    ap.add_argument("--wait", type=float, default=5.0, help="detik menunggu editor ditemukan")
    a = ap.parse_args()
    if a.code:
        command = a.code
    elif a.file:
        command = os.path.abspath(a.file).replace("\\", "/")   # MODE_EXEC_FILE menerima path file
    else:
        ap.error("butuh file atau -c")

    rex = remote_execution.RemoteExecution()
    rex.start()
    try:
        deadline = time.time() + a.wait
        while not rex.remote_nodes and time.time() < deadline:
            time.sleep(0.2)
        nodes = [n for n in rex.remote_nodes if "Jayadwara" in n.get("project_name", "")] or rex.remote_nodes
        if not nodes:
            print("Editor tidak ditemukan. Editor terbuka? Remote Execution aktif?", file=sys.stderr)
            return 2
        rex.open_command_connection(nodes[0]["node_id"])
        res = rex.run_command(command, unattended=True, exec_mode=remote_execution.MODE_EXEC_FILE)
        for o in res.get("output", []):
            print(f"[{o['type']}] {o['output']}".rstrip())
        if not res.get("success"):
            print(res.get("result"), file=sys.stderr)
            return 1
        return 0
    finally:
        rex.stop()


if __name__ == "__main__":
    sys.exit(main())
