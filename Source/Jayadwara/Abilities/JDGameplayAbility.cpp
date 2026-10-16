#include "Abilities/JDGameplayAbility.h"

#include "Abilities/JDAbilitySystemComponent.h"
#include "Abilities/JDAttributeSet.h"
#include "Abilities/JDGameplayTags.h"
#include "AbilitySystemComponent.h"
#include "Characters/JDCharacterBase.h"
#include "Combat/JDCombatComponent.h"
#include "Combat/JDCombatProfile.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"

UJDGameplayAbility::UJDGameplayAbility()
{
	InstancingPolicy = EGameplayAbilityInstancingPolicy::InstancedPerActor;
	// Single-player: tidak perlu prediksi klien-server.
	NetExecutionPolicy = EGameplayAbilityNetExecutionPolicy::LocalOnly;
}

AJDCharacterBase* UJDGameplayAbility::GetJDCharacter() const
{
	return Cast<AJDCharacterBase>(GetAvatarActorFromActorInfo());
}

UJDAbilitySystemComponent* UJDGameplayAbility::GetJDAbilitySystemComponent() const
{
	return Cast<UJDAbilitySystemComponent>(GetAbilitySystemComponentFromActorInfo());
}

void UJDGameplayAbility::OnGiveAbility(const FGameplayAbilityActorInfo* ActorInfo, const FGameplayAbilitySpec& Spec)
{
	Super::OnGiveAbility(ActorInfo, Spec);

	if (ActivationPolicy == EJDAbilityActivationPolicy::OnSpawn && ActorInfo && !Spec.IsActive())
	{
		ActorInfo->AbilitySystemComponent->TryActivateAbility(Spec.Handle);
	}
}

UJDCombatComponent* UJDGameplayAbility::GetCombat() const
{
	const AActor* Avatar = GetAvatarActorFromActorInfo();
	return Avatar ? Avatar->FindComponentByClass<UJDCombatComponent>() : nullptr;
}

const UJDCombatProfile* UJDGameplayAbility::GetCombatProfile() const
{
	return GetCombatProfile(CurrentActorInfo);
}

const UJDCombatProfile* UJDGameplayAbility::GetCombatProfile(const FGameplayAbilityActorInfo* ActorInfo)
{
	const AActor* Avatar = ActorInfo ? ActorInfo->AvatarActor.Get() : nullptr;
	const UJDCombatComponent* Combat = Avatar ? Avatar->FindComponentByClass<UJDCombatComponent>() : nullptr;
	return Combat ? Combat->GetCombatProfile() : nullptr;
}

float UJDGameplayAbility::GetMontageRate(float StepRate) const
{
	const UJDCombatProfile* Profile = GetCombatProfile();
	const ACharacter* Character = Cast<ACharacter>(GetAvatarActorFromActorInfo());
	const float MeshRate = Character && Character->GetMesh() ? Character->GetMesh()->GlobalAnimRateScale : 1.0f;
	return (Profile ? Profile->MontagePlayRate : 1.0f) * StepRate / FMath::Max(MeshRate, 0.01f);
}

FVector UJDGameplayAbility::GetInputDirection2D() const
{
	const ACharacter* Character = Cast<ACharacter>(GetAvatarActorFromActorInfo());
	if (!Character)
	{
		return FVector::ZeroVector;
	}
	FVector Direction = Character->GetPendingMovementInputVector();
	if (Direction.IsNearlyZero())
	{
		Direction = Character->GetLastMovementInputVector();
	}
	Direction.Z = 0.0f;
	return Direction.SizeSquared() > 0.01f ? Direction.GetSafeNormal() : FVector::ZeroVector;
}

void UJDGameplayAbility::FaceInputDirection() const
{
	AActor* Avatar = GetAvatarActorFromActorInfo();
	const FVector Direction = GetInputDirection2D();
	if (Avatar && !Direction.IsZero())
	{
		Avatar->SetActorRotation(FRotator(0.0f, Direction.Rotation().Yaw, 0.0f));
	}
}

bool UJDGameplayAbility::HasStamina(const FGameplayAbilityActorInfo* ActorInfo, float Cost)
{
	const UAbilitySystemComponent* ASC = ActorInfo ? ActorInfo->AbilitySystemComponent.Get() : nullptr;
	return Cost <= 0.0f || (ASC && ASC->GetNumericAttribute(UJDAttributeSet::GetStaminaAttribute()) >= Cost);
}

void UJDGameplayAbility::SpendStamina(float Cost) const
{
	if (UAbilitySystemComponent* ASC = GetAbilitySystemComponentFromActorInfo(); ASC && Cost > 0.0f)
	{
		// Lewat base value: delegate perubahan Stamina memicu jeda regen di UJDAbilitySystemComponent.
		ASC->ApplyModToAttribute(UJDAttributeSet::GetStaminaAttribute(), EGameplayModOp::Additive, -Cost);
	}
}

bool UJDGameplayAbility::IsAvatarFalling(const FGameplayAbilityActorInfo* ActorInfo)
{
	const ACharacter* Character = ActorInfo ? Cast<ACharacter>(ActorInfo->AvatarActor.Get()) : nullptr;
	return Character && Character->GetCharacterMovement() && Character->GetCharacterMovement()->IsFalling();
}

void UJDGameplayAbility::CancelAbilitiesWithAnyTag(std::initializer_list<FGameplayTag> Tags)
{
	UAbilitySystemComponent* ASC = GetAbilitySystemComponentFromActorInfo();
	if (!ASC)
	{
		return;
	}
	for (const FGameplayTag& Tag : Tags)
	{
		const FGameplayTagContainer WithTag(Tag);
		ASC->CancelAbilities(&WithTag, nullptr, this);
	}
}

bool UJDGameplayAbility::IsAttackCancelable(const FGameplayAbilityActorInfo* ActorInfo)
{
	const UAbilitySystemComponent* ASC = ActorInfo ? ActorInfo->AbilitySystemComponent.Get() : nullptr;
	if (!ASC || !ASC->HasMatchingGameplayTag(JDGameplayTags::State_Attacking))
	{
		return true;
	}
	const AActor* Avatar = ActorInfo->AvatarActor.Get();
	const UJDCombatComponent* Combat = Avatar ? Avatar->FindComponentByClass<UJDCombatComponent>() : nullptr;
	return Combat && Combat->IsInAttackRecovery();
}
