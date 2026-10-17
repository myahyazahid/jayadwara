#include "Combat/JDGA_LightAttack.h"

#include "Abilities/JDAbilitySystemComponent.h"
#include "Abilities/JDGameplayTags.h"
#include "Abilities/Tasks/AbilityTask_ApplyRootMotionConstantForce.h"
#include "Abilities/Tasks/AbilityTask_ApplyRootMotionJumpForce.h"
#include "Abilities/Tasks/AbilityTask_PlayMontageAndWait.h"
#include "Combat/JDCombatComponent.h"
#include "Combat/JDCombatProfile.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "TimerManager.h"

UJDGA_LightAttack::UJDGA_LightAttack()
{
	ActivationPolicy = EJDAbilityActivationPolicy::OnInputTriggered;

	FGameplayTagContainer AssetTags;
	AssetTags.AddTag(JDGameplayTags::Ability_Attack_Light);
	SetAssetTags(AssetTags);

	ActivationOwnedTags.AddTag(JDGameplayTags::State_Attacking);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Attacking);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Dead);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Stagger);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Knockdown);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Dodging);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Blocking);
}

bool UJDGA_LightAttack::CanActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
	const FGameplayTagContainer* SourceTags, const FGameplayTagContainer* TargetTags, FGameplayTagContainer* OptionalRelevantTags) const
{
	if (!Super::CanActivateAbility(Handle, ActorInfo, SourceTags, TargetTags, OptionalRelevantTags))
	{
		return false;
	}
	const UJDCombatProfile* Profile = GetCombatProfile(ActorInfo);
	if (!Profile)
	{
		return false;
	}
	if (IsAvatarFalling(ActorInfo) && Profile->AirAttack.Montage)
	{
		const AActor* Avatar = ActorInfo->AvatarActor.Get();
		const UJDCombatComponent* Combat = Avatar ? Avatar->FindComponentByClass<UJDCombatComponent>() : nullptr;
		return Combat && Combat->CanAirAttack();
	}
	return !Profile->LightCombo.IsEmpty() && Profile->LightCombo[0].Montage;
}

void UJDGA_LightAttack::ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
	const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData)
{
	if (!CommitAbility(Handle, ActorInfo, ActivationInfo))
	{
		EndAbility(Handle, ActorInfo, ActivationInfo, true, true);
		return;
	}

	ComboIndex = 0;
	LastPressTime = -1000.0;

	if (UAbilitySystemComponent* ASC = GetAbilitySystemComponentFromActorInfo())
	{
		ComboWindowHandle = ASC->RegisterGameplayTagEvent(JDGameplayTags::State_Combat_ComboWindow, EGameplayTagEventType::NewOrRemoved)
			.AddUObject(this, &UJDGA_LightAttack::OnComboWindowChanged);
	}

	const UJDCombatProfile* Profile = GetCombatProfile();
	bAirMode = IsAvatarFalling(ActorInfo) && Profile && Profile->AirAttack.Montage;
	if (bAirMode)
	{
		PlayAirAttack();
		return;
	}

	if (const FJDAttackStep* Opener = ChooseOpener())
	{
		PlayAttack(*Opener, false);
		return;
	}
	PlayStep(0);
}

const FJDAttackStep* UJDGA_LightAttack::ChooseOpener()
{
	OpenerTarget.Reset();
	AActor* Avatar = GetAvatarActorFromActorInfo();
	UJDCombatComponent* Combat = GetCombat();
	const UJDCombatProfile* Profile = Combat ? Combat->GetCombatProfile() : nullptr;
	if (!Avatar || !Profile)
	{
		return nullptr;
	}

	// Serangan balik setelah parry (docs/07 "Parry"): selalu ke penyerang yang di-parry, apa pun arah input.
	if (AActor* Countered = Combat->ConsumeCounterTarget(); Countered && Profile->ParryCounterAttack.Montage)
	{
		const FVector ToCountered = (Countered->GetActorLocation() - Avatar->GetActorLocation()).GetSafeNormal2D();
		if (!ToCountered.IsZero())
		{
			Avatar->SetActorRotation(FRotator(0.0f, ToCountered.Rotation().Yaw, 0.0f));
		}
		OpenerTarget = Countered;
		return &Profile->ParryCounterAttack;
	}

	const FVector Input = GetInputDirection2D();
	if (Input.IsZero())
	{
		return nullptr;
	}
	AActor* Target = Combat->FindNearestTarget(Profile->TargetSearchRadius);
	if (!Target)
	{
		return nullptr;
	}
	const FVector ToTarget = (Target->GetActorLocation() - Avatar->GetActorLocation()) * FVector(1.0f, 1.0f, 0.0f);
	const FVector ToTargetDir = ToTarget.GetSafeNormal();
	const float Dot = FVector::DotProduct(Input, ToTargetDir);

	const FJDAttackStep* Opener = nullptr;
	if (Dot >= Profile->DirectionThreshold)
	{
		if (ToTarget.Size() > Profile->LungeMinDistance && Profile->LungeAttack.Montage)
		{
			Opener = &Profile->LungeAttack;
		}
	}
	else if (Dot <= -Profile->DirectionThreshold && Profile->BackAttack.Montage)
	{
		Opener = &Profile->BackAttack;
	}
	if (Opener && !ToTargetDir.IsZero())
	{
		// Pembuka selalu menghadap target: terjang maju ke arahnya, mundur sambil memukul ke arahnya.
		Avatar->SetActorRotation(FRotator(0.0f, ToTargetDir.Rotation().Yaw, 0.0f));
		OpenerTarget = Target;
	}
	return Opener;
}

void UJDGA_LightAttack::PlayAirAttack()
{
	UJDCombatComponent* Combat = GetCombat();
	const UJDCombatProfile* Profile = Combat ? Combat->GetCombatProfile() : nullptr;
	if (!Profile)
	{
		EndAbility(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, true, true);
		return;
	}
	Combat->NoteAirAttack();
	StartAirHang();
	PlayAttack(Profile->AirAttack, true);
}

void UJDGA_LightAttack::StartAirHang()
{
	ACharacter* Character = Cast<ACharacter>(GetAvatarActorFromActorInfo());
	const UJDCombatProfile* Profile = GetCombatProfile();
	UWorld* World = GetWorld();
	if (!Character || !Profile || !World || Profile->AirHangTime <= 0.0f)
	{
		return;
	}
	UCharacterMovementComponent* Movement = Character->GetCharacterMovement();
	if (!bAirHang)
	{
		SavedGravityScale = Movement->GravityScale;
		bAirHang = true;
	}
	Movement->GravityScale = SavedGravityScale * Profile->AirHangGravityScale;
	Movement->Velocity.Z = FMath::Max(Movement->Velocity.Z, 0.0f);
	World->GetTimerManager().SetTimer(AirHangTimer, FTimerDelegate::CreateWeakLambda(this, [this]() { EndAirHang(); }),
		Profile->AirHangTime, false);
}

void UJDGA_LightAttack::EndAirHang()
{
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(AirHangTimer);
	}
	if (!bAirHang)
	{
		return;
	}
	bAirHang = false;
	if (ACharacter* Character = Cast<ACharacter>(GetAvatarActorFromActorInfo()))
	{
		Character->GetCharacterMovement()->GravityScale = SavedGravityScale;
	}
}

void UJDGA_LightAttack::PlayStep(int32 Index)
{
	UJDCombatComponent* Combat = GetCombat();
	const UJDCombatProfile* Profile = Combat ? Combat->GetCombatProfile() : nullptr;
	if (!Profile || !Profile->LightCombo.IsValidIndex(Index) || !Profile->LightCombo[Index].Montage)
	{
		EndAbility(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, true, true);
		return;
	}
	PlayAttack(Profile->LightCombo[Index], true);
}

void UJDGA_LightAttack::PlayAttack(const FJDAttackStep& Step, bool bFaceInput)
{
	UJDCombatComponent* Combat = GetCombat();
	if (!Combat || !Step.Montage)
	{
		EndAbility(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, true, true);
		return;
	}

	// Montage langkah sebelumnya digantikan: lepas callback-nya dulu supaya interupsi ini tidak mengakhiri ability.
	if (MontageTask)
	{
		MontageTask->OnCompleted.RemoveAll(this);
		MontageTask->OnBlendOut.RemoveAll(this);
		MontageTask->OnInterrupted.RemoveAll(this);
		MontageTask->OnCancelled.RemoveAll(this);
		MontageTask->EndTask();
		MontageTask = nullptr;
	}
	if (MoveTask)
	{
		MoveTask->EndTask();
		MoveTask = nullptr;
	}
	if (UAbilitySystemComponent* ASC = GetAbilitySystemComponentFromActorInfo())
	{
		ASC->SetLooseGameplayTagCount(JDGameplayTags::State_Combat_ComboWindow, 0);
	}

	if (bFaceInput)
	{
		FaceInputDirection();
	}
	Combat->BeginAttack(Step);
	Combat->SetLightComboStep(ComboIndex);

	MontageTask = UAbilityTask_PlayMontageAndWait::CreatePlayMontageAndWaitProxy(this, NAME_None, Step.Montage, GetMontageRate(Step.PlayRate));
	MontageTask->OnBlendOut.AddDynamic(this, &UJDGA_LightAttack::OnMontageFinished);
	MontageTask->OnCompleted.AddDynamic(this, &UJDGA_LightAttack::OnMontageFinished);
	MontageTask->OnInterrupted.AddDynamic(this, &UJDGA_LightAttack::OnMontageInterrupted);
	MontageTask->OnCancelled.AddDynamic(this, &UJDGA_LightAttack::OnMontageInterrupted);
	MontageTask->ReadyForActivation();

	ACharacter* Character = Cast<ACharacter>(GetAvatarActorFromActorInfo());
	float Distance = Step.MoveDistance;
	if (Step.bStopAtTarget && Distance > 0.0f && Character)
	{
		const UJDCombatProfile* Profile = Combat->GetCombatProfile();
		const float ToTarget = OpenerTarget.IsValid() ? FVector::Dist2D(Character->GetActorLocation(), OpenerTarget->GetActorLocation()) : Distance;
		Distance = FMath::Clamp(ToTarget - (Profile ? Profile->LungeStopDistance : 0.0f), 0.0f, Distance);
	}
	if (Character && !FMath::IsNearlyZero(Distance))
	{
		// Override root motion animasi selama MoveDuration (sama dengan dodge), lalu kecepatan dijepit supaya tidak meluncur.
		const FVector Direction = Character->GetActorForwardVector().GetSafeNormal2D() * FMath::Sign(Distance);
		const float ClampSpeed = Character->GetCharacterMovement()->MaxWalkSpeed * 0.3f;
		if (Step.MoveHeight > 0.0f)
		{
			// Lompat kecil melengkung ke arah hadap (terjang); selesai saat mendarat atau MoveDuration habis.
			MoveTask = UAbilityTask_ApplyRootMotionJumpForce::ApplyRootMotionJumpForce(
				this, NAME_None, Direction.Rotation(), FMath::Abs(Distance), Step.MoveHeight, Step.MoveDuration,
				Step.MoveDuration * 0.5f, true, ERootMotionFinishVelocityMode::ClampVelocity, FVector::ZeroVector, ClampSpeed,
				nullptr, nullptr);
		}
		else
		{
			MoveTask = UAbilityTask_ApplyRootMotionConstantForce::ApplyRootMotionConstantForce(
				this, NAME_None, Direction, FMath::Abs(Distance) / Step.MoveDuration, Step.MoveDuration, false, nullptr,
				ERootMotionFinishVelocityMode::ClampVelocity, FVector::ZeroVector, ClampSpeed, true);
		}
		MoveTask->ReadyForActivation();
	}
}

void UJDGA_LightAttack::InputPressed(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
	const FGameplayAbilityActivationInfo ActivationInfo)
{
	Super::InputPressed(Handle, ActorInfo, ActivationInfo);

	if (const UWorld* World = GetWorld())
	{
		LastPressTime = World->GetTimeSeconds();
	}
	TryAdvanceCombo();
}

void UJDGA_LightAttack::OnComboWindowChanged(const FGameplayTag Tag, int32 NewCount)
{
	// Jendela baru dibuka notify (di tengah update animasi): sambung di frame berikutnya, bukan di dalam callback.
	UWorld* World = GetWorld();
	if (NewCount > 0 && World)
	{
		World->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this, [this]()
		{
			TryAdvanceCombo();
		}));
	}
}

void UJDGA_LightAttack::TryAdvanceCombo()
{
	const UAbilitySystemComponent* ASC = GetAbilitySystemComponentFromActorInfo();
	const UWorld* World = GetWorld();
	if (!IsActive() || !ASC || !World || !ASC->HasMatchingGameplayTag(JDGameplayTags::State_Combat_ComboWindow))
	{
		return;
	}

	// Tekanan sesaat sebelum jendela dibuka tetap dihitung (buffer input, docs/23 bagian 5).
	const UJDAbilitySystemComponent* JDASC = Cast<UJDAbilitySystemComponent>(ASC);
	const float Buffer = JDASC ? JDASC->GetInputBufferTime() : 0.2f;
	if (World->GetTimeSeconds() - LastPressTime > Buffer)
	{
		return;
	}

	const UJDCombatComponent* Combat = GetCombat();
	const UJDCombatProfile* Profile = Combat ? Combat->GetCombatProfile() : nullptr;
	if (bAirMode)
	{
		if (Combat && Combat->CanAirAttack() && IsAvatarFalling(CurrentActorInfo))
		{
			LastPressTime = -1000.0;
			PlayAirAttack();
		}
		return;
	}
	if (!Profile || ComboIndex + 1 >= Profile->LightCombo.Num())
	{
		return;
	}

	LastPressTime = -1000.0;
	PlayStep(++ComboIndex);
}

void UJDGA_LightAttack::OnMontageFinished()
{
	EndAbility(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, true, false);
}

void UJDGA_LightAttack::OnMontageInterrupted()
{
	EndAbility(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, true, true);
}

void UJDGA_LightAttack::EndAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
	const FGameplayAbilityActivationInfo ActivationInfo, bool bReplicateEndAbility, bool bWasCancelled)
{
	if (IsActive())
	{
		if (UAbilitySystemComponent* ASC = GetAbilitySystemComponentFromActorInfo())
		{
			ASC->RegisterGameplayTagEvent(JDGameplayTags::State_Combat_ComboWindow, EGameplayTagEventType::NewOrRemoved).Remove(ComboWindowHandle);
			ASC->SetLooseGameplayTagCount(JDGameplayTags::State_Combat_ComboWindow, 0);
		}
		ComboWindowHandle.Reset();
		if (UJDCombatComponent* Combat = GetCombat())
		{
			Combat->EndAttack();
			// Dipotong pukulan berat -> langkah ini dipakai memilih cabang finisher (UJDGA_HeavyAttack).
			Combat->SetLightComboStep(INDEX_NONE, bWasCancelled);
		}
		MontageTask = nullptr;
		MoveTask = nullptr;
		OpenerTarget.Reset();
		EndAirHang();
		bAirMode = false;
	}

	Super::EndAbility(Handle, ActorInfo, ActivationInfo, bReplicateEndAbility, bWasCancelled);
}
