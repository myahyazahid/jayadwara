#include "Combat/JDGA_HeavyAttack.h"

#include "AbilitySystemComponent.h"
#include "Abilities/JDGameplayTags.h"
#include "Abilities/Tasks/AbilityTask_PlayMontageAndWait.h"
#include "Combat/JDCombatComponent.h"
#include "Combat/JDCombatProfile.h"

UJDGA_HeavyAttack::UJDGA_HeavyAttack()
{
	ActivationPolicy = EJDAbilityActivationPolicy::OnInputTriggered;

	FGameplayTagContainer AssetTags;
	AssetTags.AddTag(JDGameplayTags::Ability_Attack_Heavy);
	SetAssetTags(AssetTags);

	ActivationOwnedTags.AddTag(JDGameplayTags::State_Attacking);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Dead);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Stagger);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Knockdown);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Dodging);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Blocking);

	// Memotong combo ringan (hanya terjadi kalau CanActivate mengizinkan: jendela combo / recovery).
	CancelAbilitiesWithTag.AddTag(JDGameplayTags::Ability_Attack_Light);
}

bool UJDGA_HeavyAttack::CanActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
	const FGameplayTagContainer* SourceTags, const FGameplayTagContainer* TargetTags, FGameplayTagContainer* OptionalRelevantTags) const
{
	if (!Super::CanActivateAbility(Handle, ActorInfo, SourceTags, TargetTags, OptionalRelevantTags))
	{
		return false;
	}
	const AActor* Avatar = ActorInfo ? ActorInfo->AvatarActor.Get() : nullptr;
	const UJDCombatComponent* Combat = Avatar ? Avatar->FindComponentByClass<UJDCombatComponent>() : nullptr;
	const UJDCombatProfile* Profile = Combat ? Combat->GetCombatProfile() : nullptr;
	if (!Profile)
	{
		return false;
	}
	const FJDAttackStep& Step = Profile->GetHeavyAttack(Combat->GetComboStepForFinisher());
	if (!Step.Montage || !HasStamina(ActorInfo, Step.StaminaCost))
	{
		return false;
	}
	const UAbilitySystemComponent* ASC = ActorInfo->AbilitySystemComponent.Get();
	return IsAttackCancelable(ActorInfo) || (ASC && ASC->HasMatchingGameplayTag(JDGameplayTags::State_Combat_ComboWindow));
}

void UJDGA_HeavyAttack::ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
	const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData)
{
	UJDCombatComponent* Combat = GetCombat();
	const UJDCombatProfile* Profile = GetCombatProfile();
	if (!Combat || !Profile || !CommitAbility(Handle, ActorInfo, ActivationInfo))
	{
		EndAbility(Handle, ActorInfo, ActivationInfo, true, true);
		return;
	}
	// Cabang finisher: combo ringan yang baru dipotong menentukan pukulan beratnya (docs/07 "Combo & arah").
	const FJDAttackStep& Step = Profile->GetHeavyAttack(Combat->GetComboStepForFinisher());

	SpendStamina(Step.StaminaCost);
	FaceInputDirection();
	Combat->BeginAttack(Step);

	UAbilityTask_PlayMontageAndWait* Task = UAbilityTask_PlayMontageAndWait::CreatePlayMontageAndWaitProxy(
		this, NAME_None, Step.Montage, GetMontageRate(Step.PlayRate));
	Task->OnBlendOut.AddDynamic(this, &UJDGA_HeavyAttack::OnMontageFinished);
	Task->OnCompleted.AddDynamic(this, &UJDGA_HeavyAttack::OnMontageFinished);
	Task->OnInterrupted.AddDynamic(this, &UJDGA_HeavyAttack::OnMontageInterrupted);
	Task->OnCancelled.AddDynamic(this, &UJDGA_HeavyAttack::OnMontageInterrupted);
	Task->ReadyForActivation();
}

void UJDGA_HeavyAttack::OnMontageFinished()
{
	EndAbility(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, true, false);
}

void UJDGA_HeavyAttack::OnMontageInterrupted()
{
	EndAbility(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, true, true);
}

void UJDGA_HeavyAttack::EndAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
	const FGameplayAbilityActivationInfo ActivationInfo, bool bReplicateEndAbility, bool bWasCancelled)
{
	if (IsActive())
	{
		if (UJDCombatComponent* Combat = GetCombat())
		{
			Combat->EndAttack();
		}
	}
	Super::EndAbility(Handle, ActorInfo, ActivationInfo, bReplicateEndAbility, bWasCancelled);
}
