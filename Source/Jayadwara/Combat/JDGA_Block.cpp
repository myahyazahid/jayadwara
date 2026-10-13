#include "Combat/JDGA_Block.h"

#include "AbilitySystemComponent.h"
#include "Abilities/JDGameplayTags.h"
#include "Animation/AnimInstance.h"
#include "Combat/JDCombatProfile.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "TimerManager.h"

UJDGA_Block::UJDGA_Block()
{
	ActivationPolicy = EJDAbilityActivationPolicy::WhileInputActive;

	FGameplayTagContainer AssetTags;
	AssetTags.AddTag(JDGameplayTags::Ability_Block);
	SetAssetTags(AssetTags);

	ActivationOwnedTags.AddTag(JDGameplayTags::State_Blocking);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Dead);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Stagger);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Knockdown);
	ActivationBlockedTags.AddTag(JDGameplayTags::State_Dodging);
}

bool UJDGA_Block::CanActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
	const FGameplayTagContainer* SourceTags, const FGameplayTagContainer* TargetTags, FGameplayTagContainer* OptionalRelevantTags) const
{
	return Super::CanActivateAbility(Handle, ActorInfo, SourceTags, TargetTags, OptionalRelevantTags)
		&& GetCombatProfile(ActorInfo) && IsAttackCancelable(ActorInfo);
}

void UJDGA_Block::ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
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

	CancelAbilitiesWithAnyTag({ JDGameplayTags::Ability_Attack_Light, JDGameplayTags::Ability_Attack_Heavy });

	// Parry: tekanan baru membuka jendela, kecuali menekan berulang terlalu cepat (anti spam).
	const double Now = World->GetTimeSeconds();
	if (Now - LastPressTime >= Profile->ParryLockout)
	{
		OpenParryWindow(Profile->ParryWindow);
	}
	LastPressTime = Now;

	UCharacterMovementComponent* Movement = Character->GetCharacterMovement();
	SavedMaxWalkSpeed = Movement->MaxWalkSpeed;
	Movement->MaxWalkSpeed = SavedMaxWalkSpeed * Profile->BlockMoveSpeedScale;

	USkeletalMeshComponent* Mesh = Character->GetMesh();
	UAnimInstance* Anim = Mesh ? Mesh->GetAnimInstance() : nullptr;
	if (Anim && Profile->BlockMontage)
	{
		// Pose diambil dari BlockHoldTime lalu langsung ditahan: tanpa root motion, blend-in tetap berjalan.
		PlayingMontage = Profile->BlockMontage;
		Anim->Montage_Play(PlayingMontage, GetMontageRate(), EMontagePlayReturnType::MontageLength, Profile->BlockHoldTime);
		Anim->Montage_Pause(PlayingMontage);
	}

	// Dilepas sebelum ability sempat aktif (tekan sangat singkat): tetap parry, tangkis langsung selesai.
	if (const FGameplayAbilitySpec* Spec = GetCurrentAbilitySpec(); Spec && !Spec->InputPressed)
	{
		EndAbility(Handle, ActorInfo, ActivationInfo, true, false);
	}
}

void UJDGA_Block::InputReleased(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
	const FGameplayAbilityActivationInfo ActivationInfo)
{
	Super::InputReleased(Handle, ActorInfo, ActivationInfo);
	EndAbility(Handle, ActorInfo, ActivationInfo, true, false);
}

void UJDGA_Block::OpenParryWindow(float Duration)
{
	UAbilitySystemComponent* ASC = GetAbilitySystemComponentFromActorInfo();
	UWorld* World = GetWorld();
	if (!ASC || !World || Duration <= 0.0f)
	{
		return;
	}
	ASC->SetLooseGameplayTagCount(JDGameplayTags::State_ParryWindow, 1);
	// Timer milik dunia, bukan ability: jendela tetap berjalan walau tangkis sudah dilepas.
	TWeakObjectPtr<UAbilitySystemComponent> WeakASC = ASC;
	World->GetTimerManager().SetTimer(ParryTimer, FTimerDelegate::CreateWeakLambda(ASC, [WeakASC]()
	{
		if (WeakASC.IsValid())
		{
			WeakASC->SetLooseGameplayTagCount(JDGameplayTags::State_ParryWindow, 0);
		}
	}), Duration, false);
}

void UJDGA_Block::CloseParryWindow()
{
	if (UAbilitySystemComponent* ASC = GetAbilitySystemComponentFromActorInfo())
	{
		ASC->SetLooseGameplayTagCount(JDGameplayTags::State_ParryWindow, 0);
	}
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(ParryTimer);
	}
}

void UJDGA_Block::EndAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
	const FGameplayAbilityActivationInfo ActivationInfo, bool bReplicateEndAbility, bool bWasCancelled)
{
	if (IsActive())
	{
		// Dibatalkan (dodge, stagger, guard break): jendela parry ikut tutup. Dilepas biasa: jendela berjalan terus.
		if (bWasCancelled)
		{
			CloseParryWindow();
		}
		if (ACharacter* Character = Cast<ACharacter>(GetAvatarActorFromActorInfo()))
		{
			if (SavedMaxWalkSpeed > 0.0f)
			{
				Character->GetCharacterMovement()->MaxWalkSpeed = SavedMaxWalkSpeed;
			}
			UAnimInstance* Anim = Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr;
			if (Anim && PlayingMontage)
			{
				Anim->Montage_Stop(0.2f, PlayingMontage);
			}
		}
		SavedMaxWalkSpeed = 0.0f;
		PlayingMontage = nullptr;
	}
	Super::EndAbility(Handle, ActorInfo, ActivationInfo, bReplicateEndAbility, bWasCancelled);
}
