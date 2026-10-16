"""MK4b — Kelompok ISM + pohon + tiang (Unreal Editor Python, via Tools/ue_remote.py).

DEST = /Game/Hermes/MapsEp2  (sandbox Hermes)
Bangun dari Art/Level/ep02_layout_v02.json:
- 8 kelompok instanced (1.817 item): 1 actor per kelompok (label = id, folder = awalan id), berisi ISM.
  `bentuk` "rumah" -> 2 ISM: Dinding (P x L x (T-0,5), `mi`) + Atap ((P+0,4) x (L+0,4) x 0,5, `mi_atap`).
  `bentuk` "kotak" -> 1 ISM Cube P x L x T. `z` kelompok = alas absolut semua item; tanpa `z` alas
  otomatis per item (elev terendah di tapak). Collision ISM BlockAll.
- 5 kelompok pohon (258 batang = 258 tajuk): 1 actor POHON_<Kelompok> dengan 2 ISM (Batang Cylinder
  diameter 0,5 x 7 m, `mi` Kayu, BlockAll; Tajuk Cone diameter 7 x 8 m alas 5 m di atas tanah, NoCollision).
- 1 actor TIANG_Listrik: ISM Cylinder diameter 0,3 x 9 m, `mi` Kendaraan, BlockAll.

Tiap skrip menghapus actor buatannya dulu (cari per label) sebelum membangun ulang.
Uji (cetak tabel): jumlah instance per kelompok (= jumlah item; rumah Dinding = Atap), total 1.817,
258 batang = 258 tajuk, 55 tiang, waktu skrip.

Pakai (dari WORKTREE, editor worktree terbuka):
  python Tools/ue_remote.py Hermes/Tools/maps_ep2_41_kelompok.py
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
CONE = "/Engine/BasicShapes/Cone"
CYLINDER = "/Engine/BasicShapes/Cylinder"

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "Art", "Level"))
import ep02_medan_v02 as M  # noqa: E402

with open(os.path.join(REPO, "Art", "Level", "ep02_layout_v02.json"), encoding="utf-8") as f:
    DATA = json.load(f)
KELOMPOK = DATA["kelompok"]
POHON = DATA["pohon_kelompok"]
POHON_BENTUK = DATA["pohon_bentuk"]
TIANG = DATA["tiang_listrik"]

EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)

problems = []


def log(m):
    unreal.log(f"[MK4b] {m}")


def fail(m):
    problems.append(m)
    unreal.log_error(f"[MK4b] {m}")


def elev(x, y):
    return M.elev(x, y)


def bottom_local(mesh):
    b = mesh.get_bounds()
    return b.origin.z - b.box_extent.z


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


def alas_rect(cx, cy, P, L, yaw_deg, step=1.0):
    hx, hy = P / 2.0, L / 2.0
    lo = None
    for u in frange(-hx, hx, step):
        for v in frange(-hy, hy, step):
            wx, wy = rot_pt(cx, cy, u, v, yaw_deg)
            z = elev(wx, wy)
            lo = z if lo is None else min(lo, z)
    return lo


def add_tags(actor, tags):
    if not tags:
        return
    try:
        actor.set_editor_property("tags", [unreal.Name(t) for t in tags])
    except Exception as e:  # noqa: BLE001
        fail(f"tag {tags} gagal pada {actor.get_actor_label()}: {e}")


def tags_kelompok(k):
    tags = []
    if k.get("hancur"):
        tags.append("hancur")
    p = k.get("penalti")
    if p == "tinggi":
        tags.append("penalti_tinggi")
    elif p == "normal":
        tags.append("penalti_normal")
    elif p == "tanpa":
        tags.append("tanpa_penalti")
    if k.get("tukar_puing"):
        tags.append("tukar_puing")
    if k.get("milik") == "Adikara":
        tags.append("adikara")
    return tags


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
    comp.set_collision_profile_name("BlockAll" if collision else "NoCollision")
    return comp


def build_kelompok(k, mis):
    idd, bentuk = k["id"], k["bentuk"]
    folder = idd.split("_")[0]
    z_abs = k.get("z")
    a = EAS.spawn_actor_from_class(unreal.Actor, unreal.Vector(0.0, 0.0, 0.0))
    a.set_actor_label(idd)
    a.set_folder_path(folder)
    add_tags(a, tags_kelompok(k))
    root = SDS.k2_gather_subobject_data_for_instance(a)[0]
    mesh = EAL.load_asset(CUBE)
    n_d = n_a = 0
    if bentuk == "rumah":
        cd = new_ism(a, root, "Dinding", mesh, mis[k["mi"]], True)
        ca = new_ism(a, root, "Atap", mesh, mis[k["mi_atap"]], True)
        if cd is None or ca is None:
            return 0, 0, 0
        for (x, y, P, L, T, yaw) in k["item"]:
            base = z_abs if z_abs is not None else alas_rect(x, y, P, L, yaw)
            hw = T - 0.5
            cd.add_instance(unreal.Transform(
                location=unreal.Vector(x * 100.0, -y * 100.0, (base + hw / 2.0) * 100.0),
                rotation=unreal.Rotator(yaw=-yaw),
                scale=unreal.Vector(P, L, hw)))
            ca.add_instance(unreal.Transform(
                location=unreal.Vector(x * 100.0, -y * 100.0, (base + hw + 0.25) * 100.0),
                rotation=unreal.Rotator(yaw=-yaw),
                scale=unreal.Vector(P + 0.4, L + 0.4, 0.5)))
        n_d, n_a = cd.get_instance_count(), ca.get_instance_count()
    else:
        c = new_ism(a, root, "Badan", mesh, mis[k["mi"]], True)
        if c is None:
            return 0, 0, 0
        for (x, y, P, L, T, yaw) in k["item"]:
            base = z_abs if z_abs is not None else alas_rect(x, y, P, L, yaw)
            c.add_instance(unreal.Transform(
                location=unreal.Vector(x * 100.0, -y * 100.0, (base + T / 2.0) * 100.0),
                rotation=unreal.Rotator(yaw=-yaw),
                scale=unreal.Vector(P, L, T)))
        n_d = c.get_instance_count()
    return len(k["item"]), n_d, n_a


def build_pohon(mis):
    bb, tb = POHON_BENTUK["batang"], POHON_BENTUK["tajuk"]
    mesh_b, mesh_t = EAL.load_asset(CYLINDER), EAL.load_asset(CONE)
    zb, zt = bottom_local(mesh_b), bottom_local(mesh_t)
    total_b = total_t = 0
    for grup, titik in POHON.items():
        a = EAS.spawn_actor_from_class(unreal.Actor, unreal.Vector(0.0, 0.0, 0.0))
        a.set_actor_label(f"POHON_{grup}")
        a.set_folder_path("POHON")
        root = SDS.k2_gather_subobject_data_for_instance(a)[0]
        cb = new_ism(a, root, "Batang", mesh_b, mis[bb["mi"]], True)
        ct = new_ism(a, root, "Tajuk", mesh_t, mis[tb["mi"]], False)
        if cb is None or ct is None:
            continue
        for (x, y, s) in titik:
            e = elev(x, y)
            hb = bb["tinggi"] * s
            ht = tb["tinggi"] * s
            cb.add_instance(unreal.Transform(
                location=unreal.Vector(x * 100.0, -y * 100.0, e * 100.0 - zb * hb),
                scale=unreal.Vector(bb["diameter"] * s, bb["diameter"] * s, hb)))
            ct.add_instance(unreal.Transform(
                location=unreal.Vector(x * 100.0, -y * 100.0, (e + tb["z_relatif"]) * 100.0 - zt * ht),
                scale=unreal.Vector(tb["diameter"] * s, tb["diameter"] * s, ht)))
        total_b += cb.get_instance_count()
        total_t += ct.get_instance_count()
    log(f"pohon: {len(POHON)} actor, instance batang = {total_b}, tajuk = {total_t} (target 258/258)")
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
    log(f"tiang: 1 actor, instance = {n} (target 55)")
    return n


def load_level():
    if not EAL.does_asset_exist(MAP):
        fail(f"level {MAP} tidak ada — jalankan MK3 dulu")
        return False
    LES.load_level(MAP)
    log(f"level dimuat: {MAP}")
    if next((a for a in EAS.get_all_level_actors() if a.get_actor_label() == "SM_Ep02_Medan"), None) is None:
        fail("SM_Ep02_Medan tidak ada di level — jalankan MK3 dulu")
        return False
    return True


def bersihkan_sebelumnya():
    labels = {k["id"] for k in KELOMPOK} | {f"POHON_{g}" for g in POHON} | {"TIANG_Listrik"}
    n = 0
    for a in list(EAS.get_all_level_actors()):
        if a.get_actor_label() in labels:
            a.destroy_actor()
            n += 1
    if n:
        log(f"hapus {n} actor MK4b dari sesi sebelumnya")


def uji_kelompok():
    log("TABEL KELOMPOK: id | bentuk | n_item | n_Dinding | n_Atap | tag")
    total = 0
    rows = []
    for k in KELOMPOK:
        a = next((x for x in EAS.get_all_level_actors() if x.get_actor_label() == k["id"]), None)
        if a is None:
            fail(f"kelompok hilang: {k['id']}")
            continue
        n_d = n_a = 0
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            if c.get_name() in ("Dinding", "Badan"):
                n_d = c.get_instance_count()
            elif c.get_name() == "Atap":
                n_a = c.get_instance_count()
        n_item = len(k["item"])
        total += n_item
        tags = [str(t) for t in a.get_editor_property("tags")]
        rows.append((k["id"], k["bentuk"], n_item, n_d, n_a, ",".join(tags)))
        log("  %-20s %-6s %6d %10d %8d  %s" % (k["id"], k["bentuk"], n_item, n_d, n_a, ",".join(tags)))
        if n_d != n_item:
            fail(f"{k['id']}: instance {n_d} != item {n_item}")
        if k["bentuk"] == "rumah" and n_a != n_item:
            fail(f"{k['id']}: Atap {n_a} != Dinding {n_d}")
    log(f"kelompok: {len(rows)} actor, total item = {total} (target 8 actor / 1.817 item)")
    return total


def hitung_pohon_tiang():
    nb = nt = ntiang = n_act_p = 0
    for a in EAS.get_all_level_actors():
        lbl = a.get_actor_label()
        if lbl.startswith("POHON_"):
            n_act_p += 1
            for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
                if c.get_name() == "Batang":
                    nb += c.get_instance_count()
                elif c.get_name() == "Tajuk":
                    nt += c.get_instance_count()
        elif lbl == "TIANG_Listrik":
            for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
                ntiang += c.get_instance_count()
    log(f"pohon: {n_act_p} actor, batang = {nb}, tajuk = {nt} (target 5 / 258 / 258)")
    log(f"tiang: 1 actor, instance = {ntiang} (target 55)")
    return n_act_p, nb, nt, ntiang


def main():
    if unreal.EditorLevelLibrary.get_pie_worlds(False):
        unreal.log_error("[MK4b] Editor sedang Play (PIE) — hentikan dulu lalu jalankan ulang")
        return
    t0 = time.time()
    if not load_level():
        return
    bersihkan_sebelumnya()

    need = {k["mi"] for k in KELOMPOK} | {k.get("mi_atap") for k in KELOMPOK if k.get("mi_atap")} \
        | {POHON_BENTUK["batang"]["mi"], POHON_BENTUK["tajuk"]["mi"], TIANG["mi"]}
    mis = {}
    for name in need:
        p = f"{MAT_DIR}/MI_Ep02_{name}"
        mi = EAL.load_asset(p)
        if mi is None:
            fail(f"MI tidak ada: {p}")
        mis[name] = mi
    if problems:
        return

    for k in KELOMPOK:
        build_kelompok(k, mis)
    total_item = uji_kelompok()
    build_pohon(mis)
    build_tiang(mis)
    n_act_p, nb, nt, ntiang = hitung_pohon_tiang()

    LES.save_current_level()
    log("level disimpan")

    dt = time.time() - t0
    ok = (total_item == 1817 and n_act_p == 5 and nb == 258 and nt == 258 and ntiang == 55)
    log(f"CEK MK4b: item1817={total_item == 1817} pohon5={n_act_p == 5} batang258={nb == 258} "
        f"tajuk258={nt == 258} tiang55={ntiang == 55} -> {'LULUS' if ok else 'GAGAL'}")
    log(f"WAKTU skrip MK4b: {dt:.1f} s")

    if problems:
        unreal.log_warning(f"[MK4b] {len(problems)} masalah:")
        for p in problems:
            unreal.log_warning("  - " + p)


main()
