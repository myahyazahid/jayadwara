#include "Combat/JDGA_Dodge.h"

#include "AbilitySystemComponent.h"
#include "Abilities/JDGameplayTags.h"
#include "Abilities/Tasks/AbilityTask_ApplyRootMotionConstantForce.h"
#include "Animation/AnimInstance.h"
#include "Combat/JDCombatProfile.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "TimerManager.h"

UJDGA_Dodge::UJDGA_Dodge()
{
	ActivationPolicy = EJDAbilityActivationPolicy::OnInputTriggered;

	FGameplayTagContainer AssetTags;
	AssetTags.AddTag(JDGameplayTags::Ability_Dodge);
	SetAssetTags(AssetTags);

	ActivationOwnedTags.AddTag(JDGameplayTags::State_Dodging);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Dead);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Stagger);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Knockdown);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Dodging);

	CancelAbilitiesWithTag.AddTag(JDGameplayTags::Ability_Block);
}

bool UJDGA_Dodge::CanActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
	const FGameplayTagContainer* SourceTags, const FGameplayTagContainer* TargetTags, FGameplayTagContainer* OptionalRelevantTags) const
{
	if (!Super::CanActivateAbility(Handle, ActorInfo, SourceTags, TargetTags, OptionalRelevantTags))
	{
		return false;
	}
	const UJDCombatProfile* Profile = GetCombatProfile(ActorInfo);
	const ACharacter* Character = ActorInfo ? Cast<ACharacter>(ActorInfo->AvatarActor.Get()) : nullptr;
	return Profile && Character && Character->GetCharacterMovement()->IsMovingOnGround()
		&& HasStamina(ActorInfo, Profile->DodgeStaminaCost) && IsAttackCancelable(ActorInfo);
}

void UJDGA_Dodge::ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
	const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData)
{
	ACharacter* Character = Cast<ACharacter>(GetAvatarActorFromActorInfo());
	const UJDCombatProfile* Profile = GetCombatProfile();
	UWorld* World = GetWorld();
	if (!Character || !Profile || !World || !CommitAbility(Handle, ActorInfo, ActivationInfo))
	{
		EndAbility(Handle, ActorInfo, ActivationInfo, true, true);
		return;
	}

	// Membatalkan recovery serangan (CanActivate sudah memastikan frame hit lewat).
	CancelAbilitiesWithAnyTag({ JDGameplayTags::Ability_Attack_Light, JDGameplayTags::Ability_Attack_Heavy });
	SpendStamina(Profile->DodgeStaminaCost);

	FVector Direction = GetInputDirection2D();
	if (Direction.IsZero())
	{
		Direction = -Character->GetActorForwardVector().GetSafeNormal2D();
	}

	// Hadap tetap selama dodge supaya arah relatif (animasi kiri/kanan/belakang) bermakna.
	UCharacterMovementComponent* Movement = Character->GetCharacterMovement();
	bRestoreOrientToMovement = Movement->bOrientRotationToMovement;
	Movement->bOrientRotationToMovement = false;

	const FVector Local = Character->GetActorRotation().UnrotateVector(Direction);
	const FJDDirectionalMontages& M = Profile->DodgeMontages;
	UAnimMontage* Montage = FMath::Abs(Local.X) >= FMath::Abs(Local.Y)
		? (Local.X >= 0.0f ? M.Forward : M.Backward)
		: (Local.Y >= 0.0f ? M.Right : M.Left);
	USkeletalMeshComponent* Mesh = Character->GetMesh();
	if (Montage && Mesh && Mesh->GetAnimInstance())
	{
		PlayingMontage = Montage;
		Mesh->GetAnimInstance()->Montage_Play(Montage, GetMontageRate());
	}

	if (UAbilitySystemComponent* ASC = GetAbilitySystemComponentFromActorInfo())
	{
		FGameplayCueParameters Cue;
		Cue.Location = Character->GetActorLocation();
		Cue.Instigator = Character;
		ASC->ExecuteGameplayCue(JDGameplayTags::GameplayCue_Dodge, Cue);
	}

	// i-frame
	if (Profile->DodgeIFrameDuration > 0.0f)
	{
		auto Begin = [this, World, Duration = Profile->DodgeIFrameDuration]()
		{
			SetInvulnerable(true);
			World->GetTimerManager().SetTimer(IFrameEndTimer, FTimerDelegate::CreateWeakLambda(this, [this]() { SetInvulnerable(false); }), Duration, false);
		};
		if (Profile->DodgeIFrameStart > 0.0f)
		{
			World->GetTimerManager().SetTimer(IFrameStartTimer, FTimerDelegate::CreateWeakLambda(this, Begin), Profile->DodgeIFrameStart, false);
		}
		else
		{
			Begin();
		}
	}

	const float Duration = Profile->DodgeDuration;
	UAbilityTask_ApplyRootMotionConstantForce* Task = UAbilityTask_ApplyRootMotionConstantForce::ApplyRootMotionConstantForce(
		this, NAME_None, Direction, Profile->DodgeDistance / Duration, Duration, false, nullptr,
		ERootMotionFinishVelocityMode::ClampVelocity, FVector::ZeroVector, Movement->MaxWalkSpeed * 0.5f, true);
	Task->OnFinish.AddDynamic(this, &UJDGA_Dodge::OnDodgeFinished);
	Task->ReadyForActivation();
}

void UJDGA_Dodge::SetInvulnerable(bool bNewInvulnerable)
{
	if (bInvulnerable == bNewInvulnerable)
	{
		return;
	}
	bInvulnerable = bNewInvulnerable;
	if (UAbilitySystemComponent* ASC = GetAbilitySystemComponentFromActorInfo())
	{
		if (bInvulnerable)
		{
			ASC->AddLooseGameplayTag(JDGameplayTags::State_Invulnerable);
		}
		else
		{
			ASC->RemoveLooseGameplayTag(JDGameplayTags::State_Invulnerable);
		}
	}
}

void UJDGA_Dodge::OnDodgeFinished()
{
	EndAbility(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, true, false);
}

void UJDGA_Dodge::EndAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
	const FGameplayAbilityActivationInfo ActivationInfo, bool bReplicateEndAbility, bool bWasCancelled)
{
	if (IsActive())
	{
		if (UWorld* World = GetWorld())
		{
			World->GetTimerManager().ClearTimer(IFrameStartTimer);
			World->GetTimerManager().ClearTimer(IFrameEndTimer);
		}
		SetInvulnerable(false);

		if (ACharacter* Character = Cast<ACharacter>(GetAvatarActorFromActorInfo()))
		{
			Character->GetCharacterMovement()->bOrientRotationToMovement = bRestoreOrientToMovement;
			UAnimInstance* Anim = Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr;
			if (Anim && PlayingMontage && bWasCancelled)
			{
				Anim->Montage_Stop(0.15f, PlayingMontage);
			}
		}
		PlayingMontage = nullptr;
	}
	Super::EndAbility(Handle, ActorInfo, ActivationInfo, bReplicateEndAbility, bWasCancelled);
}
