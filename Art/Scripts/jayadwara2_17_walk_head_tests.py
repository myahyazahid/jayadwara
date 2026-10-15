"""Jayadwara2 R3c — uji pose tambahan dari bug nyata Play (13 Okt 2026): LANGKAH JALAN (paha ±28°, lutut menekuk) lalu KEPALA MIRING BESAR (±36°).
  blender --background Art/Blender/jayadwara2/jayadwara2_v05_rig_r3.blend --python Art/Scripts/jayadwara2_17_walk_head_tests.py -- <tag>
Keluaran: Art/Export/_jd2/_walk_<tag>_{samping,belakang34,depan34}.png dan _tilt_<tag>_{samping,depan34}.png.
Periksa: sayap/kain pecah jadi serpihan? paha berlubang? dagu/leher tertinggal? (bug yang lolos dari 13 pose uji)."""
import bpy, math, sys
from mathutils import Matrix, Vector
tag = sys.argv[sys.argv.index("--") + 1]
arm = bpy.data.objects["JD2_Armature"]; sc = bpy.context.scene
sc.frame_set(1)
def rot(bone, axis, deg):          # rotasi di sekitar head tulang, sumbu dunia
    pb = arm.pose.bones[bone]; h = pb.head.copy()
    pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(math.radians(deg), 4, axis) @ Matrix.Translation(-h) @ pb.matrix
    bpy.context.view_layer.update()
# Karakter menghadap -Y; paha maju = rotasi sekitar X negatif? (kaki ke -Y). Langkah: kiri maju 28Â°, kanan mundur 18Â°; lutut kanan menekuk
rot("thigh_l", "X", -28); rot("calf_l", "X", 6)
rot("thigh_r", "X", 18);  rot("calf_r", "X", 30)
rot("upperarm_l", "X", 22); rot("upperarm_r", "X", -22)
sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "FLAT"; sh.color_type = "TEXTURE"
sc.view_settings.view_transform = "Standard"; sc.world = sc.world or bpy.data.worlds.new("w"); sc.world.color = (0.45, 0.5, 0.55)
for o in bpy.data.objects:
    if o.type in {"ARMATURE", "EMPTY"}: o.hide_render = True
cd = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
cd.type = "ORTHO"; cd.ortho_scale = 1.45
sc.render.resolution_x, sc.render.resolution_y = 800, 900
for name, loc in (("samping", (6, 0, 0.9)), ("belakang34", (3.2, 4.5, 1.1)), ("depan34", (-3.2, -4.5, 1.1))):
    cam.location = Vector(loc); cam.rotation_euler = (Vector((0, 0, 0.9)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = f"C:/repository/unreal_engine/jayadwara/Art/Export/_jd2/_walk_{tag}_{name}.png"; bpy.ops.render.render(write_still=True)


# ---------------------------------------------------------------- kepala miring (scene dimuat ulang)
bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)
import bpy, math, sys
from mathutils import Matrix, Vector
arm = bpy.data.objects["JD2_Armature"]; sc = bpy.context.scene
sc.frame_set(1)
def rot(bone, axis, deg):
    pb = arm.pose.bones[bone]; h = pb.head.copy()
    pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(math.radians(deg), 4, axis) @ Matrix.Translation(-h) @ pb.matrix
    bpy.context.view_layer.update()
rot("neck_01", "X", 8); rot("neck_02", "X", 6); rot("head", "X", 22)      # kepala mendongak/menunduk Â±36Â° total (lebih dari lompat Manny: 25Â°)
sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "FLAT"; sh.color_type = "TEXTURE"
sc.view_settings.view_transform = "Standard"; sc.world = sc.world or bpy.data.worlds.new("w"); sc.world.color = (0.45, 0.5, 0.55)
for o in bpy.data.objects:
    if o.type in {"ARMATURE", "EMPTY"}: o.hide_render = True
cd = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
cd.type = "ORTHO"; cd.ortho_scale = 0.62
sc.render.resolution_x = sc.render.resolution_y = 900
for name, loc in (("samping", (4, 0, 1.70)), ("depan34", (-2.4, -3.2, 1.78))):
    cam.location = Vector(loc); cam.rotation_euler = (Vector((0, 0, 1.70)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = f"C:/repository/unreal_engine/jayadwara/Art/Export/_jd2/_tilt_{tag}_{name}.png"; bpy.ops.render.render(write_still=True)
