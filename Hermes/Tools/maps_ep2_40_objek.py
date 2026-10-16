"""MK4a — 145 objek tunggal (Unreal Editor Python, via Tools/ue_remote.py).

DEST = /Game/Hermes/MapsEp2  (sandbox Hermes)
Bangun 145 objek dari Art/Level/ep02_layout_v02.json (jenis: kotak 75, rumah 60, dinding 5,
bidang 4, kerucut 1) ke level DEST/Maps/Test_Hermes_MapsEp2.
- Jenis `kotak`  : Cube diskala P,L,T; lokasi Z = alas + T/2.
- Jenis `rumah`  : SATU actor induk + 2 komponen (Dinding P x L x (T-0,5) pakai `mi`;
                   Atap pelat (P+0,4) x (L+0,4) x 0,5 pakai `mi_atap`).
- Jenis `bidang` : Plane diskala P,L; ber-`z` di tinggi itu (air), tanpa `z` 5 cm di atas tanah.
- Jenis `dinding`: kotak tipis dari `dari` ke `ke`, tinggi `tinggi`, tebal `tebal`.
- Jenis `kerucut`: Cone diskala [diameter, diameter, tinggi] (tajuk beringin).
Tag: hancur / penalti_tinggi|penalti_normal|tanpa_penalti / blok_chaos (+BLOK n) / atap_naik /
adikara / curian. `tanpa_tabrakan` -> collision NoCollision.

Uji (cetak tabel): jumlah objek, alas actor = alas hitung +/- 5 cm, hitungan tag, trace gang utama
(mendatar 1 m di atas tanah, x -26, y +138 .. -48, tidak mengenai apa pun), waktu skrip.

Pakai (dari WORKTREE, editor worktree terbuka):
  python Tools/ue_remote.py Hermes/Tools/maps_ep2_40_objek.py
"""
import os
import sys
import json
import math
import time

import unreal

DEST = "/Game/Hermes/MapsEp2"
MAP = f"{DEST}/Maps/Test_Hermes_MapsEp2"
MAT_DIR = f"{DEST}/Materials"
CUBE = "/Engine/BasicShapes/Cube"
PLANE = "/Engine/BasicShapes/Plane"
CONE = "/Engine/BasicShapes/Cone"

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
import ep02_medan_v02 as M  # noqa: E402

with open(os.path.join(REPO, "Art", "Level", "ep02_layout_v02.json"), encoding="utf-8") as f:
    DATA = json.load(f)
OBJEK = DATA["objek"]

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)

problems = []
built_ids = []


def log(m):
    unreal.log(f"[MK4a] {m}")


def fail(m):
    problems.append(m)
    unreal.log_error(f"[MK4a] {m}")


def elev(x, y):
    return M.elev(x, y)


def bottom_local(mesh):
    b = mesh.get_bounds()
    return b.origin.z - b.box_extent.z


# ------------------------------------------------------------------ geometri alas (sama seperti generator)
def frange(a, b, step):
    vals = []
    x = a
    while x < b - 1e-9:
        vals.append(x)
        x += step
    if not vals or abs(vals[-1] - b) > 1e-9:
        vals.append(b)
    return vals


def rot_pt(cx, cy, u, v, yaw_deg):
    a = math.radians(yaw_deg)
    ca, sa = math.cos(a), math.sin(a)
    return cx + u * ca - v * sa, cy + u * sa + v * ca


def sampel_rect(cx, cy, P, L, yaw_deg, step=1.0):
    hx, hy = P / 2.0, L / 2.0
    pts = []
    for u in frange(-hx, hx, step):
        for v in frange(-hy, hy, step):
            wx, wy = rot_pt(cx, cy, u, v, yaw_deg)
            pts.append((wx, wy, elev(wx, wy)))
    return pts


def sampel_seg(ax, ay, bx, by, step=1.0):
    length = math.hypot(bx - ax, by - ay)
    n = max(1, int(length / step))
    return [(ax + (bx - ax) * i / n, ay + (by - ay) * i / n,
             elev(ax + (bx - ax) * i / n, ay + (by - ay) * i / n)) for i in range(n + 1)]


def alas_obj(o):
    """Alas (meter). Objek ber-`z` = z ABSOLUT; lainnya = elev terendah di tapak."""
    if "z" in o:
        return float(o["z"])
    j = o["jenis"]
    if j == "dinding":
        return min(p[2] for p in sampel_seg(o["dari"][0], o["dari"][1], o["ke"][0], o["ke"][1]))
    cx, cy = o["pos"]
    P, L = o["ukuran"][0], o["ukuran"][1]
    return min(p[2] for p in sampel_rect(cx, cy, P, L, o.get("yaw", 0.0)))


def elev_center(o):
    if o["jenis"] == "dinding":
        return elev((o["dari"][0] + o["ke"][0]) / 2.0, (o["dari"][1] + o["ke"][1]) / 2.0)
    return elev(o["pos"][0], o["pos"][1])


def expected_base(o):
    b = alas_obj(o) + o.get("z_dasar_relatif", 0.0)
    if o["jenis"] == "bidang" and "z" not in o:
        b += 0.05
    return b


# ------------------------------------------------------------------ spawn helpers
def add_tags(actor, tags):
    if not tags:
        return
    try:
        actor.set_editor_property("tags", [unreal.Name(t) for t in tags])
    except Exception as e:  # noqa: BLE001
        fail(f"tag {tags} gagal pada {actor.get_actor_label()}: {e}")


def set_nocollision(actor):
    comp = actor.static_mesh_component
    try:
        comp.set_collision_profile_name("NoCollision")
    except Exception:  # noqa: BLE001
        comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)


def spawn(shape_path, label, loc, yaw_ue, scale_m, mi, folder, tags, collision=True):
    mesh = EAL.load_asset(shape_path)
    a = EAS.spawn_actor_from_object(mesh, loc, unreal.Rotator(pitch=0.0, yaw=yaw_ue, roll=0.0))
    a.set_actor_label(label)
    a.set_actor_scale3d(unreal.Vector(scale_m[0], scale_m[1], scale_m[2]))
    a.set_folder_path(folder)
    if mi is not None:
        a.static_mesh_component.set_material(0, mi)
    if not collision:
        set_nocollision(a)
    add_tags(a, tags)
    return a


def new_smc(actor, root, nama, mesh, mi, collision=True):
    params = unreal.AddNewSubobjectParams()
    params.set_editor_property("parent_handle", root)
    params.set_editor_property("new_class", unreal.StaticMeshComponent)
    h, msg = SDS.add_new_subobject(params)
    if str(msg):
        fail(f"SMC {nama} pada {actor.get_actor_label()}: {msg}")
    SDS.rename_subobject(h, nama)
    comp = next((c for c in actor.get_components_by_class(unreal.StaticMeshComponent)
                 if c.get_name() == nama), None)
    if comp is None:
        fail(f"SMC {nama} tidak ditemukan di {actor.get_actor_label()}")
        return None
    comp.set_static_mesh(mesh)
    if mi is not None:
        comp.set_material(0, mi)
    try:
        comp.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    except Exception:  # noqa: BLE001
        pass
    comp.set_collision_profile_name("BlockAll" if collision else "NoCollision")
    return comp


def tags_for(o):
    tags = []
    if o.get("hancur"):
        tags.append("hancur")
    p = o.get("penalti")
    if p == "tinggi":
        tags.append("penalti_tinggi")
    elif p == "normal":
        tags.append("penalti_normal")
    elif p == "tanpa":
        tags.append("tanpa_penalti")
    if "blok_chaos" in o:
        tags.append("blok_chaos")
        tags.append(o["blok_chaos"])
    if o.get("atap_naik"):
        tags.append("atap_naik")
    if o.get("milik") == "Adikara":
        tags.append("adikara")
    if o.get("curian"):
        tags.append("curian")
    return tags


def build_objek(o, mis):
    idd, j = o["id"], o["jenis"]
    folder = idd.split("_")[0]
    tags = tags_for(o)
    base = expected_base(o)
    mi = mis.get(o["mi"])
    nocoll = bool(o.get("tanpa_tabrakan"))

    if j == "kotak":
        x, y = o["pos"]
        P, L, T = o["ukuran"]
        loc = unreal.Vector(x * 100.0, -y * 100.0, (base + T / 2.0) * 100.0)
        return [spawn(CUBE, idd, loc, -o.get("yaw", 0.0), (P, L, T), mi, folder, tags, not nocoll)]

    if j == "rumah":
        x, y = o["pos"]
        P, L, T = o["ukuran"]
        hw = T - 0.5
        yaw_ue = -o.get("yaw", 0.0)
        # 1 actor (dinding = root StaticMeshComponent) + 1 komponen anak "Atap" (pola B:
        # bare Actor memunculkan BillboardComponent yang mengotori get_actor_bounds)
        a = EAS.spawn_actor_from_object(EAL.load_asset(CUBE),
                                        unreal.Vector(x * 100.0, -y * 100.0, (base + hw / 2.0) * 100.0),
                                        unreal.Rotator(pitch=0.0, yaw=yaw_ue, roll=0.0))
        a.set_actor_label(idd)
        a.set_actor_scale3d(unreal.Vector(P, L, hw))
        a.set_folder_path(folder)
        if mi is not None:
            a.static_mesh_component.set_material(0, mi)
        if nocoll:
            set_nocollision(a)
        hb = SDS.k2_gather_subobject_data_for_instance(a)
        ca = new_smc(a, hb[0], "Atap", EAL.load_asset(CUBE), mis.get(o.get("mi_atap")), not nocoll)
        if ca is not None:
            ca.set_relative_location(unreal.Vector(0.0, 0.0, (hw / 2.0 + 0.25) / hw * 100.0), False, False)
            ca.set_relative_scale3d(unreal.Vector((P + 0.4) / P, (L + 0.4) / L, 0.5 / hw))
        add_tags(a, tags)
        return [a]

    if j == "bidang":
        x, y = o["pos"]
        P, L = o["ukuran"]
        loc = unreal.Vector(x * 100.0, -y * 100.0, base * 100.0)
        return [spawn(PLANE, idd, loc, -o.get("yaw", 0.0), (P, L, 1.0), mi, folder, tags, not nocoll)]

    if j == "dinding":
        ax, ay = o["dari"]
        bx, by = o["ke"]
        dx, dy = (bx - ax) * 100.0, -(by - ay) * 100.0
        length_m = math.hypot(dx, dy) / 100.0
        yaw_ue = math.degrees(math.atan2(dy, dx))
        cx, cy = (ax + bx) / 2.0 * 100.0, -(ay + by) / 2.0 * 100.0
        h, tebal = o["tinggi"], o["tebal"]
        a = spawn(CUBE, idd, unreal.Vector(cx, cy, (base + h / 2.0) * 100.0),
                  yaw_ue, (length_m, tebal, h), mi, folder, tags, not nocoll)
        return [a]

    if j == "kerucut":
        x, y = o["pos"]
        d1, d2, t = o["ukuran"]
        loc = unreal.Vector(x * 100.0, -y * 100.0, base * 100.0 - bottom_local(EAL.load_asset(CONE)) * t)
        return [spawn(CONE, idd, loc, -o.get("yaw", 0.0), (d1, d2, t), mi, folder, tags, not nocoll)]

    fail(f"jenis tak dikenal: {idd} / {j}")
    return []


def find_by_label(label):
    for a in EAS.get_all_level_actors():
        if a.get_actor_label() == label:
            return a
    return None


# ------------------------------------------------------------------ level & pembersihan
def load_level():
    if not EAL.does_asset_exist(MAP):
        fail(f"level {MAP} tidak ada — jalankan MK3 dulu")
        return False
    LES.load_level(MAP)
    log(f"level dimuat: {MAP}")
    if find_by_label("SM_Ep02_Medan") is None:
        fail("SM_Ep02_Medan tidak ada di level — jalankan MK3 dulu")
        return False
    return True


def bersihkan_sebelumnya():
    labels = {o["id"] for o in OBJEK}
    n = 0
    for a in list(EAS.get_all_level_actors()):
        if a.get_actor_label() in labels:
            a.destroy_actor()
            n += 1
    if n:
        log(f"hapus {n} actor MK4a dari sesi sebelumnya")


# ------------------------------------------------------------------ uji
def uji():
    log("TABEL UJI OBJEK: id | jenis | alas_hitung(m) | alas_actor(m) | d(cm) | tag")
    n_ok = 0
    cnt = {"hancur": 0, "penalti_tinggi": 0, "penalti_normal": 0, "tanpa_penalti": 0,
           "blok_chaos": 0, "atap_naik": 0, "adikara": 0, "curian": 0}
    blok = {}
    for o in OBJEK:
        idd = o["id"]
        a = find_by_label(idd)
        if a is None:
            fail(f"objek hilang: {idd}")
            continue
        origin, extent = a.get_actor_bounds(False)
        alas_actor = (origin.z - extent.z) / 100.0
        exp = expected_base(o)
        d_cm = (alas_actor - exp) * 100.0
        if abs(d_cm) <= 5.0:
            n_ok += 1
        else:
            fail(f"{idd}: alas actor {alas_actor:.2f} m != hitung {exp:.2f} m (d={d_cm:+.1f} cm)")
        tags = [str(t) for t in a.get_editor_property("tags")]
        for t in cnt:
            if t in tags:
                cnt[t] += 1
        if o.get("blok_chaos"):
            blok[o["blok_chaos"]] = blok.get(o["blok_chaos"], 0) + 1
        log("  %-26s %-8s %8.2f %10.2f %+7.1f  %s" % (idd, o["jenis"], exp, alas_actor, d_cm, ",".join(tags)))

    log(f"objek ditemukan = {len(built_ids)} (target 145) | alas OK = {n_ok}/145")
    log(f"tag: hancur={cnt['hancur']} (90) penalti_tinggi={cnt['penalti_tinggi']} (61) "
        f"penalti_normal={cnt['penalti_normal']} (10) tanpa_penalti={cnt['tanpa_penalti']} (19) "
        f"blok_chaos={cnt['blok_chaos']} (32) atap_naik={cnt['atap_naik']} (27) "
        f"adikara={cnt['adikara']} (11) curian={cnt['curian']} (6)")
    log(f"blok_chaos per deret: {dict(sorted(blok.items()))} (tiap deret target 4)")

    bad = []
    for o in OBJEK:
        idd = o["id"]
        if (idd in ("KAMPUNG_Musala", "KAMPUNG_PosRT") or idd.startswith(("REL_Jembatan", "PINTUAIR_", "JEMBATAN_"))):
            a = find_by_label(idd)
            if a and "hancur" in [str(t) for t in a.get_editor_property("tags")]:
                bad.append(idd)
    if bad:
        fail(f"seharusnya tanpa tag hancur tapi punya: {bad}")
    else:
        log("KAMPUNG_Musala, KAMPUNG_PosRT, REL_Jembatan*, PINTUAIR_*, JEMBATAN_* tanpa tag hancur: OK")
    return n_ok, cnt, blok


def test_gang():
    """Trace mendatar 1 m di atas tanah sepanjang x -26 dari y +138 ke y -48; tak mengenai apa pun.
    Catatan: line_trace_single mengembalikan None bila TIDAK mengenai apa pun."""
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    medan = find_by_label("SM_Ep02_Medan")
    ignore = [medan] if medan else []
    x = -26.0

    def trace(p0, p1, ign):
        res = unreal.SystemLibrary.line_trace_single(
            world, p0, p1, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, ign,
            unreal.DrawDebugTrace.NONE, True)
        return None if res is None else res.to_tuple()

    ctl = trace(unreal.Vector(x * 100.0, -138.0 * 100.0, 20000.0),
                unreal.Vector(x * 100.0, -138.0 * 100.0, -20000.0), [])
    if ctl is not None and ctl[0]:
        log(f"kontrol trace vertikal x=-26,y=138 mengenai '{ctl[9].get_actor_label() if ctl[9] else '?'}' -> trace bekerja")
    else:
        fail("kontrol trace vertikal tidak mengenai apa pun -> trace tidak bekerja")

    ys = [138.0 - i for i in range(0, 187)]
    hits = []
    for i in range(len(ys) - 1):
        y0, y1 = ys[i], ys[i + 1]
        p0 = unreal.Vector(x * 100.0, -y0 * 100.0, (elev(x, y0) + 1.0) * 100.0)
        p1 = unreal.Vector(x * 100.0, -y1 * 100.0, (elev(x, y1) + 1.0) * 100.0)
        tup = trace(p0, p1, ignore)
        if tup is not None and tup[0]:
            lbl = tup[9].get_actor_label() if tup[9] else "?"
            hits.append((y0, lbl))
    if hits:
        fail(f"gang utama x=-26 terhalang di {len(hits)} tempat: {hits[:8]}")
    else:
        log("gang utama x=-26 (y +138..-48) 1 m di atas tanah: BEBAS (tidak mengenai apa pun)")
    return hits


# ------------------------------------------------------------------ main
def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[MK4a] Editor sedang Play (PIE) — hentikan dulu lalu jalankan ulang")
        return
    t0 = time.time()
    if not load_level():
        return
    bersihkan_sebelumnya()

    need = {o["mi"] for o in OBJEK} | {o.get("mi_atap") for o in OBJEK if o.get("mi_atap")}
    mis = {}
    for name in need:
        p = f"{MAT_DIR}/MI_Ep02_{name}"
        mi = EAL.load_asset(p)
        if mi is None:
            fail(f"MI tidak ada: {p}")
        mis[name] = mi
    if problems:
        return

    for o in OBJEK:
        if build_objek(o, mis):
            built_ids.append(o["id"])
    log(f"dibangun {len(built_ids)} objek (target 145)")

    n_ok, cnt, blok = uji()
    test_gang()
    LES.save_current_level()
    log("level disimpan")

    dt = time.time() - t0
    ok = (len(built_ids) == 145 and n_ok == 145 and cnt["hancur"] == 90
          and cnt["penalti_tinggi"] == 61 and cnt["penalti_normal"] == 10 and cnt["tanpa_penalti"] == 19
          and cnt["blok_chaos"] == 32 and cnt["atap_naik"] == 27 and cnt["adikara"] == 11 and cnt["curian"] == 6
          and all(v == 4 for v in blok.values()) and len(blok) == 8)
    log(f"CEK MK4a: objek145={len(built_ids) == 145} alas145={n_ok == 145} "
        f"hancur90={cnt['hancur'] == 90} chaos32={cnt['blok_chaos'] == 32} atap_naik27={cnt['atap_naik'] == 27} "
        f"adikara11={cnt['adikara'] == 11} curian6={cnt['curian'] == 6} -> {'LULUS' if ok else 'GAGAL'}")
    log(f"WAKTU skrip MK4a: {dt:.1f} s")

    if problems:
        unreal.log_warning(f"[MK4a] {len(problems)} masalah:")
        for p in problems:
            unreal.log_warning("  - " + p)


main()
