"""Iterasi 4 — bake Ambient Occlusion (Cycles) ke UV atlas tiap slot material.

Mesh gabungan sementara (supaya oklusi ANTAR-bagian ikut terhitung, mis. bahu menaungi dada), satu image target per material.
Hasil: Art/Export/Textures/_bake/AO_<Slot>.png (mentah, ber-noise sesuai jumlah sample). make_textures.py menghaluskan
sedikit lalu memasukkannya ke kanal R ORM. Variabel opsional: AO_SAMPLES (default 24), AO_DISTANCE (default 0.06 m).
Scene tidak berubah (engine dikembalikan, objek/material sementara dibuang).
"""
import os
import time

import bpy

SAMPLES = globals().get("AO_SAMPLES", 24)
DIST = globals().get("AO_DISTANCE", 0.06)
OUT = r"C:\repository\unreal_engine\jayadwara\Art\Export\Textures\_bake"
SIZE = {"Armor": 2048, "Cloth": 2048, "Body": 1024, "Face": 1024}
os.makedirs(OUT, exist_ok=True)

scene = bpy.context.scene
prev_engine = scene.render.engine
t0 = time.time()

parts = sorted([o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("JD_") and "jd_kind" in o], key=lambda o: o.name)
tmp_coll = bpy.data.collections.new("_BAKE_TMP")
scene.collection.children.link(tmp_coll)
dups = []
for ob in parts:
    d = ob.copy()
    d.data = ob.data.copy()
    d.modifiers.clear()
    d.parent = None
    d.matrix_world = ob.matrix_world.copy()
    tmp_coll.objects.link(d)
    dups.append(d)
for o in bpy.context.view_layer.objects:
    o.select_set(False)
for d in dups:
    d.select_set(True)
act = dups[0]
bpy.context.view_layer.objects.active = act
with bpy.context.temp_override(active_object=act, object=act, selected_objects=dups, selected_editable_objects=dups):
    bpy.ops.object.join()
J = bpy.context.view_layer.objects.active
J.name = "_BAKE_JOINED"
me = J.data

# image target per material (node tidak terhubung, dijadikan aktif)
targets = {}
for mat in me.materials:
    slot = mat.name.replace("M_Jayadwara_", "")
    img = bpy.data.images.new(f"AO_{slot}", SIZE[slot], SIZE[slot], alpha=False, float_buffer=False)
    img.colorspace_settings.name = "Non-Color"
    nt = mat.node_tree
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = img
    n.label = "BAKE_AO"
    nt.nodes.active = n
    n.select = True
    targets[slot] = (img, n, mat)

scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = False
if scene.world is None:
    scene.world = bpy.data.worlds.new("_bake_world")
scene.world.light_settings.distance = DIST
for o in bpy.context.view_layer.objects:
    o.select_set(False)
J.select_set(True)
bpy.context.view_layer.objects.active = J
try:
    res = bpy.ops.object.bake(type="AO", margin=8, margin_type="EXTEND", use_clear=True)
    print("bake:", res)
finally:
    scene.render.engine = prev_engine

for slot, (img, n, mat) in targets.items():
    path = os.path.join(OUT, f"AO_{slot}.png")
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    mat.node_tree.nodes.remove(n)
    bpy.data.images.remove(img)
    print("simpan:", path)

bpy.data.objects.remove(J, do_unlink=True)
for m in list(bpy.data.meshes):
    if m.users == 0:
        bpy.data.meshes.remove(m)
bpy.data.collections.remove(tmp_coll)
print(f"selesai dalam {time.time() - t0:.0f} s | samples={SAMPLES} jarak={DIST} m")
