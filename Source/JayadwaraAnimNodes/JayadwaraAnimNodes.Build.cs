using UnrealBuildTool;

// Modul UncookedOnly: node AnimGraph (sisi editor dari FAnimNode_* runtime di modul Jayadwara). UE mewajibkan node K2/AnimGraph
// yang dipakai di Anim Blueprint runtime berada di modul Developer/UncookedOnly, bukan Editor (jika tidak, ABP gagal saat cook).
public class JayadwaraAnimNodes : ModuleRules
{
	public JayadwaraAnimNodes(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "AnimGraph", "AnimGraphRuntime", "Jayadwara" });
		PrivateDependencyModuleNames.AddRange(new string[] { "BlueprintGraph" });
	}
}
