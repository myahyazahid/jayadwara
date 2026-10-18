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
#include "GameFramework/CharacterMovementComponent.h"
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
	// Serangan udara berbagi jatah dengan pukulan ringan: lompat = 1 serangan saja (LMB atau E).
	// Kalau masih naik, input ditahan dan baru dijalankan di puncak (lihat StartApexWait).
	if (IsAvatarFalling(ActorInfo) && Profile->AirSlam.Montage && !Combat->CanAirAttack())
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
	bSlamHang = false;
	if (IsAvatarFalling(ActorInfo) && Profile->AirSlam.Montage)
	{
		StartApexWait();
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

void UJDGA_HeavyAttack::StartApexWait()
{
	UWorld* World = GetWorld();
	const UJDCombatProfile* Profile = GetCombatProfile();
	if (!World || !Profile)
	{
		EndAbility(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, true, true);
		return;
	}
	// Tombol E yang ditekan sebelum puncak tetap dicatat: ability aktif tapi montage
	// belum diputar, lalu CheckApex menunggu sampai karakter berhenti naik.
	ApexWaitElapsed = 0.0f;
	World->GetTimerManager().SetTimer(ApexTimer,
		FTimerDelegate::CreateUObject(this, &UJDGA_HeavyAttack::CheckApex), 0.02f, true);
}

void UJDGA_HeavyAttack::CheckApex()
{
	UWorld* World = GetWorld();
	ACharacter* Character = Cast<ACharacter>(GetAvatarActorFromActorInfo());
	const UJDCombatProfile* Profile = GetCombatProfile();
	if (!World || !Character || !Profile)
	{
		if (World)
		{
			World->GetTimerManager().ClearTimer(ApexTimer);
		}
		EndAbility(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, true, true);
		return;
	}
	ApexWaitElapsed += 0.02f;
	const UCharacterMovementComponent* Movement = Character->GetCharacterMovement();
	const bool bAtApex = Character->GetVelocity().Z <= Profile->AirSlamApexVelocity;
	const bool bLanded = Movement && Movement->IsMovingOnGround();
	if (bAtApex || ApexWaitElapsed >= 1.5f)
	{
		World->GetTimerManager().ClearTimer(ApexTimer);
		ActivateAirSlam(Profile->AirSlam);
	}
	else if (bLanded)
	{
		World->GetTimerManager().ClearTimer(ApexTimer);
		EndAbility(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, true, true);
	}
}

void UJDGA_HeavyAttack::ActivateAirSlam(const FJDAttackStep& Step)
{
	ACharacter* Character = Cast<ACharacter>(GetAvatarActorFromActorInfo());
	UJDCombatComponent* Combat = GetCombat();
	const UJDCombatProfile* Profile = GetCombatProfile();
	if (!Character || !Combat || !Profile)
	{
		EndAbility(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, true, true);
		return;
	}
	bSlam = true;
	SpendStamina(Step.StaminaCost);
	FaceInputDirection();
	Combat->NoteAirAttack();          // pakai jatah serangan udara (sama dengan LMB)
	Combat->BeginAttack(Step);

	// Konsepnya sama dengan pukulan udara ringan: badan "ngambang" sebentar lalu montage
	// diputar di tempat. Tidak ada dash ke depan dan tidak ada hantaman ke tanah.
	StartSlamHang();

	UAbilityTask_PlayMontageAndWait* Task = UAbilityTask_PlayMontageAndWait::CreatePlayMontageAndWaitProxy(
		this, NAME_None, Step.Montage, GetMontageRate(Step.PlayRate));
	Task->OnBlendOut.AddDynamic(this, &UJDGA_HeavyAttack::OnMontageFinished);
	Task->OnCompleted.AddDynamic(this, &UJDGA_HeavyAttack::OnMontageFinished);
	Task->OnInterrupted.AddDynamic(this, &UJDGA_HeavyAttack::OnMontageInterrupted);
	Task->OnCancelled.AddDynamic(this, &UJDGA_HeavyAttack::OnMontageInterrupted);
	Task->ReadyForActivation();
}

void UJDGA_HeavyAttack::StartSlamHang()
{
	ACharacter* Character = Cast<ACharacter>(GetAvatarActorFromActorInfo());
	const UJDCombatProfile* Profile = GetCombatProfile();
	UWorld* World = GetWorld();
	if (!Character || !Profile || !World || Profile->AirHangTime <= 0.0f)
	{
		return;
	}
	UCharacterMovementComponent* Movement = Character->GetCharacterMovement();
	if (!Movement)
	{
		return;
	}
	if (!bSlamHang)
	{
		SavedGravityScale = Movement->GravityScale;
		bSlamHang = true;
	}
	Movement->GravityScale = SavedGravityScale * Profile->AirHangGravityScale;
	Movement->Velocity.Z = FMath::Max(Movement->Velocity.Z, 0.0f);
	World->GetTimerManager().SetTimer(HangTimer,
		FTimerDelegate::CreateUObject(this, &UJDGA_HeavyAttack::EndSlamHang), Profile->AirHangTime, false);
}

void UJDGA_HeavyAttack::EndSlamHang()
{
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(HangTimer);
	}
	if (!bSlamHang)
	{
		return;
	}
	bSlamHang = false;
	if (ACharacter* Character = Cast<ACharacter>(GetAvatarActorFromActorInfo()))
	{
		if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
		{
			Movement->GravityScale = SavedGravityScale;
		}
	}
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
		if (UWorld* World = GetWorld())
		{
			World->GetTimerManager().ClearTimer(ApexTimer);
		}
		UJDCombatComponent* Combat = GetCombat();
		if (Combat)
		{
			Combat->EndAttack();
		}
		if (bSlam)
		{
			EndSlamHang();
			bSlam = false;
		}
	}
	Super::EndAbility(Handle, ActorInfo, ActivationInfo, bReplicateEndAbility, bWasCancelled);
}
