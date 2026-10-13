#pragma once

#include "CoreMinimal.h"
#include "Abilities/JDGameplayAbility.h"
#include "JDGA_HeavyAttack.generated.h"

class UAbilityTask_PlayMontageAndWait;

/**
 * Pukulan berat (docs/23 Iterasi 3): satu serangan dari UJDCombatProfile::HeavyAttack, makan stamina, tanpa charge di F1.
 * Bisa dimulai dari diam, dari jendela combo ringan (memotong combo), atau dari recovery serangan lain.
 */
UCLASS()
class JAYADWARA_API UJDGA_HeavyAttack : public UJDGameplayAbility
{
	GENERATED_BODY()

public:
	UJDGA_HeavyAttack();

	virtual bool CanActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
		const FGameplayTagContainer* SourceTags, const FGameplayTagContainer* TargetTags, FGameplayTagContainer* OptionalRelevantTags) const override;
	virtual void ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
		const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData) override;
	virtual void EndAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
		const FGameplayAbilityActivationInfo ActivationInfo, bool bReplicateEndAbility, bool bWasCancelled) override;

private:
	UFUNCTION()
	void OnMontageFinished();

	UFUNCTION()
	void OnMontageInterrupted();
};
