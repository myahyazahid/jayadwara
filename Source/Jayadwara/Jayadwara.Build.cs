// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class Jayadwara : ModuleRules
{
	public Jayadwara(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		// Include relatif dari akar modul, mis. #include "Characters/JDHumanCharacter.h" (struktur folder docs/12).
		PublicIncludePaths.Add(ModuleDirectory);

		// Daftar modul mengikuti docs/12-technical-design.md (Dependensi module).
		// GeometryCollectionEngine (Chaos Destruction) ditambah di Fase 1 (Mar 2027) setelah plugin-nya diaktifkan dari editor.
		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput",
			"GameplayAbilities", "GameplayTags", "GameplayTasks",
			"AIModule", "StateTreeModule", "GameplayStateTreeModule",
			"Niagara", "MotionWarping"
		});

		PrivateDependencyModuleNames.AddRange(new string[] { "UMG", "Slate", "SlateCore" });

		// Uncomment if you are using online features
		// PrivateDependencyModuleNames.Add("OnlineSubsystem");

		// To include OnlineSubsystemSteam, add it to the plugins section in your uproject file with the Enabled attribute set to true
	}
}
