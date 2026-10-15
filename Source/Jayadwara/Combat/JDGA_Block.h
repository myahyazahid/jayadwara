#pragma once

#include "CoreMinimal.h"
#include "Abilities/JDGameplayAbility.h"
#include "JDGA_Block.generated.h"

class UAnimMontage;

/**
 * Tangkis (tahan) + parry (tekan tepat waktu), satu tombol (docs/23 Iterasi 3, Q5). Aktif selama tombol ditahan
 * (WhileInputActive): State.Blocking, jalan melambat, pose BlockMontage ditahan. Setiap tekanan membuka
 * State.ParryWindow selama ParryWindow detik (tetap berjalan walau tombol cepat dilepas), kecuali ditekan lagi dalam
 * ParryLockout setelah tekanan sebelumnya. Hasil serangan (kurangi damage, stamina, guard break, parry) diputuskan
 * UJDCombatComponent::ResolveIncomingHit milik penangkis.
 */
UCLASS()
class JAYADWARA_API UJDGA_Block : public UJDGameplayAbility
{
	GENERATED_BODY()

public:
	UJDGA_Block();

	virtual bool CanActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
		const FGameplayTagContainer* SourceTags, const FGameplayTagContainer* TargetTags, FGameplayTagContainer* OptionalRelevantTags) const override;
	virtual void ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
		const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData) override;
	virtual void EndAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
		const FGameplayAbilityActivationInfo ActivationInfo, bool bReplicateEndAbility, bool bWasCancelled) override;
	virtual void InputReleased(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
		const FGameplayAbilityActivationInfo ActivationInfo) override;

private:
	void OpenParryWindow(float Duration);
	void CloseParryWindow();

	FTimerHandle ParryTimer;
	double LastPressTime = -1000.0;
	float SavedMaxWalkSpeed = 0.0f;

	UPROPERTY(Transient)
	TObjectPtr<UAnimMontage> PlayingMontage;
};
