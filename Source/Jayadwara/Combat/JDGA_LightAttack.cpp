#include "Combat/JDGA_LightAttack.h"

#include "Abilities/JDAbilitySystemComponent.h"
#include "Abilities/JDGameplayTags.h"
#include "Abilities/Tasks/AbilityTask_PlayMontageAndWait.h"
#include "Combat/JDCombatComponent.h"
#include "Combat/JDCombatProfile.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "TimerManager.h"

UJDGA_LightAttack::UJDGA_LightAttack()
{
	ActivationPolicy = EJDAbilityActivationPolicy::OnInputTriggered;

	FGameplayTagContainer AssetTags;
	AssetTags.AddTag(JDGameplayTags::Ability_Attack_Light);
	SetAssetTags(AssetTags);

	ActivationOwnedTags.AddTag(JDGameplayTags::State_Attacking);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Dead);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Stagger);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Knockdown);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Dodging);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Blocking);
}

UJDCombatComponent* UJDGA_LightAttack::GetCombat() const
{
	const AActor* Avatar = GetAvatarActorFromActorInfo();
	return Avatar ? Avatar->FindComponentByClass<UJDCombatComponent>() : nullptr;
}

bool UJDGA_LightAttack::CanActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
	const FGameplayTagContainer* SourceTags, const FGameplayTagContainer* TargetTags, FGameplayTagContainer* OptionalRelevantTags) const
{
	if (!Super::CanActivateAbility(Handle, ActorInfo, SourceTags, TargetTags, OptionalRelevantTags))
	{
		return false;
	}
	const AActor* Avatar = ActorInfo ? ActorInfo->AvatarActor.Get() : nullptr;
	const UJDCombatComponent* Combat = Avatar ? Avatar->FindComponentByClass<UJDCombatComponent>() : nullptr;
	const UJDCombatProfile* Profile = Combat ? Combat->GetCombatProfile() : nullptr;
	return Profile && !Profile->LightCombo.IsEmpty() && Profile->LightCombo[0].Montage;
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

	PlayStep(0);
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
	const FJDAttackStep& Step = Profile->LightCombo[Index];

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
	if (UAbilitySystemComponent* ASC = GetAbilitySystemComponentFromActorInfo())
	{
		ASC->SetLooseGameplayTagCount(JDGameplayTags::State_Combat_ComboWindow, 0);
	}

	FaceInputDirection();
	Combat->BeginAttack(Step);

	MontageTask = UAbilityTask_PlayMontageAndWait::CreatePlayMontageAndWaitProxy(this, NAME_None, Step.Montage, Profile->MontagePlayRate);
	MontageTask->OnBlendOut.AddDynamic(this, &UJDGA_LightAttack::OnMontageFinished);
	MontageTask->OnCompleted.AddDynamic(this, &UJDGA_LightAttack::OnMontageFinished);
	MontageTask->OnInterrupted.AddDynamic(this, &UJDGA_LightAttack::OnMontageInterrupted);
	MontageTask->OnCancelled.AddDynamic(this, &UJDGA_LightAttack::OnMontageInterrupted);
	MontageTask->ReadyForActivation();
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
	if (!Profile || ComboIndex + 1 >= Profile->LightCombo.Num())
	{
		return;
	}

	LastPressTime = -1000.0;
	PlayStep(++ComboIndex);
}

void UJDGA_LightAttack::FaceInputDirection() const
{
	ACharacter* Character = Cast<ACharacter>(GetAvatarActorFromActorInfo());
	if (!Character)
	{
		return;
	}
	FVector Direction = Character->GetPendingMovementInputVector();
	if (Direction.IsNearlyZero())
	{
		Direction = Character->GetLastMovementInputVector();
	}
	Direction.Z = 0.0f;
	if (Direction.SizeSquared() > 0.01f)
	{
		Character->SetActorRotation(FRotator(0.0f, Direction.Rotation().Yaw, 0.0f));
	}
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
		}
		MontageTask = nullptr;
	}

	Super::EndAbility(Handle, ActorInfo, ActivationInfo, bReplicateEndAbility, bWasCancelled);
}
