
import unreal
print("SkeletalMeshEditorSubsystem:", [x for x in dir(unreal.SkeletalMeshEditorSubsystem) if "bone" in x.lower()])
def bones(path):
    m = unreal.load_asset(path)
    sk = m.get_editor_property("skeleton")
    try:
        names = unreal.SkeletalMeshEditorSubsystem().get_bone_names(m)
    except Exception as e:
        names = []
        print("  (subsistem gagal:", str(e)[:60], ")")
    return sk, names
for p in ("/Game/Jayadwara/Characters/Aksa2/Mesh/SK_Aksa2", "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"):
    sk, names = bones(p)
    print(p.split("/")[-1], "| skel:", sk.get_name(), "| tulang:", len(names))
    print("   ", [str(n) for n in names[:8]])
