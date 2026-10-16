"""V4 — Objek + pohon + tiang v02 (Unreal Editor Python, via Tools/ue_remote.py).

DEST = /Game/Hermes/MapsEp1
Bangun 88 objek dari Art/Level/ep01_layout_v02.json + 6 actor pohon + 1 actor tiang:
- kotak            : /Engine/BasicShapes/Cube diskala P,L,T; loc Z = (alas + T/2)
- rumah            : dinding + atap (2 actor)
- candi_bertingkat : kotak bertumpuk
- tangga           : pakai actor SM_Ep01_Tangga_v02 (dari V3) -> dilabeli CANDI_Tangga
- dinding          : kotak tipis dari `dari` ke `ke`; tanpa_tabrakan -> NoCollision
- bidang           : /Engine/BasicShapes/Plane
- kerucut (baru)   : /Engine/BasicShapes/Cone diskala [diameter, diameter, tinggi], alas di `z`
Alas objek = elev terendah di tapak (sampel 1 m) + z_dasar_relatif; objek ber-`z` = `z` ABSOLUT.
Tag: hancur / cadangan / adikara (`"milik":"Adikara"` -> tag `adikara`, hancur tanpa penalti).
Pohon (6 kelompok) = 1 actor `POHON_<Kelompok>` (folder POHON) berisi 2 InstancedStaticMeshComponent:
  Batang (Cylinder Ø0,6x8 m, MI Kayu, BlockAll) & Tajuk (Cone Ø7x9 m, alas 6 m di atas tanah, MI Hutan, NoCollision).
  Tiap titik [x,y,s]: ukuran x s, alas = elev(x,y). Tiang listrik = 1 actor `TIANG_Listrik` (ISM silinder Ø0,3x9 m, MI Kendaraan, BlockAll).
Simpan level + aset satu per satu (TIDAK PERNAH Save All).

Uji (cetak tabel):
- 88 objek ada; alas actor = alas hitungan +/- 5 cm (z absolut: = z +/- 5 cm).
- tag hancur = 30 (adikara = 20, cadangan = 2); DESA_Musala / CANDI_* / DESA_RumahLatar* tanpa hancur.
- instance pohon = 775 (batang = tajuk), tiang = 30. 4 screenshot.

Pakai (dari WORKTREE, editor worktree terbuka): python Tools/ue_remote.py Hermes/Tools/maps_ep1_v02_40_objek.py
"""
import os
import sys
import json
import math

import unreal

DEST = "/Game/Hermes/MapsEp1"
MAP = f"{DEST}/Maps/Test_Hermes_MapsEp1_v02"
MAT_DIR = f"{DEST}/Materials"
CUBE = "/Engine/BasicShapes/Cube"
PLANE = "/Engine/BasicShapes/Plane"
CONE = "/Engine/BasicShapes/Cone"
CYLINDER = "/Engine/BasicShapes/Cylinder"

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
import ep01_medan_v02 as M  # noqa: E402  (v02)

with open(os.path.join(REPO, "Art", "Level", "ep01_layout_v02.json"), encoding="utf-8") as f:
    DATA = json.load(f)
OBJEK = DATA["objek"]
POHON = DATA["pohon_kelompok"]
POHON_BENTUK = DATA["pohon_bentuk"]
TIANG = DATA["tiang_listrik"]

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)

problems = []
built_ids = []


def log(m):
    unreal.log(f"[V4] {m}")


def fail(m):
    problems.append(m)
    unreal.log_error(f"[V4] {m}")


def elev(x, y):
    return M.elev(x, y)


def bottom_local(mesh):
    """Z dasar mesh lokal (unit UE) relatif pivot: -50 (pivot tengah) / 0 (pivot alas)."""
    b = mesh.get_bounds()
    return b.origin.z - b.box_extent.z


# ------------------------------------------------------------------ geometri alas (sama seperti M1/M4 v01)
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
    """Alas (meter). Objek ber-`z` = z ABSOLUT; lainnya = elev terendah di tapak."""
    if "z" in o:
        return float(o["z"])
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


def tags_for(o):
    tags = []
    if o.get("hancur"):
        tags.append("hancur")
    if o.get("cadangan"):
        tags.append("cadangan")
    if o.get("milik") == "Adikara":
        tags.append("adikara")
    return tags


def build_objek(o, mi):
    idd, j = o["id"], o["jenis"]
    folder = idd.split("_")[0]
    tags = tags_for(o)
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

    if j == "kerucut":
        x, y = o["pos"]
        d1, d2, t = o["ukuran"]
        loc = unreal.Vector(x * 100.0, -y * 100.0, base * 100.0 - bottom_local(EAL.load_asset(CONE)) * t)
        a = spawn(CONE, idd, loc, -o.get("yaw", 0.0), (d1, d2, t), mi, folder, tags)
        if o.get("tanpa_tabrakan"):
            set_nocollision(a)
        return [a]

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
        loc = unreal.Vector(x * 100.0, -y * 100.0, base * 100.0)
        return [spawn(PLANE, idd, loc, -o.get("yaw", 0.0), (P, L, 1.0), mi, folder, tags)]

    if j == "tangga":
        a = find_by_label("SM_Ep01_Tangga_v02") or find_by_label(idd)
        if a is None:
            fail("actor SM_Ep01_Tangga_v02 (CANDI_Tangga) tidak ada — jalankan V3 dulu")
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


# ------------------------------------------------------------------ pohon & tiang (InstancedStaticMesh)
def new_ism(actor, root, nama, mesh, mi, collision):
    params = unreal.AddNewSubobjectParams()
    params.set_editor_property("parent_handle", root)
    params.set_editor_property("new_class", unreal.InstancedStaticMeshComponent)
    h, msg = SDS.add_new_subobject(params)
    if str(msg):
        fail(f"ISM {nama} pada {actor.get_actor_label()}: {msg}")
    SDS.rename_subobject(h, nama)
    comp = next((c for c in actor.get_components_by_class(unreal.InstancedStaticMeshComponent)
                 if c.get_name() == nama), None)
    if comp is None:
        fail(f"ISM {nama} tidak ditemukan di {actor.get_actor_label()}")
        return None
    comp.set_static_mesh(mesh)
    if mi is not None:
        comp.set_material(0, mi)
    try:
        comp.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    except Exception:  # noqa: BLE001
        pass
    if collision:
        comp.set_collision_profile_name("BlockAll")
    else:
        comp.set_collision_profile_name("NoCollision")
    return comp


def build_pohon(mis):
    batang_b, tajuk_b = POHON_BENTUK["batang"], POHON_BENTUK["tajuk"]
    mesh_b, mesh_t = EAL.load_asset(CYLINDER), EAL.load_asset(CONE)
    zb, zt = bottom_local(mesh_b), bottom_local(mesh_t)
    total_b = total_t = 0
    for grup, titik in POHON.items():
        a = EAS.spawn_actor_from_class(unreal.Actor, unreal.Vector(0.0, 0.0, 0.0))
        a.set_actor_label(f"POHON_{grup}")
        a.set_folder_path("POHON")
        root = SDS.k2_gather_subobject_data_for_instance(a)[0]
        cb = new_ism(a, root, "Batang", mesh_b, mis[batang_b["mi"]], True)
        ct = new_ism(a, root, "Tajuk", mesh_t, mis[tajuk_b["mi"]], False)
        if cb is None or ct is None:
            continue
        for (x, y, s) in titik:
            e = elev(x, y)
            tb = batang_b["tinggi"] * s
            tt = tajuk_b["tinggi"] * s
            cb.add_instance(unreal.Transform(
                location=unreal.Vector(x * 100.0, -y * 100.0, e * 100.0 - zb * tb),
                scale=unreal.Vector(batang_b["diameter"] * s, batang_b["diameter"] * s, tb)))
            ct.add_instance(unreal.Transform(
                location=unreal.Vector(x * 100.0, -y * 100.0, (e + tajuk_b["z_relatif"]) * 100.0 - zt * tt),
                scale=unreal.Vector(tajuk_b["diameter"] * s, tajuk_b["diameter"] * s, tt)))
        total_b += cb.get_instance_count()
        total_t += ct.get_instance_count()
    log(f"pohon: 6 actor, instance batang = {total_b}, tajuk = {total_t} (target 775)")
    return total_b, total_t


def build_tiang(mis):
    mesh = EAL.load_asset(CYLINDER)
    z = bottom_local(mesh)
    a = EAS.spawn_actor_from_class(unreal.Actor, unreal.Vector(0.0, 0.0, 0.0))
    a.set_actor_label("TIANG_Listrik")
    a.set_folder_path("TIANG")
    root = SDS.k2_gather_subobject_data_for_instance(a)[0]
    c = new_ism(a, root, "Tiang", mesh, mis[TIANG["mi"]], True)
    if c is None:
        return 0
    h = TIANG["tinggi"]
    for (x, y) in TIANG["titik"]:
        e = elev(x, y)
        c.add_instance(unreal.Transform(
            location=unreal.Vector(x * 100.0, -y * 100.0, e * 100.0 - z * h),
            scale=unreal.Vector(TIANG["diameter"], TIANG["diameter"], h)))
    n = c.get_instance_count()
    log(f"tiang: 1 actor, instance = {n} (target 30)")
    return n


# ------------------------------------------------------------------ level & pembersihan
def load_level():
    if not EAL.does_asset_exist(MAP):
        fail(f"level {MAP} tidak ada — jalankan V3 dulu")
        return False
    LES.load_level(MAP)
    log(f"level dimuat: {MAP}")
    if find_by_label("SM_Ep01_Medan_v02") is None:
        fail("SM_Ep01_Medan_v02 tidak ada di level — jalankan V3 dulu")
        return False
    return True


def bersihkan_sebelumnya():
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
    labels.add("TIANG_Listrik")
    for grup in POHON:
        labels.add(f"POHON_{grup}")
    n = 0
    for a in list(EAS.get_all_level_actors()):
        if a.get_actor_label() in labels:
            a.destroy_actor()
            n += 1
    if n:
        log(f"hapus {n} actor V4 dari sesi sebelumnya")


# ------------------------------------------------------------------ uji
def uji():
    log("TABEL UJI OBJEK: id | jenis | alas_hitung(m) | alas_actor(m) | d(cm) | elev_tengah(m) | tag")
    n_ok = n_hancur = n_adikara = n_cadangan = 0
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
        if ec - alas_actor > 1.0 and "z" not in o:
            buried.append(f"{idd}: alas {alas_actor:.2f} m, tanah tengah {ec:.2f} m (selisih {ec - alas_actor:.2f} m)")
        tags = [str(t) for t in prim.get_editor_property("tags")]
        if "hancur" in tags:
            n_hancur += 1
        if "adikara" in tags:
            n_adikara += 1
        if "cadangan" in tags:
            n_cadangan += 1
        log("  %-24s %-16s %8.2f %10.2f %+7.1f %10.2f  %s"
            % (idd, o["jenis"], exp, alas_actor, d_cm, ec, ",".join(tags)))

    log(f"objek ditemukan = {len(built_ids)} (target 88) | alas OK = {n_ok}/88")
    log(f"tag hancur = {n_hancur} (target 30) ; adikara = {n_adikara} (target 20) ; cadangan = {n_cadangan} (target 2)")

    bad = []
    for o in OBJEK:
        if o["id"] == "DESA_Musala" or o["id"].startswith("CANDI_") or o["id"].startswith("DESA_RumahLatar"):
            a = find_by_label(o["id"])
            if a and "hancur" in [str(t) for t in a.get_editor_property("tags")]:
                bad.append(o["id"])
    if bad:
        fail(f"objek yang seharusnya tanpa tag hancur tapi punya: {bad}")
    else:
        log("DESA_Musala, CANDI_*, DESA_RumahLatar* tanpa tag hancur: OK")

    if buried:
        log("CATATAN alas > 1 m di bawah tanah di titik tengah (diperiksa manual):")
        for s in buried:
            log("  - " + s)
    return n_ok, n_hancur, n_adikara, n_cadangan


def hitung_instance():
    nb = nt = ntiang = 0
    for a in EAS.get_all_level_actors():
        lbl = a.get_actor_label()
        if lbl.startswith("POHON_"):
            for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
                if c.get_name() == "Batang":
                    nb += c.get_instance_count()
                elif c.get_name() == "Tajuk":
                    nt += c.get_instance_count()
        elif lbl == "TIANG_Listrik":
            for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
                ntiang += c.get_instance_count()
    return nb, nt, ntiang


# ------------------------------------------------------------------ main
def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[V4] Editor sedang Play (PIE) — hentikan dulu lalu jalankan ulang")
        return
    if not load_level():
        return
    bersihkan_sebelumnya()

    mis = {}
    for name in {o["mi"] for o in OBJEK} | {POHON_BENTUK["batang"]["mi"], POHON_BENTUK["tajuk"]["mi"], TIANG["mi"]}:
        p = f"{MAT_DIR}/MI_Ep01_{name}"
        mi = EAL.load_asset(p)
        if mi is None:
            fail(f"MI tidak ada: {p}")
        mis[name] = mi
    if problems:
        return

    log("pivot mesh (z dasar lokal): cone=%.1f cylinder=%.1f cube=%.1f" % (
        bottom_local(EAL.load_asset(CONE)), bottom_local(EAL.load_asset(CYLINDER)), bottom_local(EAL.load_asset(CUBE))))

    for o in OBJEK:
        actors = build_objek(o, mis[o["mi"]])
        if actors:
            built_ids.append(o["id"])
    log(f"dibangun {len(built_ids)} objek (target 88)")

    nb, nt = build_pohon(mis)
    ntiang = build_tiang(mis)

    n_ok, n_hancur, n_adikara, n_cadangan = uji()

    LES.save_current_level()
    log("level disimpan")

    # screenshot V4 (4 sudut) dibuat oleh Hermes/Tools/maps_ep1_v02_41_shot.py pada invokasi terpisah:
    # render SceneCapture di invokasi yang sama dengan load_level menghasilkan gambar gelap.

    # verifikasi persistensi: muat ulang level, hitung lagi
    LES.load_level(MAP)
    nb2, nt2, ntiang2 = hitung_instance()
    log(f"setelah muat ulang: instance batang = {nb2}, tajuk = {nt2}, tiang = {ntiang2}")

    ok = (len(built_ids) == 88 and n_ok == 88 and n_hancur == 30 and n_adikara == 20
          and n_cadangan == 2 and nb == 775 and nt == 775 and ntiang == 30)
    log(f"CEK V4: objek88={len(built_ids) == 88} alas88={n_ok == 88} hancur30={n_hancur == 30} "
        f"adikara20={n_adikara == 20} cadangan2={n_cadangan == 2} pohon775={nb == 775 and nt == 775} "
        f"tiang30={ntiang == 30} persist={nb2 == 775 and ntiang2 == 30} -> {'LULUS' if ok else 'GAGAL'}")

    if problems:
        unreal.log_warning(f"[V4] {len(problems)} masalah:")
        for p in problems:
            unreal.log_warning("  - " + p)


main()
