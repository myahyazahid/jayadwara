using UnrealBuildTool;

// Modul editor-only: alat yang dipanggil dari skrip Python di Tools/ untuk pekerjaan yang tidak terjangkau API
// Python UE (mengisi Physics Asset, menyisipkan node Anim Graph). Tidak ikut ke build game.
public class JayadwaraEditor : ModuleRules
{
	public JayadwaraEditor(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine" });

		PrivateDependencyModuleNames.AddRange(new string[]
		{
			"UnrealEd", "PhysicsCore", "PhysicsUtilities", "MeshUtilitiesEngine",
			"AnimGraph", "AnimGraphRuntime", "BlueprintGraph", "IKRig", "IKRigEditor"
		});
	}
}
