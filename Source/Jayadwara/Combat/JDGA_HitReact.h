#pragma once

#include "CoreMinimal.h"
#include "Abilities/JDGameplayAbility.h"
#include "Combat/JDCombatComponent.h"
#include "JDGA_HitReact.generated.h"

class UAnimMontage;

/**
 * Reaksi kena pukul (docs/23 Iterasi 4). Dipicu Gameplay Event Event.HitReact.Light/Stagger/Knockdown yang dikirim
 * UJDCombatComponent::ApplyHitReaction (EventMagnitude > 0 = durasi pengganti, mis. guard break / parry). Diberikan
 * otomatis ke semua AJDCharacterBase; tidak perlu dimasukkan ke DA_AbilitySet_*. Reaksi baru menggantikan yang lama
 * (pengirim tidak pernah menurunkan reaksi: stagger tidak diganti ringan).
 *
 * - Ringan: sentak (HitReactMontages bergantian). Musuh: serangannya batal. Pemain: input tidak dikunci; kalau sedang
 *   menyerang, animasinya tidak diputar supaya serangan tetap jalan.
 * - Stagger: semua ability combat batal, State.Stagger (gerak & aksi dikunci), hadap penyerang, terdorong mundur.
 * - Knockdown: seperti stagger dengan State.Knockdown, lalu bangun dengan State.Invulnerable.
 * Selesai normal setelah stagger/knockdown: poise penuh lagi (bResetPoiseAfterStagger).
 */
UCLASS()
class JAYADWARA_API UJDGA_HitReact : public UJDGameplayAbility
{
	GENERATED_BODY()

public:
	UJDGA_HitReact();

	/** Tag event untuk reaksi ini (None = tag tidak valid). */
	static FGameplayTag GetEventTag(EJDHitReaction Reaction);

	virtual void ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
		const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData) override;
	virtual void EndAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
		const FGameplayAbilityActivationInfo ActivationInfo, bool bReplicateEndAbility, bool bWasCancelled) override;

private:
	static EJDHitReaction GetReactionFromTag(const FGameplayTag& EventTag);

	void BeginLight(const UJDCombatProfile& Profile);
	void BeginStagger(const UJDCombatProfile& Profile, float Duration);
	void BeginKnockdown(const UJDCombatProfile& Profile, float Duration);
	void BeginGetUp();
	void FinishReaction();

	/** Batalkan serangan (ringan) atau semua aksi combat (stagger/knockdown). */
	void InterruptCombat(bool bAllActions);
	void FaceInstigatorAndPush(float PushSpeed);
	void AddStateTag(const FGameplayTag& Tag);
	bool IsPlayerAvatar() const;
	void PlayReactionMontage(UAnimMontage* Montage);
	void StopReactionMontage();

	EJDHitReaction Reaction = EJDHitReaction::None;
	TWeakObjectPtr<const AActor> ReactionInstigator;
	FTimerHandle PhaseTimer;
	TArray<FGameplayTag> AddedTags;
	int32 LightVariant = 0;

	UPROPERTY(Transient)
	TObjectPtr<UAnimMontage> PlayingMontage;
};
