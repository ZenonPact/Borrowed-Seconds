// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class BorrowedSeconds : ModuleRules
{
	public BorrowedSeconds(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"AIModule",
			"StateTreeModule",
			"GameplayStateTreeModule",
			"UMG",
			"Slate"
		});

		PrivateDependencyModuleNames.AddRange(new string[] { });

		PublicIncludePaths.AddRange(new string[] {
			"BorrowedSeconds",
			"BorrowedSeconds/Variant_Horror",
			"BorrowedSeconds/Variant_Horror/UI",
			"BorrowedSeconds/Variant_Shooter",
			"BorrowedSeconds/Variant_Shooter/AI",
			"BorrowedSeconds/Variant_Shooter/UI",
			"BorrowedSeconds/Variant_Shooter/Weapons"
		});

		// Uncomment if you are using Slate UI
		// PrivateDependencyModuleNames.AddRange(new string[] { "Slate", "SlateCore" });

		// Uncomment if you are using online features
		// PrivateDependencyModuleNames.Add("OnlineSubsystem");

		// To include OnlineSubsystemSteam, add it to the plugins section in your uproject file with the Enabled attribute set to true
	}
}
