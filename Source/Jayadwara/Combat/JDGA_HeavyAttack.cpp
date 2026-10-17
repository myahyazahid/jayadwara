#include "Combat/JDGA_HeavyAttack.h"

#include "AbilitySystemComponent.h"
#include "Abilities/JDGameplayTags.h"
#include "Abilities/Tasks/AbilityTask_PlayMontageAndWait.h"
#include "Combat/JDCombatComponent.h"
#include "Combat/JDCombatProfile.h"
#include "Animation/AnimInstance.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "TimerManager.h"

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
	const FJDAttackStep& Step = IsAvatarFalling(ActorInfo) && Profile->AirSlam.Montage
		? Profile->AirSlam : Profile->GetHeavyAttack(Combat->GetComboStepForFinisher());
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
	bSlam = false;
	bSlamLanded = false;
	if (IsAvatarFalling(ActorInfo) && Profile->AirSlam.Montage)
	{
		ActivateAirSlam(Profile->AirSlam);
		return;
	}

	// Cabang finisher: combo ringan yang baru dipotong menentukan pukulan beratnya (docs/07 "Combo & arah").
	const FJDAttackStep& Step = Profile->GetHeavyAttack(Combat->GetComboStepForFinisher());

	SpendStamina(Step.StaminaCost);
	FaceInputDirection();
	WarpToSoftTarget();
	Combat->BeginAttack(Step);

	UAbilityTask_PlayMontageAndWait* Task = UAbilityTask_PlayMontageAndWait::CreatePlayMontageAndWaitProxy(
		this, NAME_None, Step.Montage, GetMontageRate(Step.PlayRate));
	Task->OnBlendOut.AddDynamic(this, &UJDGA_HeavyAttack::OnMontageFinished);
	Task->OnCompleted.AddDynamic(this, &UJDGA_HeavyAttack::OnMontageFinished);
	Task->OnInterrupted.AddDynamic(this, &UJDGA_HeavyAttack::OnMontageInterrupted);
	Task->OnCancelled.AddDynamic(this, &UJDGA_HeavyAttack::OnMontageInterrupted);
	Task->ReadyForActivation();
}

void UJDGA_HeavyAttack::ActivateAirSlam(const FJDAttackStep& Step)
{
	ACharacter* Character = Cast<ACharacter>(GetAvatarActorFromActorInfo());
	UJDCombatComponent* Combat = GetCombat();
	const UJDCombatProfile* Profile = GetCombatProfile();
	UWorld* World = GetWorld();
	if (!Character || !Combat || !Profile || !World)
	{
		EndAbility(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, true, true);
		return;
	}
	bSlam = true;
	SpendStamina(Step.StaminaCost);
	FaceInputDirection();
	Combat->BeginAttack(Step);

	// Montage hanya pose menukik: selesai/blend out sebelum mendarat tidak mengakhiri ability, pendaratan yang mengakhiri.
	UAnimInstance* Anim = Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr;
	if (Anim && Anim->Montage_Play(Step.Montage, GetMontageRate(Step.PlayRate)) > 0.0f)
	{
		SlamMontage = Step.Montage;
	}
	Character->LaunchCharacter(FVector(0.0f, 0.0f, -Profile->AirSlamSpeed), true, true);
	LandedHandle = Combat->OnLanded.AddUObject(this, &UJDGA_HeavyAttack::OnSlamLanded);

	// Pengaman kalau tidak pernah mendarat (mis. tersangkut di tepi).
	World->GetTimerManager().SetTimer(SlamTimer, FTimerDelegate::CreateWeakLambda(this, [this]()
	{
		EndAbility(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, true, true);
	}), 3.0f, false);
}

void UJDGA_HeavyAttack::OnSlamLanded()
{
	UJDCombatComponent* Combat = GetCombat();
	const UJDCombatProfile* Profile = GetCombatProfile();
	const ACharacter* Character = Cast<ACharacter>(GetAvatarActorFromActorInfo());
	UWorld* World = GetWorld();
	if (!IsActive() || bSlamLanded || !Combat || !Profile || !Character || !World)
	{
		return;
	}
	bSlamLanded = true;
	Combat->OnLanded.Remove(LandedHandle);
	LandedHandle.Reset();

	const float HalfHeight = Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
	Combat->ApplyAreaHit(Character->GetActorLocation() - FVector(0.0f, 0.0f, HalfHeight), Profile->AirSlamRadius);

	World->GetTimerManager().SetTimer(SlamTimer, FTimerDelegate::CreateWeakLambda(this, [this]()
	{
		EndAbility(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, true, false);
	}), FMath::Max(Profile->AirSlamRecovery, 0.01f), false);
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
		UJDCombatComponent* Combat = GetCombat();
		if (Combat)
		{
			Combat->EndAttack();
		}
		if (bSlam)
		{
			if (Combat && LandedHandle.IsValid())
			{
				Combat->OnLanded.Remove(LandedHandle);
			}
			LandedHandle.Reset();
			if (UWorld* World = GetWorld())
			{
				World->GetTimerManager().ClearTimer(SlamTimer);
			}
			const ACharacter* Character = Cast<ACharacter>(GetAvatarActorFromActorInfo());
			UAnimInstance* Anim = Character && Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr;
			if (Anim && SlamMontage)
			{
				Anim->Montage_Stop(0.2f, SlamMontage);
			}
			SlamMontage = nullptr;
			bSlam = false;
		}
	}
	Super::EndAbility(Handle, ActorInfo, ActivationInfo, bReplicateEndAbility, bWasCancelled);
}
