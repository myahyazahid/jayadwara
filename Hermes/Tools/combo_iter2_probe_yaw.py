"""Ukur putaran badan (yaw) per frame pada satu FBX Mixamo.

Dipakai untuk kasus "tendangan memutar selesai di samping": perlu angka, bukan
perasaan, untuk tahu badan berputar berapa derajat dan berhenti menghadap ke mana.

Jalan:
  blender --background --factory-startup --python Hermes/Tools/combo_iter2_probe_yaw.py -- <file.fbx>

Keluaran: tabel t, yaw garis pinggul (LeftUpLeg-RightUpLeg), yaw dada, yaw kepala.
Satuan derajat, 0 = menghadap seperti frame pertama.
"""
import math
import sys

import bpy


def arg():
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1:]
    return []


def yaw(v):
    return math.degrees(math.atan2(v.y, v.x))


def main():
    a = arg()
    if not a:
        print("[yaw] butuh 1 argumen: <file.fbx>")
        return
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=a[0])

    arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
    fps = bpy.context.scene.render.fps
    act = bpy.data.actions[0]
    f0, f1 = (int(round(x)) for x in act.frame_range)

    pre = ""
    for b in arm.data.bones:
        if b.name.endswith("Hips"):
            pre = b.name[: -len("Hips")]
            break
    pb = arm.pose.bones
    perlu = ["Hips", "Spine2", "Head", "LeftUpLeg", "RightUpLeg", "LeftArm", "RightArm"]
    for n in perlu:
        if pre + n not in pb:
            print("[yaw] tulang hilang:", pre + n)
            return

    scn = bpy.context.scene
    dasar = {}

    def sudut(f):
        scn.frame_set(f)
        bpy.context.view_layer.update()
        mw = arm.matrix_world
        d = {}
        d["bahu"] = yaw((mw @ pb[pre + "LeftArm"].head) - (mw @ pb[pre + "RightArm"].head))
        d["lokal"] = math.degrees(pb[pre + "Hips"].matrix_basis.to_euler().z)
        d["obj"] = math.degrees(arm.rotation_euler.z)
        return d

    dasar = sudut(f0)
    print("[yaw] %s  %.2f s  fps %d  frame %d..%d" % (
        a[0].split("/")[-1], (f1 - f0) / float(fps), fps, f0, f1))
    print("   t     bahu    lokal      obj")
    for f in range(f0, f1 + 1):
        d = sudut(f)
        print("  %5.2f  %7.1f  %5.1f  %6.1f" % (
            (f - f0) / float(fps),
            (d["bahu"] - dasar["bahu"] + 180) % 360 - 180,
            (d["lokal"] - dasar["lokal"] + 180) % 360 - 180,
            (d["obj"] - dasar["obj"] + 180) % 360 - 180))


main()
