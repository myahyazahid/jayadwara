#pragma once

#include "CoreMinimal.h"
#include "Abilities/JDGameplayAbility.h"
#include "JDGA_LightAttack.generated.h"

class UAbilityTask_PlayMontageAndWait;
class UJDCombatComponent;

/**
 * Combo pukulan ringan (docs/23 Iterasi 2). Dipakai manusia & raksasa; montage, damage, dan rasa dari
 * UJDCombatProfile::LightCombo milik karakter.
 *
 * Tiap langkah = satu montage. Tekan pukulan ringan lagi selama JD Combo Window (atau sesaat sebelumnya, sebatas
 * buffer input ASC) -> langkah berikutnya. Berhenti menekan -> montage selesai -> ability berakhir. Arah pukulan:
 * arah input gerak saat langkah dimulai (soft target menyusul di Iterasi 4).
 */
UCLASS()
class JAYADWARA_API UJDGA_LightAttack : public UJDGameplayAbility
{
	GENERATED_BODY()

public:
	UJDGA_LightAttack();

	virtual bool CanActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
		const FGameplayTagContainer* SourceTags, const FGameplayTagContainer* TargetTags, FGameplayTagContainer* OptionalRelevantTags) const override;
	virtual void ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
		const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData) override;
	virtual void EndAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
		const FGameplayAbilityActivationInfo ActivationInfo, bool bReplicateEndAbility, bool bWasCancelled) override;
	virtual void InputPressed(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
		const FGameplayAbilityActivationInfo ActivationInfo) override;

private:
	UJDCombatComponent* GetCombat() const;
	void PlayStep(int32 Index);
	void TryAdvanceCombo();
	void FaceInputDirection() const;
	void OnComboWindowChanged(const FGameplayTag Tag, int32 NewCount);

	UFUNCTION()
	void OnMontageFinished();

	UFUNCTION()
	void OnMontageInterrupted();

	UPROPERTY(Transient)
	TObjectPtr<UAbilityTask_PlayMontageAndWait> MontageTask;

	int32 ComboIndex = 0;
	double LastPressTime = -1000.0;
	FDelegateHandle ComboWindowHandle;
};
