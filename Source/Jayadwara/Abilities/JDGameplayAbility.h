#pragma once

#include "CoreMinimal.h"
#include "Abilities/GameplayAbility.h"
#include "JDGameplayAbility.generated.h"

class AJDCharacterBase;
class UJDAbilitySystemComponent;
class UJDCombatComponent;
class UJDCombatProfile;

/** Kapan ability yang terikat input tag diaktifkan. */
UENUM(BlueprintType)
enum class EJDAbilityActivationPolicy : uint8
{
	/** Sekali saat tombol ditekan (pukulan, dodge). Kalau gagal (mis. masih menyerang), tekanan di-buffer sebentar. */
	OnInputTriggered,

	/** Terus dicoba selama tombol ditahan (tangkis). */
	WhileInputActive,

	/** Langsung aktif saat diberikan (pasif). */
	OnSpawn
};

/**
 * Basis semua ability Jayadwara (docs/23 bagian 4.1). Dipakai manusia dan raksasa; perbedaan skala lewat
 * UJDCombatProfile (Iterasi 2). Helper combat (profil, laju montage, arah input, stamina) dipakai ability combat.
 */
UCLASS(Abstract)
class JAYADWARA_API UJDGameplayAbility : public UGameplayAbility
{
	GENERATED_BODY()

public:
	UJDGameplayAbility();

	EJDAbilityActivationPolicy GetActivationPolicy() const { return ActivationPolicy; }

	UFUNCTION(BlueprintPure, Category = "Ability")
	AJDCharacterBase* GetJDCharacter() const;

	UFUNCTION(BlueprintPure, Category = "Ability")
	UJDAbilitySystemComponent* GetJDAbilitySystemComponent() const;

	virtual void OnGiveAbility(const FGameplayAbilityActorInfo* ActorInfo, const FGameplayAbilitySpec& Spec) override;

protected:
	UJDCombatComponent* GetCombat() const;
	const UJDCombatProfile* GetCombatProfile() const;
	static const UJDCombatProfile* GetCombatProfile(const FGameplayAbilityActorInfo* ActorInfo);

	/**
	 * Laju montage yang membuat animasi terlihat berjalan pada Profile->MontagePlayRate x StepRate. Mesh raksasa sudah
	 * diperlambat GlobalAnimRateScale (speed / skala, ±0,6 ala Mebius, untuk locomotion), jadi dikompensasi di sini.
	 */
	float GetMontageRate(float StepRate = 1.0f) const;

	/** Putar avatar ke arah input gerak (kalau ada). */
	void FaceInputDirection() const;

	/** Arah input gerak di bidang datar (ternormalisasi), nol kalau tidak ada input. */
	FVector GetInputDirection2D() const;

	/** Gagal aktif kalau Stamina < Cost (docs/23 Iterasi 3: tidak bisa spam dodge/tangkis/berat). */
	static bool HasStamina(const FGameplayAbilityActorInfo* ActorInfo, float Cost);
	void SpendStamina(float Cost) const;

	/** Avatar sedang melompat/jatuh (serangan udara; dodge & tangkis tidak bisa di udara). */
	static bool IsAvatarFalling(const FGameplayAbilityActorInfo* ActorInfo);

	/** Batalkan ability lain milik avatar yang punya salah satu tag ini. */
	void CancelAbilitiesWithAnyTag(std::initializer_list<FGameplayTag> Tags);

	/** Serangan avatar sedang berjalan tapi frame hit-nya sudah lewat (recovery) -> boleh dibatalkan dodge/tangkis. */
	static bool IsAttackCancelable(const FGameplayAbilityActorInfo* ActorInfo);

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Ability|Activation")
	EJDAbilityActivationPolicy ActivationPolicy = EJDAbilityActivationPolicy::OnInputTriggered;
};
