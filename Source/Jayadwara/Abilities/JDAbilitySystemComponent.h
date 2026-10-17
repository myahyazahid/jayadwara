#pragma once

#include "CoreMinimal.h"
#include "AbilitySystemComponent.h"
#include "JDAbilitySystemComponent.generated.h"

/** Satu atribut yang pulih sendiri setelah jeda (stamina, poise); dipakai UJDAbilitySystemComponent. */
struct FJDAttributeRegen
{
	FGameplayAttribute Attribute;
	TSubclassOf<UGameplayEffect> Effect;
	FGameplayTag DataTag;
	float TickPeriod = 0.1f;
	float PerSecond = 0.0f;
	float Delay = 0.0f;
	FActiveGameplayEffectHandle Handle;
	FTimerHandle DelayTimer;
	FDelegateHandle ChangedHandle;
};

namespace JDRegen
{
	enum Index : int32 { Stamina = 0, Poise = 1, Count = 2 };
}

/**
 * ASC Jayadwara (docs/23 bagian 4.1, R1: dipasang di karakter, bukan PlayerState).
 *
 * Input: karakter meneruskan tekan/lepas input tag (UJDInputConfig) ke AbilityInputTagPressed/Released; aktivasi
 * dikerjakan sekali per frame di ProcessAbilityInput (dipanggil AJDPlayerController::PostProcessInput) sesuai
 * EJDAbilityActivationPolicy. Tekanan yang gagal mengaktifkan ability (mis. animasi serangan masih jalan) disimpan
 * sebagai buffer dan dicoba ulang selama InputBufferTime; hanya tekanan terakhir yang diingat.
 *
 * Stamina & poise: regen (UJDGE_StaminaRegen / UJDGE_PoiseRegen) dilepas setiap atributnya berkurang dan dipasang lagi
 * setelah jeda.
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

	/** Laju regen poise (per detik) & jeda setelah kena (docs/23 Iterasi 4). Laju 0 = tanpa regen. */
	void ConfigurePoiseRegen(float PerSecond, float Delay);

	virtual void OnUnregister() override;

protected:
	virtual void AbilitySpecInputPressed(FGameplayAbilitySpec& Spec) override;
	virtual void AbilitySpecInputReleased(FGameplayAbilitySpec& Spec) override;

private:
	void ConfigureRegen(int32 Index, float PerSecond, float Delay);
	void OnRegenAttributeChanged(const FOnAttributeChangeData& Data, int32 Index);
	void StartRegen(int32 Index);
	void StopRegen(int32 Index);

	/** Ability yang terikat InputTag (tag ada di dynamic spec source tags, dipasang UJDAbilitySet). */
	void FindSpecsWithInputTag(const FGameplayTag& InputTag, TArray<FGameplayAbilitySpecHandle>& OutHandles) const;

	TArray<FGameplayAbilitySpecHandle> InputPressedSpecHandles;
	TArray<FGameplayAbilitySpecHandle> InputReleasedSpecHandles;
	TArray<FGameplayAbilitySpecHandle> InputHeldSpecHandles;

	FGameplayAbilitySpecHandle BufferedSpecHandle;
	double BufferedAtTime = 0.0;
	float InputBufferTime = 0.2f;

	FJDAttributeRegen Regens[JDRegen::Count];
};
