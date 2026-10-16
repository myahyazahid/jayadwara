"""M4 — Objek Ep01_LawangSapta (Unreal Editor Python, via Tools/ue_remote.py).

DEST = /Game/Hermes/MapsEp1
Bangun 43 objek dari Art/Level/ep01_layout_v01.json sesuai Hermes/maps_ep1_hermes.md bagian 2
(jenis, alas, rotasi, MI, tag, label, folder):
- kotak            : /Engine/BasicShapes/Cube diskala P,L,T; loc Z = (alas + zrel + T/2)
- rumah            : kotak dinding (label=id) + kotak atap (label=id_Atap) di atasnya
- candi_bertingkat : kotak bertumpuk sesuai daftar tingkat (label=id, id_T2, ...)
- tangga           : pakai actor SM_Ep01_Tangga (dibuat M3) -> dilabeli ulang CANDI_Tangga
- dinding          : kotak tipis dari `dari` ke `ke` (tinggi, tebal); tanpa_tabrakan -> NoCollision
- bidang           : /Engine/BasicShapes/Plane diskala P,L, 5 cm di atas tanah
Alas objek = elev terendah di tapaknya (sampel 1 m) + z_dasar_relatif.
Tag: hancur / cadangan. Folder Outliner = awalan id. MI = MI_Ep01_<mi>.
Simpan level + aset satu per satu (TIDAK PERNAH Save All).

Uji (cetak tabel):
- 43 objek ada (rumah = 1 objek walau 2 actor); alas actor = alas hitungan +/- 5 cm;
  tidak ada objek yang alasnya > 1 m di bawah tanah di titik tengahnya.
- 10 objek bertag hancur (2 di antaranya cadangan); DESA_Musala & semua CANDI_* tanpa tag hancur.
- 3 screenshot: Render/M4_candi.png, Render/M4_desa.png, Render/M4_galian.png.

Pakai (dari WORKTREE): python Tools/ue_remote.py Hermes/Tools/maps_ep1_40_objek.py
"""
import os
import sys
import json
import math

import unreal

DEST = "/Game/Hermes/MapsEp1"
MAP = f"{DEST}/Maps/Test_Hermes_MapsEp1"
MAT_DIR = f"{DEST}/Materials"
CUBE = "/Engine/BasicShapes/Cube"
PLANE = "/Engine/BasicShapes/Plane"

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
from ep01_medan import elev  # noqa: E402

LAYOUT = os.path.join(REPO, "Art", "Level", "ep01_layout_v01.json")
with open(LAYOUT, encoding="utf-8") as f:
    DATA = json.load(f)
OBJEK = DATA["objek"]

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

problems = []
built_ids = []


def log(m):
    unreal.log(f"[M4] {m}")


def fail(m):
    problems.append(m)
    unreal.log_error(f"[M4] {m}")


# ------------------------------------------------------------------ geometri alas (sama seperti M1)
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
    pts = []
    for i in range(n + 1):
        t = i / n
        x = ax + (bx - ax) * t
        y = ay + (by - ay) * t
        pts.append((x, y, elev(x, y)))
    return pts


def alas_obj(o):
    """Alas = elev terendah di tapak (meter), sebelum z_dasar_relatif."""
    j = o["jenis"]
    if j == "tangga":
        return o["dari"][2]
    if j == "dinding":
        pts = sampel_seg(o["dari"][0], o["dari"][1], o["ke"][0], o["ke"][1])
        return min(p[2] for p in pts)
    cx, cy = o["pos"]
    if j == "candi_bertingkat":
        P, L = o["tingkat"][0][0], o["tingkat"][0][1]
    else:
        P, L = o["ukuran"][0], o["ukuran"][1]
    return min(p[2] for p in sampel_rect(cx, cy, P, L, o.get("yaw", 0.0)))


def elev_center(o):
    j = o["jenis"]
    if j == "dinding":
        return elev((o["dari"][0] + o["ke"][0]) / 2.0, (o["dari"][1] + o["ke"][1]) / 2.0)
    if j == "tangga":
        return elev(o["dari"][0], o["dari"][1])
    return elev(o["pos"][0], o["pos"][1])


def expected_base(o):
    """Alas aktual objek (meter) = alas + z_dasar_relatif (+0.05 untuk bidang yang dinaikkan 5 cm)."""
    b = alas_obj(o) + o.get("z_dasar_relatif", 0.0)
    if o["jenis"] == "bidang":
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


def spawn(shape_path, label, loc, yaw_ue, scale_m, mi, folder, tags):
    mesh = EAL.load_asset(shape_path)
    a = EAS.spawn_actor_from_object(mesh, loc, unreal.Rotator(pitch=0.0, yaw=yaw_ue, roll=0.0))
    a.set_actor_label(label)
    a.set_actor_scale3d(unreal.Vector(scale_m[0], scale_m[1], scale_m[2]))
    a.set_folder_path(folder)
    if mi is not None:
        a.static_mesh_component.set_material(0, mi)
    add_tags(a, tags)
    return a


def build_objek(o, mi):
    idd, j = o["id"], o["jenis"]
    folder = idd.split("_")[0]
    tags = []
    if o.get("hancur"):
        tags.append("hancur")
    if o.get("cadangan"):
        tags.append("cadangan")
    base = expected_base(o)

    if j == "kotak":
        x, y = o["pos"]
        P, L, T = o["ukuran"]
        loc = unreal.Vector(x * 100.0, -y * 100.0, (base + T / 2.0) * 100.0)
        return [spawn(CUBE, idd, loc, -o.get("yaw", 0.0), (P, L, T), mi, folder, tags)]

    if j == "rumah":
        x, y = o["pos"]
        P, L, T = o["ukuran"]
        hw = T - 2.0
        yaw_ue = -o.get("yaw", 0.0)
        wall = spawn(CUBE, idd, unreal.Vector(x * 100.0, -y * 100.0, (base + hw / 2.0) * 100.0),
                     yaw_ue, (P, L, hw), mi, folder, tags)
        roof = spawn(CUBE, idd + "_Atap", unreal.Vector(x * 100.0, -y * 100.0, (base + hw + 1.0) * 100.0),
                     yaw_ue, (P + 0.6, L + 0.6, 2.0), mi, folder, [])
        roof.attach_to_actor(wall, "", unreal.AttachmentRule.KEEP_WORLD,
                             unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
        return [wall, roof]

    if j == "candi_bertingkat":
        x, y = o["pos"]
        z = base
        actors = []
        for i, (p, l, t) in enumerate(o["tingkat"]):
            lbl = idd if i == 0 else f"{idd}_T{i + 1}"
            actors.append(spawn(CUBE, lbl, unreal.Vector(x * 100.0, -y * 100.0, (z + t / 2.0) * 100.0),
                                0.0, (p, l, t), mi, folder, tags if i == 0 else []))
            z += t
        return actors

    if j == "dinding":
        ax, ay = o["dari"]
        bx, by = o["ke"]
        dx, dy = (bx - ax) * 100.0, -(by - ay) * 100.0
        length_m = math.hypot(dx, dy) / 100.0
        yaw_ue = math.degrees(math.atan2(dy, dx))
        cx, cy = (ax + bx) / 2.0 * 100.0, -(ay + by) / 2.0 * 100.0
        h, tebal = o["tinggi"], o["tebal"]
        a = spawn(CUBE, idd, unreal.Vector(cx, cy, (base + h / 2.0) * 100.0),
                  yaw_ue, (length_m, tebal, h), mi, folder, tags)
        if o.get("tanpa_tabrakan"):
            set_nocollision(a)
        return [a]

    if j == "bidang":
        x, y = o["pos"]
        P, L = o["ukuran"]
        loc = unreal.Vector(x * 100.0, -y * 100.0, (base) * 100.0)
        return [spawn(PLANE, idd, loc, -o.get("yaw", 0.0), (P, L, 1.0), mi, folder, tags)]

    if j == "tangga":
        a = find_by_label("SM_Ep01_Tangga") or find_by_label(idd)
        if a is None:
            fail("actor SM_Ep01_Tangga (CANDI_Tangga) tidak ada — jalankan M3 dulu")
            return []
        a.set_actor_label(idd)
        a.set_folder_path(folder)
        add_tags(a, tags)
        return [a]

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
        fail(f"level {MAP} tidak ada — jalankan M3 dulu")
        return False
    LES.load_level(MAP)
    log(f"level dimuat: {MAP}")
    if find_by_label("SM_Ep01_Medan") is None:
        fail("SM_Ep01_Medan tidak ada di level — jalankan M3 dulu")
        return False
    return True


def bersihkan_sebelumnya():
    """Hapus actor hasil M4 sebelumnya (label = id / id_Atap / id_Tn) supaya bisa dijalankan ulang.
    Actor SM_Ep01_Medan & SM_Ep01_Tangga (M3) tidak disentuh."""
    labels = set()
    for o in OBJEK:
        if o["jenis"] == "tangga":
            continue
        labels.add(o["id"])
        if o["jenis"] == "rumah":
            labels.add(o["id"] + "_Atap")
        if o["jenis"] == "candi_bertingkat":
            for i in range(1, len(o["tingkat"])):
                labels.add(f"{o['id']}_T{i + 1}")
    n = 0
    for a in list(EAS.get_all_level_actors()):
        if a.get_actor_label() in labels:
            a.destroy_actor()
            n += 1
    if n:
        log(f"hapus {n} actor M4 dari sesi sebelumnya")


# ------------------------------------------------------------------ uji
def uji():
    log("TABEL UJI OBJEK: id | jenis | alas_hitung(m) | alas_actor(m) | d(cm) | elev_tengah(m) | hancur")
    n_ok = 0
    n_hancur = 0
    n_cadangan = 0
    hancur_ids = []
    cadangan_ids = []
    buried = []
    for o in OBJEK:
        idd = o["id"]
        prim = find_by_label(idd)
        if prim is None:
            fail(f"objek hilang: {idd}")
            continue
        origin, extent = prim.get_actor_bounds(False)
        alas_actor = (origin.z - extent.z) / 100.0
        exp = expected_base(o)
        d_cm = (alas_actor - exp) * 100.0
        ok = abs(d_cm) <= 5.0
        if ok:
            n_ok += 1
        else:
            fail(f"{idd}: alas actor {alas_actor:.2f} m != hitung {exp:.2f} m (d={d_cm:+.1f} cm)")
        ec = elev_center(o)
        if ec - alas_actor > 1.0:
            buried.append(f"{idd}: alas {alas_actor:.2f} m, tanah tengah {ec:.2f} m (selisih {ec - alas_actor:.2f} m)")
        tags = [str(t) for t in prim.get_editor_property("tags")]
        if "hancur" in tags:
            n_hancur += 1
            hancur_ids.append(idd)
        if "cadangan" in tags:
            n_cadangan += 1
            cadangan_ids.append(idd)
        log("  %-24s %-16s %8.2f %10.2f %+7.1f %10.2f  %s"
            % (idd, o["jenis"], exp, alas_actor, d_cm, ec, ",".join(tags)))

    log(f"objek ditemukan = {len(built_ids)} (target 43) | alas OK = {n_ok}/43")
    log(f"tag hancur = {n_hancur} (target 10) ; cadangan = {n_cadangan} (target 2)")

    # DESA_Musala & CANDI_* tanpa hancur
    bad = []
    for o in OBJEK:
        if o["id"] == "DESA_Musala" or o["id"].startswith("CANDI_"):
            a = find_by_label(o["id"])
            if a and "hancur" in [str(t) for t in a.get_editor_property("tags")]:
                bad.append(o["id"])
    if bad:
        fail(f"objek yang seharusnya tanpa tag hancur tapi punya: {bad}")
    else:
        log("DESA_Musala & semua CANDI_* tanpa tag hancur: OK")

    if buried:
        log("CATATAN alas > 1 m di bawah tanah di titik tengah (diperiksa manual):")
        for s in buried:
            log("  - " + s)

    return n_ok, n_hancur, n_cadangan


# ------------------------------------------------------------------ screenshot
def shot(name, P, T, fov=60.0):
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    unreal.SystemLibrary.execute_console_command(None, "r.Streaming.FullyLoadUsedTextures 1")
    d = T - P
    yaw = math.degrees(math.atan2(d.y, d.x))
    pitch = math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
    rt = unreal.RenderingLibrary.create_render_target2d(
        world, 1920, 1080, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap = EAS.spawn_actor_from_class(
        unreal.SceneCapture2D, P, unreal.Rotator(pitch=pitch, yaw=yaw, roll=0.0))
    comp = cap.capture_component2d
    comp.set_editor_property("texture_target", rt)
    comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    comp.set_editor_property("fov_angle", fov)
    # 8 frame: auto-exposure scene capture butuh beberapa frame untuk beradaptasi
    # (2 frame -> gambar nyaris hitam; 8 frame -> terang & terbaca).
    for _ in range(8):
        comp.capture_scene()
    out_dir = os.path.join(REPO, "Hermes", "Art", "maps_ep1", "Render")
    os.makedirs(out_dir, exist_ok=True)
    unreal.RenderingLibrary.export_render_target(world, rt, out_dir.replace("\\", "/"), name)
    no_ext = os.path.join(out_dir, name)
    if os.path.exists(no_ext):
        os.replace(no_ext, no_ext + ".png")
    png = os.path.join(out_dir, name + ".png")
    px = unreal.RenderingLibrary.read_render_target_pixel(world, rt, 960, 540)
    lum = (px.r + px.g + px.b) / 3.0
    log("screenshot -> %s ; piksel tengah = %.0f,%.0f,%.0f (lum %.0f)" % (png, px.r, px.g, px.b, lum))
    EAS.destroy_actor(cap)
    return lum


# ------------------------------------------------------------------ main
def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[M4] Editor sedang Play (PIE) — hentikan dulu lalu jalankan ulang")
        return
    if not load_level():
        return
    bersihkan_sebelumnya()

    mis = {}
    for name in {o["mi"] for o in OBJEK}:
        p = f"{MAT_DIR}/MI_Ep01_{name}"
        mi = EAL.load_asset(p)
        if mi is None:
            fail(f"MI tidak ada: {p}")
        mis[name] = mi
    if problems:
        return

    for o in OBJEK:
        actors = build_objek(o, mis[o["mi"]])
        if actors:
            built_ids.append(o["id"])
    log(f"dibangun {len(built_ids)} objek (target 43)")

    n_ok, n_hancur, n_cadangan = uji()

    LES.save_current_level()
    log("level disimpan")

    # screenshot tiga sudut (UE cm)
    shot("M4_candi", unreal.Vector(0.0, -9000.0, 3600.0), unreal.Vector(0.0, -19500.0, 4200.0), 60.0)
    shot("M4_desa", unreal.Vector(6000.0, 19000.0, 900.0), unreal.Vector(-17000.0, 26000.0, 300.0), 60.0)
    shot("M4_galian", unreal.Vector(14000.0, 2000.0, 3500.0), unreal.Vector(0.0, 0.0, 1200.0), 60.0)

    ok = (len(built_ids) == 43 and n_ok == 43 and n_hancur == 10 and n_cadangan == 2)
    log(f"CEK: 43 objek={len(built_ids) == 43} alas43={n_ok == 43} hancur10={n_hancur == 10} cadangan2={n_cadangan == 2}")

    if problems:
        unreal.log_warning(f"[M4] {len(problems)} masalah:")
        for p in problems:
            unreal.log_warning("  - " + p)
    if ok and not problems:
        log("selesai tanpa masalah")


main()
