#include "Core/JDCheatManager.h"

#include "Abilities/JDAbilitySystemComponent.h"
#include "Abilities/JDAttributeSet.h"
#include "Abilities/JDGameplayEffects.h"
#include "Abilities/JDGameplayTags.h"
#include "AbilitySystemGlobals.h"
#include "Characters/JDTrainingDummy.h"
#include "EngineUtils.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "HAL/IConsoleManager.h"
#include "Jayadwara.h"

UJDAbilitySystemComponent* UJDCheatManager::GetPawnASC() const
{
	const APlayerController* PC = GetPlayerController();
	UJDAbilitySystemComponent* ASC = Cast<UJDAbilitySystemComponent>(
		UAbilitySystemGlobals::GetAbilitySystemComponentFromActor(PC ? PC->GetPawn() : nullptr));
	if (!ASC)
	{
		UE_LOG(LogJayadwara, Warning, TEXT("Cheat: pawn pemain tidak punya UJDAbilitySystemComponent"));
	}
	return ASC;
}

void UJDCheatManager::ToggleGod()
{
	bGod = !bGod;
	if (const APlayerController* PC = GetPlayerController())
	{
		ApplyToPawn(PC->GetPawn());
	}
	UE_LOG(LogJayadwara, Display, TEXT("JD.God %s"), bGod ? TEXT("ON") : TEXT("OFF"));
}

void UJDCheatManager::ApplyToPawn(APawn* Pawn)
{
	if (UAbilitySystemComponent* ASC = UAbilitySystemGlobals::GetAbilitySystemComponentFromActor(Pawn))
	{
		ASC->SetLooseGameplayTagCount(JDGameplayTags::Cheat_God, bGod ? 1 : 0);
	}
}

void UJDCheatManager::ApplyDamage(float Amount)
{
	if (UJDAbilitySystemComponent* ASC = GetPawnASC())
	{
		const FGameplayEffectSpecHandle Spec = UJDGE_Damage::MakeSpec(ASC, Amount);
		if (Spec.IsValid())
		{
			ASC->ApplyGameplayEffectSpecToSelf(*Spec.Data.Get());
		}
		UE_LOG(LogJayadwara, Display, TEXT("JD.Damage %.1f -> Health %.1f"), Amount, ASC->GetNumericAttribute(UJDAttributeSet::GetHealthAttribute()));
	}
}

void UJDCheatManager::Heal()
{
	if (UJDAbilitySystemComponent* ASC = GetPawnASC())
	{
		const float MaxHealth = ASC->GetNumericAttribute(UJDAttributeSet::GetMaxHealthAttribute());
		ASC->SetNumericAttributeBase(UJDAttributeSet::GetHealthAttribute(), MaxHealth);
		ASC->SetLooseGameplayTagCount(JDGameplayTags::State_Dead, 0);
		UE_LOG(LogJayadwara, Display, TEXT("JD.Heal -> Health %.1f"), MaxHealth);
	}
}

void UJDCheatManager::SpendStamina(float Amount)
{
	if (UJDAbilitySystemComponent* ASC = GetPawnASC())
	{
		ASC->ApplyModToAttribute(UJDAttributeSet::GetStaminaAttribute(), EGameplayModOp::Additive, -FMath::Abs(Amount));
		UE_LOG(LogJayadwara, Display, TEXT("JD.Stamina -%.1f -> Stamina %.1f"), FMath::Abs(Amount), ASC->GetNumericAttribute(UJDAttributeSet::GetStaminaAttribute()));
	}
}

// ------------------------------------------------------------------ perintah konsol "JD.*"
#if !UE_BUILD_SHIPPING
namespace
{
	UJDCheatManager* FindCheatManager(UWorld* World)
	{
		APlayerController* PC = World ? World->GetFirstPlayerController() : nullptr;
		UJDCheatManager* Cheats = PC ? Cast<UJDCheatManager>(PC->CheatManager) : nullptr;
		if (!Cheats)
		{
			UE_LOG(LogJayadwara, Warning, TEXT("Cheat tidak aktif (bukan PIE/Standalone, atau controller bukan AJDPlayerController)"));
		}
		return Cheats;
	}

	float ArgOr(const TArray<FString>& Args, float Default)
	{
		return Args.Num() > 0 ? FCString::Atof(*Args[0]) : Default;
	}

	FAutoConsoleCommandWithWorldAndArgs GJDGod(TEXT("JD.God"), TEXT("Nyalakan/matikan kebal damage"),
		FConsoleCommandWithWorldAndArgsDelegate::CreateLambda([](const TArray<FString>&, UWorld* World)
		{
			if (UJDCheatManager* C = FindCheatManager(World)) { C->ToggleGod(); }
		}));

	FAutoConsoleCommandWithWorldAndArgs GJDDamage(TEXT("JD.Damage"), TEXT("JD.Damage <n>: damage n ke pawn pemain (default 10)"),
		FConsoleCommandWithWorldAndArgsDelegate::CreateLambda([](const TArray<FString>& Args, UWorld* World)
		{
			if (UJDCheatManager* C = FindCheatManager(World)) { C->ApplyDamage(ArgOr(Args, 10.0f)); }
		}));

	FAutoConsoleCommandWithWorldAndArgs GJDHeal(TEXT("JD.Heal"), TEXT("Health penuh"),
		FConsoleCommandWithWorldAndArgsDelegate::CreateLambda([](const TArray<FString>&, UWorld* World)
		{
			if (UJDCheatManager* C = FindCheatManager(World)) { C->Heal(); }
		}));

	FAutoConsoleCommandWithWorldAndArgs GJDDummyAttack(TEXT("JD.Dummy.Attack"),
		TEXT("JD.Dummy.Attack <0|1>: mode menyerang semua training dummy (tanpa argumen = bolak-balik)"),
		FConsoleCommandWithWorldAndArgsDelegate::CreateLambda([](const TArray<FString>& Args, UWorld* World)
		{
			if (!World)
			{
				return;
			}
			int32 Count = 0;
			bool bEnable = Args.Num() > 0 && FCString::Atoi(*Args[0]) != 0;
			for (TActorIterator<AJDTrainingDummy> It(World); It; ++It)
			{
				if (Args.IsEmpty() && Count == 0)
				{
					bEnable = !It->IsAttackMode();
				}
				It->SetAttackMode(bEnable);
				++Count;
			}
			UE_LOG(LogJayadwara, Display, TEXT("JD.Dummy.Attack %d -> %d dummy"), bEnable ? 1 : 0, Count);
		}));

	FAutoConsoleCommandWithWorldAndArgs GJDInput(TEXT("JD.Input"),
		TEXT("JD.Input <Input.tag> <1|0>: tekan (1) / lepas (0) input tag pawn pemain tanpa perangkat (uji otomatis)"),
		FConsoleCommandWithWorldAndArgsDelegate::CreateLambda([](const TArray<FString>& Args, UWorld* World)
		{
			APlayerController* PC = World ? World->GetFirstPlayerController() : nullptr;
			UJDAbilitySystemComponent* ASC = Cast<UJDAbilitySystemComponent>(
				UAbilitySystemGlobals::GetAbilitySystemComponentFromActor(PC ? PC->GetPawn() : nullptr));
			const FGameplayTag Tag = Args.Num() > 0 ? FGameplayTag::RequestGameplayTag(FName(*Args[0]), false) : FGameplayTag();
			if (!ASC || !Tag.IsValid())
			{
				UE_LOG(LogJayadwara, Warning, TEXT("JD.Input: pawn tanpa ASC atau tag tidak dikenal"));
				return;
			}
			if (Args.Num() < 2 || FCString::Atoi(*Args[1]) != 0)
			{
				ASC->AbilityInputTagPressed(Tag);
			}
			else
			{
				ASC->AbilityInputTagReleased(Tag);
			}
		}));

	FAutoConsoleCommandWithWorldAndArgs GJDStamina(TEXT("JD.Stamina"), TEXT("JD.Stamina <n>: kurangi stamina n (default 30), regen mulai setelah jeda"),
		FConsoleCommandWithWorldAndArgsDelegate::CreateLambda([](const TArray<FString>& Args, UWorld* World)
		{
			if (UJDCheatManager* C = FindCheatManager(World)) { C->SpendStamina(ArgOr(Args, 30.0f)); }
		}));
}
#endif
