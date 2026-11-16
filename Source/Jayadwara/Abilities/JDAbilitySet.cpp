#include "Abilities/JDAbilitySet.h"

#include "Abilities/JDAbilitySystemComponent.h"
#include "Abilities/JDGameplayAbility.h"
#include "Abilities/JDGameplayEffects.h"
#include "Abilities/JDGameplayTags.h"
#include "Jayadwara.h"

void FJDAbilitySet_GrantedHandles::TakeFromAbilitySystem(UJDAbilitySystemComponent* ASC)
{
	if (ASC)
	{
		for (const FGameplayAbilitySpecHandle& Handle : AbilityHandles)
		{
			ASC->ClearAbility(Handle);
		}
		for (const FActiveGameplayEffectHandle& Handle : EffectHandles)
		{
			ASC->RemoveActiveGameplayEffect(Handle);
		}
	}
	AbilityHandles.Reset();
	EffectHandles.Reset();
}

void UJDAbilitySet::GiveToAbilitySystem(UJDAbilitySystemComponent* ASC, FJDAbilitySet_GrantedHandles* OutHandles) const
{
	if (!ASC)
	{
		return;
	}

	// Atribut awal dulu: GE & ability berikutnya boleh bergantung pada nilai Max.
	FGameplayEffectSpecHandle Init = ASC->MakeOutgoingSpec(UJDGE_InitAttributes::StaticClass(), 1.0f, ASC->MakeEffectContext());
	if (Init.IsValid())
	{
		Init.Data->SetSetByCallerMagnitude(JDGameplayTags::Data_Init_MaxHealth, Attributes.MaxHealth);
		Init.Data->SetSetByCallerMagnitude(JDGameplayTags::Data_Init_MaxStamina, Attributes.MaxStamina);
		Init.Data->SetSetByCallerMagnitude(JDGameplayTags::Data_Init_MaxPoise, Attributes.MaxPoise);
		Init.Data->SetSetByCallerMagnitude(JDGameplayTags::Data_Init_MaxSync, Attributes.MaxSync);
		Init.Data->SetSetByCallerMagnitude(JDGameplayTags::Data_Init_MaxTransformEnergy, Attributes.MaxTransformEnergy);
		ASC->ApplyGameplayEffectSpecToSelf(*Init.Data.Get());
	}

	ASC->ConfigureStaminaRegen(Attributes.StaminaRegenPerSecond, Attributes.StaminaRegenDelay);
	ASC->ConfigurePoiseRegen(Attributes.PoiseRegenPerSecond, Attributes.PoiseRegenDelay);
	ASC->SetInputBufferTime(InputBufferTime);

	for (const FJDAbilitySet_Effect& Entry : Effects)
	{
		if (!Entry.Effect)
		{
			UE_LOG(LogJayadwara, Warning, TEXT("%s: entri Effects kosong"), *GetName());
			continue;
		}
		const FGameplayEffectSpecHandle Spec = ASC->MakeOutgoingSpec(Entry.Effect, Entry.EffectLevel, ASC->MakeEffectContext());
		if (Spec.IsValid())
		{
			const FActiveGameplayEffectHandle Handle = ASC->ApplyGameplayEffectSpecToSelf(*Spec.Data.Get());
			if (OutHandles && Handle.IsValid())
			{
				OutHandles->EffectHandles.Add(Handle);
			}
		}
	}

	for (const FJDAbilitySet_Ability& Entry : Abilities)
	{
		if (!Entry.Ability)
		{
			UE_LOG(LogJayadwara, Warning, TEXT("%s: entri Abilities kosong"), *GetName());
			continue;
		}
		FGameplayAbilitySpec Spec(Entry.Ability, Entry.AbilityLevel, INDEX_NONE, ASC->GetOwner());
		if (Entry.InputTag.IsValid())
		{
			Spec.GetDynamicSpecSourceTags().AddTag(Entry.InputTag);
		}
		const FGameplayAbilitySpecHandle Handle = ASC->GiveAbility(Spec);
		if (OutHandles)
		{
			OutHandles->AbilityHandles.Add(Handle);
		}
	}
}
