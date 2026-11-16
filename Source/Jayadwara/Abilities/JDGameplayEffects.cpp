#include "Abilities/JDGameplayEffects.h"

#include "AbilitySystemComponent.h"
#include "Abilities/JDAttributeSet.h"
#include "Abilities/JDGameplayTags.h"

namespace
{
	FGameplayModifierInfo MakeSetByCallerModifier(const FGameplayAttribute& Attribute, EGameplayModOp::Type Op, const FGameplayTag& DataTag)
	{
		FSetByCallerFloat SetByCaller;
		SetByCaller.DataTag = DataTag;

		FGameplayModifierInfo Modifier;
		Modifier.Attribute = Attribute;
		Modifier.ModifierOp = Op;
		Modifier.ModifierMagnitude = FGameplayEffectModifierMagnitude(SetByCaller);
		return Modifier;
	}
}

UJDGE_InitAttributes::UJDGE_InitAttributes()
{
	DurationPolicy = EGameplayEffectDurationType::Instant;

	const TPair<FGameplayAttribute, FGameplayAttribute> Pairs[] =
	{
		{ UJDAttributeSet::GetMaxHealthAttribute(), UJDAttributeSet::GetHealthAttribute() },
		{ UJDAttributeSet::GetMaxStaminaAttribute(), UJDAttributeSet::GetStaminaAttribute() },
		{ UJDAttributeSet::GetMaxPoiseAttribute(), UJDAttributeSet::GetPoiseAttribute() },
		{ UJDAttributeSet::GetMaxSyncAttribute(), UJDAttributeSet::GetSyncAttribute() },
		{ UJDAttributeSet::GetMaxTransformEnergyAttribute(), UJDAttributeSet::GetTransformEnergyAttribute() },
	};
	const FGameplayTag Tags[] =
	{
		JDGameplayTags::Data_Init_MaxHealth, JDGameplayTags::Data_Init_MaxStamina, JDGameplayTags::Data_Init_MaxPoise,
		JDGameplayTags::Data_Init_MaxSync, JDGameplayTags::Data_Init_MaxTransformEnergy,
	};

	for (int32 i = 0; i < UE_ARRAY_COUNT(Pairs); ++i)
	{
		Modifiers.Add(MakeSetByCallerModifier(Pairs[i].Key, EGameplayModOp::Override, Tags[i]));
		Modifiers.Add(MakeSetByCallerModifier(Pairs[i].Value, EGameplayModOp::Override, Tags[i]));
	}
}

UJDGE_StaminaRegen::UJDGE_StaminaRegen()
{
	DurationPolicy = EGameplayEffectDurationType::Infinite;
	Period = FScalableFloat(TickPeriod);
	bExecutePeriodicEffectOnApplication = false;

	Modifiers.Add(MakeSetByCallerModifier(UJDAttributeSet::GetStaminaAttribute(), EGameplayModOp::Additive, JDGameplayTags::Data_StaminaRegen));
}

UJDGE_PoiseRegen::UJDGE_PoiseRegen()
{
	DurationPolicy = EGameplayEffectDurationType::Infinite;
	Period = FScalableFloat(TickPeriod);
	bExecutePeriodicEffectOnApplication = false;

	Modifiers.Add(MakeSetByCallerModifier(UJDAttributeSet::GetPoiseAttribute(), EGameplayModOp::Additive, JDGameplayTags::Data_PoiseRegen));
}

UJDGE_Damage::UJDGE_Damage()
{
	DurationPolicy = EGameplayEffectDurationType::Instant;

	Modifiers.Add(MakeSetByCallerModifier(UJDAttributeSet::GetIncomingDamageAttribute(), EGameplayModOp::Additive, JDGameplayTags::Data_Damage));
	Modifiers.Add(MakeSetByCallerModifier(UJDAttributeSet::GetIncomingPoiseDamageAttribute(), EGameplayModOp::Additive, JDGameplayTags::Data_PoiseDamage));
}

FGameplayEffectSpecHandle UJDGE_Damage::MakeSpec(const UAbilitySystemComponent* Source, float Damage, float PoiseDamage)
{
	if (!Source)
	{
		return FGameplayEffectSpecHandle();
	}

	FGameplayEffectSpecHandle Spec = Source->MakeOutgoingSpec(UJDGE_Damage::StaticClass(), 1.0f, Source->MakeEffectContext());
	if (Spec.IsValid())
	{
		Spec.Data->SetSetByCallerMagnitude(JDGameplayTags::Data_Damage, Damage);
		Spec.Data->SetSetByCallerMagnitude(JDGameplayTags::Data_PoiseDamage, PoiseDamage);
	}
	return Spec;
}
