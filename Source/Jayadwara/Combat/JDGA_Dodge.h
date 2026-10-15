#pragma once

#include "CoreMinimal.h"
#include "Abilities/JDGameplayAbility.h"
#include "JDGA_Dodge.generated.h"

class UAnimMontage;

/**
 * Dodge 4 arah (docs/23 Iterasi 3, Q10). Arah = input gerak (relatif kamera); tanpa input = mundur. Karakter tetap
 * menghadap arah semula, animasi dipilih dari arah relatif hadap (UJDCombatProfile::DodgeMontages, opsional).
 * Gerak dari root motion source (jarak/durasi di profil, jalan juga tanpa animasi), i-frame = State.Invulnerable
 * selama jendela profil, biaya stamina. Bisa membatalkan recovery serangan (setelah frame hit) dan tangkis.
 */
UCLASS()
class JAYADWARA_API UJDGA_Dodge : public UJDGameplayAbility
{
	GENERATED_BODY()

public:
	UJDGA_Dodge();

	virtual bool CanActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
		const FGameplayTagContainer* SourceTags, const FGameplayTagContainer* TargetTags, FGameplayTagContainer* OptionalRelevantTags) const override;
	virtual void ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
		const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData) override;
	virtual void EndAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
		const FGameplayAbilityActivationInfo ActivationInfo, bool bReplicateEndAbility, bool bWasCancelled) override;

private:
	UFUNCTION()
	void OnDodgeFinished();

	void SetInvulnerable(bool bInvulnerable);

	FTimerHandle IFrameStartTimer;
	FTimerHandle IFrameEndTimer;
	bool bInvulnerable = false;
	bool bRestoreOrientToMovement = false;

	UPROPERTY(Transient)
	TObjectPtr<UAnimMontage> PlayingMontage;
};
