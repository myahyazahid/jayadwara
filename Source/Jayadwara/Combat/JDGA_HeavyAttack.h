#pragma once

#include "CoreMinimal.h"
#include "Abilities/JDGameplayAbility.h"
#include "JDGA_HeavyAttack.generated.h"

class UAbilityTask_PlayMontageAndWait;
class UAnimMontage;
struct FJDAttackStep;

/**
 * Pukulan berat (docs/23 Iterasi 3): satu serangan dari UJDCombatProfile::HeavyAttack, makan stamina, tanpa charge di F1.
 * Bisa dimulai dari diam, dari jendela combo ringan (memotong combo), atau dari recovery serangan lain. Memotong combo
 * ringan di langkah ke-i memakai UJDCombatProfile::HeavyFinishers[i] kalau ada (cabang finisher).
 *
 * Di udara (docs/07 "Serangan udara"): AirSlam. Menukik lurus ke bawah, saat mendarat gelombang kejut AirSlamRadius
 * (UJDCombatComponent::ApplyAreaHit), lalu jeda AirSlamRecovery. Slot AirSlam kosong = pukulan berat biasa.
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
	void ActivateAirSlam(const FJDAttackStep& Step);
	void StartSlamHang();
	void EndSlamHang();
	/** E yang ditekan sebelum puncak lompatan ditahan dulu, dijalankan saat sudah mentok. */
	void StartApexWait();
	void CheckApex();

	UFUNCTION()
	void OnMontageFinished();

	UFUNCTION()
	void OnMontageInterrupted();

	bool bSlam = false;
	bool bSlamHang = false;
	float SavedGravityScale = 1.0f;
	FTimerHandle HangTimer;
	FTimerHandle ApexTimer;
	float ApexWaitElapsed = 0.0f;
};
