#include "Abilities/JDGameplayAbility.h"

#include "Abilities/JDAbilitySystemComponent.h"
#include "AbilitySystemComponent.h"
#include "Characters/JDCharacterBase.h"

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
