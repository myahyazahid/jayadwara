"""Cek hasil retarget Mixamo -> Manny di sandbox (M4, Hermes/combo_iter2_hermes.md §5).

Hanya membaca. Jalan: python Tools/ue_remote.py Hermes/Tools/combo_iter2_cek_retarget.py
Menulis Hermes/Art/combo-iter2/Log/cek_retarget.json.

Untuk tiap A_Aksa_Mx_<peran> di /Game/Hermes/ComboIter2/Mixamo:
  panjang vs FBX (±1 frame, dari cek_fbx.json), skeleton (harus SK_Mannequin),
  tulang & jumlah puncak kecepatan (tangan/kaki relatif pelvis, logika strike_timings),
  tinggi pinggul minimum, dan lompatan tulang antar-frame (tanda retarget patah).
"""
import json
import os

import unreal

DEST = "/Game/Hermes/ComboIter2"
MX = f"{DEST}/Mixamo"
LOG_DIR = os.path.join(unreal.Paths.project_dir(), "Hermes/Art/combo-iter2/Log")
STRIKE_BONES = ("hand_r", "hand_l", "foot_r", "foot_l")
CEK_TULANG = ("pelvis", "spine_01", "head", "hand_l", "hand_r", "foot_l", "foot_r")
KENA_BONE = {"tangan": ("hand_l", "hand_r"), "kaki": ("foot_l", "foot_r")}
# peran yang boleh pinggulnya rendah (dodge/air_slam) — panduan §5
PINGGUL_RENDAH_OK = ("dodge_", "air_slam")
TOLERANSI_FRAME = 1.0 / 30.0 + 0.005
# peran yang sengaja dipangkas (combo_iter2_pangkas.py) -> panjang yang diharapkan, bukan panjang FBX.
# air_slam: kode memakainya sebagai pose menukik singkat (JDGA_HeavyAttack baris 108).
DIPANGKAS = {"air_slam": 0.40, "air": 0.867, "light_01": 1.10, "light_02": 1.133}

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary


def log(msg):
    unreal.log(f"[cek_retarget] {msg}")


def muat_cek_fbx():
    p = os.path.join(LOG_DIR, "cek_fbx.json")
    if not os.path.isfile(p):
        return {}
    with open(p, encoding="utf-8") as fh:
        d = json.load(fh)
    return {h["file"][:-4]: h for h in d["file"] if h.get("file", "").endswith(".fbx")}


def sampel(seq, dt=1.0 / 60.0):
    """Pose tiap frame: (waktu, pelvis_z_cm, {tulang: posisi relatif pelvis}, {tulang: posisi dunia})."""
    length = AL.get_sequence_length(seq)
    opts = unreal.AnimPoseEvaluationOptions()
    world = unreal.AnimPoseSpaces.WORLD
    hasil = []
    for i in range(int(length / dt) + 1):
        t = min(i * dt, length)
        pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(seq, t, opts)
        pelvis = unreal.AnimPoseExtensions.get_bone_pose(pose, "pelvis", world).translation
        rel = {b: unreal.AnimPoseExtensions.get_bone_pose(pose, b, world).translation - pelvis
               for b in STRIKE_BONES}
        dunia = {b: unreal.AnimPoseExtensions.get_bone_pose(pose, b, world).translation
                 for b in CEK_TULANG}
        hasil.append((t, pelvis.z, rel, dunia))
    return hasil, length, dt


T_AWAL = 0.10          # puncak < 0,1 s = transisi masuk animasi (blend_in 0,08 s), bukan hantaman


def semua_puncak(samples, dt):
    """[(kecepatan, tulang, waktu)] semua sampel kecepatan setelah T_AWAL, urut tercepat."""
    out = []
    for i in range(1, len(samples)):
        t, _, rel, _ = samples[i]
        _, _, prev, _ = samples[i - 1]
        if t < T_AWAL:
            continue
        for b in STRIKE_BONES:
            out.append(((rel[b] - prev[b]).length() / dt, b, t))
    out.sort(reverse=True)
    return out


def puncak(samples, dt, jumlah=1, keluarga=None):
    """[(kecepatan, tulang, waktu)] puncak tercepat berjarak >= 0,2 s.

    keluarga = tulang yang diharapkan kena (mis. ("foot_l","foot_r") untuk tendangan). Ayunan tangan pada animasi
    Mixamo sering lebih cepat dari tendangannya, jadi puncak dicari di keluarga itu saja — kalau tidak, jendela hit
    mendarat di tangan padahal jurusnya tendangan (temuan untuk Claude, lihat laporan).
    """
    out = [r for r in semua_puncak(samples, dt) if keluarga is None or r[1] in keluarga]
    peaks = []
    for speed, bone, t in out:
        if len(peaks) >= jumlah:
            break
        if all(abs(t - p[2]) >= 0.2 for p in peaks):
            peaks.append((speed, bone, t))
    return sorted(peaks, key=lambda p: p[2])


def cek_satu(nama_peran, fbx):
    path = f"{MX}/A_Aksa_Mx_{nama_peran}"
    seq = unreal.load_asset(path)
    h = {"peran": nama_peran, "aset": path, "gagal": [], "catatan": []}
    if not isinstance(seq, unreal.AnimSequence):
        h["gagal"].append("AnimSequence tidak ada / bukan AnimSequence")
        h["lulus"] = False
        return h

    samples, length, dt = sampel(seq)
    h["panjang_s"] = round(length, 3)
    h["frame_ue"] = len(samples)
    sk = seq.get_editor_property("skeleton")
    h["skeleton"] = sk.get_path_name() if sk else None
    if not sk or sk.get_name() != "SK_Mannequin":
        h["gagal"].append(f"skeleton bukan SK_Mannequin ({h['skeleton']})")

    # panjang vs FBX (atau vs panjang pangkasan kalau peran ini sengaja dipangkas)
    if fbx:
        h["panjang_fbx_s"] = fbx.get("detik")
        h["frame_fbx"] = fbx.get("frame_jumlah")
        acuan = DIPANGKAS.get(nama_peran, fbx.get("detik"))
        if nama_peran in DIPANGKAS:
            h["catatan"].append(f"dipangkas sengaja: {acuan:.2f} s (FBX {fbx.get('detik'):.2f} s)")
        if acuan is not None and abs(length - acuan) > TOLERANSI_FRAME:
            h["gagal"].append(f"panjang {length:.3f} s vs acuan {acuan:.3f} s (beda > 1 frame)")
    else:
        h["catatan"].append("tidak ada data cek_fbx.json untuk file ini")

    # tulang kena
    kena = (fbx or {}).get("kena")
    jumlah = 2 if nama_peran == "finisher_02" else 1
    keluarga = KENA_BONE.get(kena) if kena else None
    peaks = puncak(samples, dt, jumlah, keluarga)
    h["puncak"] = [{"tulang": b, "waktu_s": round(t, 3), "kecepatan_cm_s": round(s, 1)} for s, b, t in peaks]
    global_top = semua_puncak(samples, dt)[0]
    h["puncak_global"] = {"tulang": global_top[1], "waktu_s": round(global_top[2], 3),
                          "kecepatan_cm_s": round(global_top[0], 1)}
    if kena and global_top[1] not in keluarga:
        h["catatan"].append(
            f"puncak global {global_top[1]} {global_top[0]:.0f} cm/s @{global_top[2]:.2f} s "
            f"(bukan {kena}) — auto strike_timings proyek akan memilih tulang ini")
    h["kena_diharapkan"] = kena
    h["kena_jumlah_diharapkan"] = jumlah if kena else 0
    if kena:
        boleh = KENA_BONE[kena]
        if len(peaks) < jumlah:
            h["gagal"].append(f"puncak hanya {len(peaks)}, harusnya {jumlah}")
        for s, b, t in peaks[:jumlah]:
            if b not in boleh:
                h["gagal"].append(f"puncak {b} pada {t:.2f} s bukan tulang {kena} ({boleh})")
        if len(peaks) >= 2 and abs(peaks[1][2] - peaks[0][2]) < 0.2:
            h["gagal"].append("dua puncak berjarak < 0,2 s")

    # tinggi pinggul
    zmin = min(s[1] for s in samples)
    h["pinggul_min_cm"] = round(zmin, 2)
    boleh_rendah = nama_peran.startswith(PINGGUL_RENDAH_OK)
    if not boleh_rendah and zmin < 40.0:
        h["gagal"].append(f"pinggul turun ke {zmin:.1f} cm (< 40 cm)")
    elif boleh_rendah:
        h["catatan"].append("peran boleh pinggul rendah (dodge/air_slam)")

    # lompatan tulang antar-frame
    lompat = 0.0
    tulang_lompat = None
    for i in range(1, len(samples)):
        for b in CEK_TULANG:
            d = (samples[i][3][b] - samples[i - 1][3][b]).length()
            if d > lompat:
                lompat, tulang_lompat = d, b
    h["lompat_maks_cm"] = round(lompat, 2)
    h["lompat_tulang"] = tulang_lompat
    if lompat > 50.0:
        h["gagal"].append(f"tulang {tulang_lompat} lompat {lompat:.1f} cm antar-frame (> 50 cm)")

    # tanda tangan gerak: posisi 7 tulang tiap 2 frame (untuk deteksi animasi yang sama)
    h["_sig"] = [[round(c, 1) for b in CEK_TULANG for c in
                  (samples[i][3][b].x, samples[i][3][b].y, samples[i][3][b].z)]
                 for i in range(0, len(samples), 2)]

    h["lulus"] = not h["gagal"]
    return h


def main():
    fbx_data = muat_cek_fbx()
    # pakai registry langsung: EditorAssetLibrary.list_assets bisa kosong setelah editor dibuka ulang
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    ar.scan_paths_synchronous([MX], True, True)
    aset = [str(a.package_name) for a in ar.get_assets_by_path(MX, recursive=False)]
    peran = sorted(os.path.basename(p).replace("A_Aksa_Mx_", "") for p in aset
                   if os.path.basename(p).startswith("A_Aksa_Mx_"))
    log(f"{len(peran)} animasi di {MX}: {peran}")

    hasil = [cek_satu(p, fbx_data.get(p)) for p in peran]
    for h in hasil:
        log(f"{h['peran']}: {'LULUS' if h['lulus'] else 'GAGAL'} panjang={h.get('panjang_s')} "
            f"puncak={[(p['tulang'], p['waktu_s']) for p in h.get('puncak', [])]} "
            f"pinggul_min={h.get('pinggul_min_cm')} lompat={h.get('lompat_maks_cm')} "
            f"gagal={h['gagal']}")

    # animasi yang geraknya sama persis (sering karena salah download / dobel simpan)
    sigs = {h["peran"]: h.pop("_sig", []) for h in hasil}
    for i, a in enumerate(hasil):
        for b in hasil[i + 1:]:
            sa, sb = sigs.get(a["peran"], []), sigs.get(b["peran"], [])
            n = min(len(sa), len(sb))
            if n < 10:
                continue
            beda = max(abs(x - y) for fa, fb in zip(sa[:n], sb[:n]) for x, y in zip(fa, fb))
            if beda < 1.0:
                for x, y in ((a, b), (b, a)):
                    x.setdefault("gerak_identik_dengan", []).append(y["peran"])
                    x["catatan"].append(f"gerak identik dengan {y['peran']} (beda maks {beda:.2f} cm) "
                                        f"— kemungkinan salah download")

    belum = sorted(set(fbx_data) - set(peran))
    out = {
        "jumlah": len(hasil),
        "lulus": sum(1 for h in hasil if h["lulus"]),
        "gagal": sum(1 for h in hasil if not h["lulus"]),
        "belum_retarget": belum,
        "file": hasil,
    }
    os.makedirs(LOG_DIR, exist_ok=True)
    p = os.path.join(LOG_DIR, "cek_retarget.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    log(f"lulus {out['lulus']}/{out['jumlah']} -> {p}")
    if belum:
        log(f"belum ada animasi retarget untuk: {belum}")
    for h in hasil:
        if not h["lulus"]:
            unreal.log_error(f"[cek_retarget] GAGAL {h['peran']}: " + "; ".join(h["gagal"]))


main()
