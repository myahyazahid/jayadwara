#include "Abilities/JDAttributeSet.h"

#include "Abilities/JDGameplayTags.h"
#include "GameplayEffectExtension.h"

void UJDAttributeSet::PreAttributeBaseChange(const FGameplayAttribute& Attribute, float& NewValue) const
{
	Super::PreAttributeBaseChange(Attribute, NewValue);
	ClampAttribute(Attribute, NewValue);
}

void UJDAttributeSet::PreAttributeChange(const FGameplayAttribute& Attribute, float& NewValue)
{
	Super::PreAttributeChange(Attribute, NewValue);
	ClampAttribute(Attribute, NewValue);
}

void UJDAttributeSet::ClampAttribute(const FGameplayAttribute& Attribute, float& NewValue) const
{
	if (Attribute == GetHealthAttribute())
	{
		NewValue = FMath::Clamp(NewValue, 0.0f, GetMaxHealth());
	}
	else if (Attribute == GetStaminaAttribute())
	{
		NewValue = FMath::Clamp(NewValue, 0.0f, GetMaxStamina());
	}
	else if (Attribute == GetPoiseAttribute())
	{
		NewValue = FMath::Clamp(NewValue, 0.0f, GetMaxPoise());
	}
	else if (Attribute == GetSyncAttribute())
	{
		NewValue = FMath::Clamp(NewValue, 0.0f, GetMaxSync());
	}
	else if (Attribute == GetTransformEnergyAttribute())
	{
		NewValue = FMath::Clamp(NewValue, 0.0f, GetMaxTransformEnergy());
	}
	else if (Attribute == GetMaxHealthAttribute() || Attribute == GetMaxStaminaAttribute() || Attribute == GetMaxPoiseAttribute()
		|| Attribute == GetMaxSyncAttribute() || Attribute == GetMaxTransformEnergyAttribute())
	{
		NewValue = FMath::Max(NewValue, 0.0f);
	}
}

void UJDAttributeSet::PostGameplayEffectExecute(const FGameplayEffectModCallbackData& Data)
{
	Super::PostGameplayEffectExecute(Data);

	const UAbilitySystemComponent* ASC = GetOwningAbilitySystemComponent();

	if (Data.EvaluatedData.Attribute == GetIncomingDamageAttribute())
	{
		const float Damage = GetIncomingDamage();
		SetIncomingDamage(0.0f);
		if (Damage <= 0.0f || (ASC && ASC->HasMatchingGameplayTag(JDGameplayTags::Cheat_God)))
		{
			return;
		}

		const float HealthBefore = GetHealth();
		SetHealth(FMath::Clamp(HealthBefore - Damage, 0.0f, GetMaxHealth()));

		if (HealthBefore > 0.0f && GetHealth() <= 0.0f)
		{
			OnOutOfHealth.Broadcast(Data.EffectSpec.GetEffectContext().GetOriginalInstigator(), Damage);
		}
	}
	else if (Data.EvaluatedData.Attribute == GetIncomingPoiseDamageAttribute())
	{
		const float PoiseDamage = GetIncomingPoiseDamage();
		SetIncomingPoiseDamage(0.0f);
		if (PoiseDamage > 0.0f)
		{
			// Poise habis -> Event.Poise.Broken (stagger) menyusul di Iterasi 4.
			SetPoise(FMath::Clamp(GetPoise() - PoiseDamage, 0.0f, GetMaxPoise()));
		}
	}
}
