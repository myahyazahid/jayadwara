"""Aksa2 — render tiap morph wajah (nilai 1) dari depan dan 3/4, lalu lembar kontak (butuh Pillow di Python sistem).

  blender --background --factory-startup --python Art/Scripts/aksa2_41_render_morphs.py -- <outdir> [blend] [morph,morph...]
  python -I Art/Scripts/aksa2_41_render_morphs.py --sheet <outdir>        (menyusun lembar kontak dari PNG hasil render)
Default blend: Art/Blender/aksa2/aksa2_v07_morph.blend. Pose rest (modifier armature dimatikan), cahaya & kamera tetap supaya dapat dibandingkan.
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1].parent
NAMES = ["netral", "ak_blink_L", "ak_blink_R", "ak_smile", "ak_angry", "ak_mouth_open", "ak_brow_up", "ak_wince", "ak_sad"]


def render():
    import bpy
    argv = sys.argv[sys.argv.index("--") + 1:]
    out = Path(argv[0])
    out.mkdir(parents=True, exist_ok=True)
    blend = Path(argv[1]) if len(argv) > 1 and argv[1] != "-" else ROOT / "Art" / "Blender" / "aksa2" / "aksa2_v07_morph.blend"
    only = argv[2].split(",") if len(argv) > 2 and argv[2] != "-" else NAMES
    fx, fz, fs = (float(a) for a in argv[3].split(",")) if len(argv) > 3 else (0.0, 1.625, 0.17)   # pusat x,z dan lebar kanvas (m)
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    ob = bpy.data.objects["AK2_Source"]
    sc = bpy.context.scene
    for o in bpy.data.objects:
        if o.type in {"EMPTY", "ARMATURE"}:
            o.hide_render = True
    for m in ob.modifiers:
        if m.type == "ARMATURE":
            m.show_render = m.show_viewport = False
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0.9, 0.92, 0.95, 1)
    bg.inputs["Strength"].default_value = 1.1
    for name, rot, e in (("key", (65, 0, -25), 2.6), ("fill", (75, 0, 50), 0.9)):
        d = bpy.data.lights.new(name, "SUN")
        d.energy = e
        o = bpy.data.objects.new(name, d)
        sc.collection.objects.link(o)
        o.rotation_euler = tuple(math.radians(a) for a in rot)
    ids = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    sc.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in ids else "BLENDER_EEVEE_NEXT"
    sc.view_settings.view_transform = "Standard"
    cd = bpy.data.cameras.new("c")
    cd.type = "ORTHO"
    cd.ortho_scale = fs
    cam = bpy.data.objects.new("c", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    sc.render.resolution_x = sc.render.resolution_y = 560
    keys = ob.data.shape_keys.key_blocks if ob.data.shape_keys else []
    focus = (fx, -0.02, fz)
    views = {"depan": 0.0, "q34": 38.0}
    for name in only:
        for kb in list(keys)[1:]:
            kb.value = 1.0 if kb.name == name else 0.0
        for vn, ang in views.items():
            a = math.radians(ang)
            cam.location = (focus[0] - math.sin(a) * 1.0, focus[1] - math.cos(a) * 1.0, focus[2])
            cam.rotation_euler = (math.radians(90), 0, -a)
            sc.render.filepath = str(out / f"{name}_{vn}.png")
            bpy.ops.render.render(write_still=True)
    print("render selesai ->", out)


def sheet(out):
    from PIL import Image, ImageDraw
    out = Path(out)
    cols = 5
    names = [n for n in NAMES if (out / f"{n}_depan.png").exists()]
    for vn in ("depan", "q34"):
        ims = [Image.open(out / f"{n}_{vn}.png").convert("RGB") for n in names]
        w, h = ims[0].size
        rows = math.ceil(len(ims) / cols)
        S = Image.new("RGB", (cols * w, rows * h), (255, 255, 255))
        for i, (n, im) in enumerate(zip(names, ims)):
            S.paste(im, ((i % cols) * w, (i // cols) * h))
            ImageDraw.Draw(S).text(((i % cols) * w + 6, (i // cols) * h + 6), n, fill=(200, 0, 0))
        S.save(out / f"sheet_{vn}.png")
        print("lembar:", out / f"sheet_{vn}.png")


if "--sheet" in sys.argv:
    sheet(sys.argv[sys.argv.index("--sheet") + 1])
elif "--" in sys.argv:
    render()
