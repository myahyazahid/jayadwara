"""MK4d — Verifikasi level tersimpan (Unreal Editor Python, via Tools/ue_remote.py).

Muat ulang level DARI DISK lalu uji ulang semua kriteria MK4 pada keadaan tersimpan:
- 145 objek ada, alas actor = alas hitungan +/- 5 cm, tag (hancur 90; penalti 61/10/19;
  blok_chaos 32 = 4 x BLOK1..8; atap_naik 27; adikara 11; curian 6)
- KAMPUNG_Musala, KAMPUNG_PosRT, REL_Jembatan*, PINTUAIR_*, JEMBATAN_* tanpa tag hancur
- 8 actor kelompok (total 1.817 item; rumah Dinding = Atap), 5 actor pohon (258/258), 1 tiang (55)
- gang utama x=-26 terbuka (line trace 1 m di atas tanah)
- jumlah draw call proxy (komponen mesh) untuk tampak atas C5

Pakai (dari WORKTREE, editor worktree terbuka):
  python Tools/ue_remote.py Hermes/Tools/maps_ep2_43_verifikasi.py
"""
import os
import sys
import json
import math
import time

import unreal

DEST = "/Game/Hermes/MapsEp2"
MAP = f"{DEST}/Maps/Test_Hermes_MapsEp2"
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
import ep02_medan_v02 as M  # noqa: E402

with open(os.path.join(REPO, "Art", "Level", "ep02_layout_v02.json"), encoding="utf-8") as f:
    DATA = json.load(f)
OBJEK, KELOMPOK = DATA["objek"], DATA["kelompok"]
POHON, TIANG = DATA["pohon_kelompok"], DATA["tiang_listrik"]

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

problems = []


def log(m):
    unreal.log(f"[MK4d] {m}")


def fail(m):
    problems.append(m)
    unreal.log_error(f"[MK4d] {m}")


def elev(x, y):
    return M.elev(x, y)


def frange(a, b, step):
    v = []
    x = a
    while x < b - 1e-9:
        v.append(x)
        x += step
    if not v or abs(v[-1] - b) > 1e-9:
        v.append(b)
    return v


def alas_rect(cx, cy, P, L, yaw, step=1.0):
    a = math.radians(yaw)
    ca, sa = math.cos(a), math.sin(a)
    lo = None
    for u in frange(-P / 2.0, P / 2.0, step):
        for v in frange(-L / 2.0, L / 2.0, step):
            wx, wy = cx + u * ca - v * sa, cy + u * sa + v * ca
            z = elev(wx, wy)
            lo = z if lo is None else min(lo, z)
    return lo


def expected_base(o):
    """Alas actor yang diharapkan (meter), sama dengan maps_ep2_40_objek.py."""
    if "z" in o:
        return float(o["z"])
    j = o["jenis"]
    if j == "dinding":
        (x0, y0), (x1, y1) = o["dari"], o["ke"]
        n = max(2, int(math.hypot(x1 - x0, y1 - y0)) + 1)
        b = min(elev(x0 + (x1 - x0) * i / (n - 1), y0 + (y1 - y0) * i / (n - 1)) for i in range(n))
    else:
        b = alas_rect(o["pos"][0], o["pos"][1], o["ukuran"][0], o["ukuran"][1], o.get("yaw", 0.0))
    b += o.get("z_dasar_relatif", 0.0)
    if j == "bidang" and "z" not in o:
        b += 0.05
    return b


def tags_of(a):
    try:
        return [str(t) for t in a.get_editor_property("tags")]
    except Exception:  # noqa: BLE001
        return []


def main():
    t0 = time.time()
    if not EAL.does_asset_exist(MAP):
        fail(f"level {MAP} tidak ada")
        return
    LES.load_level(MAP)
    log(f"level dimuat ulang dari disk: {MAP}")

    semua = list(EAS.get_all_level_actors())
    log(f"jumlah actor di level = {len(semua)}")
    by_label = {}
    for a in semua:
        by_label.setdefault(a.get_actor_label(), []).append(a)

    # ---- 145 objek ----
    n_ada = n_alas = 0
    tag = {"hancur": 0, "penalti_tinggi": 0, "penalti_normal": 0, "tanpa_penalti": 0,
           "blok_chaos": 0, "atap_naik": 0, "adikara": 0, "curian": 0}
    chaos_per = {}
    worst = 0.0
    for o in OBJEK:
        idd = o["id"]
        a = by_label.get(idd, [None])[0]
        if a is None:
            fail(f"objek hilang setelah reload: {idd}")
            continue
        n_ada += 1
        ts = tags_of(a)
        for k in tag:
            if k in ts:
                tag[k] += 1
        if "blok_chaos" in ts:
            b = next((x for x in ts if x.startswith("BLOK")), "?")
            chaos_per[b] = chaos_per.get(b, 0) + 1
        # alas
        base = expected_base(o)
        org, ext = a.get_actor_bounds(False)
        d = abs(org.z - ext.z - base * 100.0) / 100.0
        worst = max(worst, d)
        if d <= 0.05:
            n_alas += 1
    log(f"objek: ada {n_ada}/145 ; alas dalam +/-5 cm: {n_alas}/145 ; selisih terburuk {worst * 100:.1f} cm")
    log(f"tag: " + " ".join(f"{k}={v}" for k, v in tag.items()))
    log(f"blok_chaos per deret: {dict(sorted(chaos_per.items()))}")

    for pat in ("KAMPUNG_Musala", "KAMPUNG_PosRT", "REL_Jembatan", "PINTUAIR_", "JEMBATAN_"):
        hit = [i for i in by_label if i.startswith(pat)]
        bad = [i for i in hit if "hancur" in tags_of(by_label[i][0])]
        if bad:
            fail(f"{pat}* punya tag hancur: {bad}")
        else:
            log(f"{pat}* ({len(hit)} actor) tanpa tag hancur: OK")

    # ---- kelompok ----
    tot = 0
    for k in KELOMPOK:
        a = by_label.get(k["id"], [None])[0]
        if a is None:
            fail(f"kelompok hilang: {k['id']}")
            continue
        n_d = n_a = 0
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            if c.get_name() in ("Dinding", "Badan"):
                n_d = c.get_instance_count()
            elif c.get_name() == "Atap":
                n_a = c.get_instance_count()
        tot += len(k["item"])
        if n_d != len(k["item"]):
            fail(f"{k['id']}: instance {n_d} != item {len(k['item'])}")
        if k["bentuk"] == "rumah" and n_a != n_d:
            fail(f"{k['id']}: Atap {n_a} != Dinding {n_d}")
    log(f"kelompok: 8 actor, total item = {tot} (target 1.817)")

    # ---- pohon & tiang ----
    nb = nt = nti = n_act = 0
    for a in semua:
        lbl = a.get_actor_label()
        if lbl.startswith("POHON_"):
            n_act += 1
            for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
                if c.get_name() == "Batang":
                    nb += c.get_instance_count()
                elif c.get_name() == "Tajuk":
                    nt += c.get_instance_count()
        elif lbl == "TIANG_Listrik":
            for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
                nti += c.get_instance_count()
    log(f"pohon: {n_act} actor, batang {nb}, tajuk {nt} (target 5/258/258) ; tiang {nti} (target 55)")

    # ---- gang utama ----
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    medan = by_label.get("SM_Ep02_Medan", [None])[0]
    ign = [medan] if medan else []
    hits = 0
    for i in range(186):
        y0, y1 = 138.0 - i, 137.0 - i
        r = unreal.SystemLibrary.line_trace_single(
            world, unreal.Vector(-2600.0, -y0 * 100.0, (elev(-26, y0) + 1.0) * 100.0),
            unreal.Vector(-2600.0, -y1 * 100.0, (elev(-26, y1) + 1.0) * 100.0),
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, ign, unreal.DrawDebugTrace.NONE, True)
        if r is not None and r.to_tuple()[0]:
            hits += 1
    log(f"gang utama x=-26 (y +138..-48) 1 m di atas tanah: {'BEBAS' if hits == 0 else f'TERHALANG di {hits} tempat'}")

    # ---- draw call proxy (tampak atas) ----
    proxy = 0
    for a in semua:
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if c.get_editor_property("static_mesh") is not None:
                proxy += 1
    log(f"proxy draw call (komponen mesh) = {proxy} ; komponen ISM = "
        f"{sum(1 for a in semua for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent))}")

    ok = (n_ada == 145 and n_alas == 145 and tag["hancur"] == 90 and tag["penalti_tinggi"] == 61
          and tag["penalti_normal"] == 10 and tag["tanpa_penalti"] == 19 and tag["blok_chaos"] == 32
          and tag["atap_naik"] == 27 and tag["adikara"] == 11 and tag["curian"] == 6
          and tot == 1817 and n_act == 5 and nb == 258 and nt == 258 and nti == 55 and hits == 0
          and not problems)
    log(f"CEK MK4d (keadaan tersimpan): {'LULUS' if ok else 'GAGAL'}")
    log(f"WAKTU skrip MK4d: {time.time() - t0:.1f} s")
    for p in problems:
        unreal.log_warning("[MK4d] masalah: " + p)


main()
