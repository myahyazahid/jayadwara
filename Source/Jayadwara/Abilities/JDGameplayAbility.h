#pragma once

#include "CoreMinimal.h"
#include "Abilities/GameplayAbility.h"
#include "JDGameplayAbility.generated.h"

class AJDCharacterBase;
class UJDAbilitySystemComponent;

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
 * UJDCombatProfile (Iterasi 2). Helper montage & combat profile ditambahkan bersama ability combat pertama.
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
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Ability|Activation")
	EJDAbilityActivationPolicy ActivationPolicy = EJDAbilityActivationPolicy::OnInputTriggered;
};
