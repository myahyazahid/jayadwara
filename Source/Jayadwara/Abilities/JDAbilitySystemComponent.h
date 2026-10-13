#pragma once

#include "CoreMinimal.h"
#include "AbilitySystemComponent.h"
#include "JDAbilitySystemComponent.generated.h"

/**
 * ASC Jayadwara (docs/23 bagian 4.1, R1: dipasang di karakter, bukan PlayerState).
 *
 * Input: karakter meneruskan tekan/lepas input tag (UJDInputConfig) ke AbilityInputTagPressed/Released; aktivasi
 * dikerjakan sekali per frame di ProcessAbilityInput (dipanggil AJDPlayerController::PostProcessInput) sesuai
 * EJDAbilityActivationPolicy. Tekanan yang gagal mengaktifkan ability (mis. animasi serangan masih jalan) disimpan
 * sebagai buffer dan dicoba ulang selama InputBufferTime; hanya tekanan terakhir yang diingat.
 *
 * Stamina: regen (UJDGE_StaminaRegen) dilepas setiap Stamina berkurang dan dipasang lagi setelah jeda.
 */
UCLASS(ClassGroup = (Jayadwara), meta = (BlueprintSpawnableComponent))
class JAYADWARA_API UJDAbilitySystemComponent : public UAbilitySystemComponent
{
	GENERATED_BODY()

public:
	UJDAbilitySystemComponent();

	void AbilityInputTagPressed(const FGameplayTag& InputTag);
	void AbilityInputTagReleased(const FGameplayTag& InputTag);

	void ProcessAbilityInput(float DeltaTime, bool bGamePaused);

	/** Lupakan semua input yang ditahan/di-buffer (pawn dilepas, transformasi). */
	void ClearAbilityInput();

	void SetInputBufferTime(float Seconds) { InputBufferTime = FMath::Max(Seconds, 0.0f); }
	float GetInputBufferTime() const { return InputBufferTime; }

	/** Laju regen (per detik) & jeda setelah stamina terpakai. Laju 0 = tanpa regen. */
	void ConfigureStaminaRegen(float PerSecond, float Delay);

	virtual void OnUnregister() override;

protected:
	virtual void AbilitySpecInputPressed(FGameplayAbilitySpec& Spec) override;
	virtual void AbilitySpecInputReleased(FGameplayAbilitySpec& Spec) override;

private:
	void OnStaminaChanged(const FOnAttributeChangeData& Data);
	void StartStaminaRegen();
	void StopStaminaRegen();

	/** Ability yang terikat InputTag (tag ada di dynamic spec source tags, dipasang UJDAbilitySet). */
	void FindSpecsWithInputTag(const FGameplayTag& InputTag, TArray<FGameplayAbilitySpecHandle>& OutHandles) const;

	TArray<FGameplayAbilitySpecHandle> InputPressedSpecHandles;
	TArray<FGameplayAbilitySpecHandle> InputReleasedSpecHandles;
	TArray<FGameplayAbilitySpecHandle> InputHeldSpecHandles;

	FGameplayAbilitySpecHandle BufferedSpecHandle;
	double BufferedAtTime = 0.0;
	float InputBufferTime = 0.2f;

	float StaminaRegenPerSecond = 0.0f;
	float StaminaRegenDelay = 0.8f;
	FActiveGameplayEffectHandle StaminaRegenHandle;
	FTimerHandle StaminaRegenDelayTimer;
	FDelegateHandle StaminaChangedHandle;
};
