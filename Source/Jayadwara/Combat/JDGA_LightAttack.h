#pragma once

#include "CoreMinimal.h"
#include "Abilities/JDGameplayAbility.h"
#include "JDGA_LightAttack.generated.h"

class UAbilityTask_ApplyRootMotionConstantForce;
class UAbilityTask_PlayMontageAndWait;
struct FJDAttackStep;

/**
 * Combo pukulan ringan (docs/23 Iterasi 2). Dipakai manusia & raksasa; montage, damage, dan rasa dari
 * UJDCombatProfile::LightCombo milik karakter.
 *
 * Tiap langkah = satu montage. Tekan pukulan ringan lagi selama JD Combo Window (atau sesaat sebelumnya, sebatas
 * buffer input ASC) -> langkah berikutnya. Berhenti menekan -> montage selesai -> ability berakhir. Arah pukulan:
 * arah input gerak saat langkah dimulai (soft target menyusul di Iterasi 4). Tidak bisa dimulai saat serangan lain
 * (pukulan berat) masih berjalan; tekanannya di-buffer ASC.
 *
 * Arah (docs/07 "Combo & arah"): saat combo dimulai, arah input dibandingkan dengan arah ke target terdekat. Maju +
 * target jauh -> LungeAttack (terjang ke target), mundur -> BackAttack; keduanya menggantikan langkah 1 dan combo
 * berlanjut dari langkah 2. Kiri/kanan atau tanpa target -> combo biasa.
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
	/** Pembuka sesuai arah input relatif ke target (nullptr = langkah 1 biasa). Memutar avatar ke target bila ada. */
	const FJDAttackStep* ChooseOpener();
	void PlayStep(int32 Index);
	void PlayAttack(const FJDAttackStep& Step, bool bFaceInput);
	void TryAdvanceCombo();
	void OnComboWindowChanged(const FGameplayTag Tag, int32 NewCount);

	UFUNCTION()
	void OnMontageFinished();

	UFUNCTION()
	void OnMontageInterrupted();

	UPROPERTY(Transient)
	TObjectPtr<UAbilityTask_PlayMontageAndWait> MontageTask;

	UPROPERTY(Transient)
	TObjectPtr<UAbilityTask_ApplyRootMotionConstantForce> MoveTask;

	TWeakObjectPtr<AActor> OpenerTarget;

	int32 ComboIndex = 0;
	double LastPressTime = -1000.0;
	FDelegateHandle ComboWindowHandle;
};
