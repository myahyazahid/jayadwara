#pragma once

#include "CoreMinimal.h"
#include "ActiveGameplayEffectHandle.h"
#include "Engine/DataAsset.h"
#include "GameplayAbilitySpecHandle.h"
#include "GameplayTagContainer.h"
#include "JDAbilitySet.generated.h"

class UGameplayEffect;
class UJDAbilitySystemComponent;
class UJDGameplayAbility;

/** Ability yang diberikan, opsional terikat input tag. */
USTRUCT(BlueprintType)
struct FJDAbilitySet_Ability
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, Category = "Ability")
	TSubclassOf<UJDGameplayAbility> Ability;

	UPROPERTY(EditAnywhere, Category = "Ability")
	int32 AbilityLevel = 1;

	/** Kosong = tidak dipicu input (mis. HitReact dari event). */
	UPROPERTY(EditAnywhere, Category = "Ability", meta = (Categories = "Input"))
	FGameplayTag InputTag;
};

/** GE tambahan yang dipasang saat set diberikan (pasif, buff awal). */
USTRUCT(BlueprintType)
struct FJDAbilitySet_Effect
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, Category = "Effect")
	TSubclassOf<UGameplayEffect> Effect;

	UPROPERTY(EditAnywhere, Category = "Effect")
	float EffectLevel = 1.0f;
};

/** Nilai awal atribut (Max = nilai awal) + regen stamina. 0 = atribut tidak dipakai karakter ini. */
USTRUCT(BlueprintType)
struct FJDAttributeDefaults
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, Category = "Attributes", meta = (ClampMin = "0"))
	float MaxHealth = 100.0f;

	UPROPERTY(EditAnywhere, Category = "Attributes", meta = (ClampMin = "0"))
	float MaxStamina = 100.0f;

	UPROPERTY(EditAnywhere, Category = "Attributes", meta = (ClampMin = "0"))
	float MaxPoise = 50.0f;

	/** Hanya Jayadwara. */
	UPROPERTY(EditAnywhere, Category = "Attributes", meta = (ClampMin = "0"))
	float MaxSync = 0.0f;

	/** Hanya Aksa; awal penuh (docs/23 bagian 4.5: tombol transformasi bebas di level uji). */
	UPROPERTY(EditAnywhere, Category = "Attributes", meta = (ClampMin = "0"))
	float MaxTransformEnergy = 0.0f;

	/** Stamina per detik setelah jeda (docs/23 bagian 5: 25/s). 0 = tanpa regen. */
	UPROPERTY(EditAnywhere, Category = "Attributes|Stamina", meta = (ClampMin = "0"))
	float StaminaRegenPerSecond = 25.0f;

	/** Jeda setelah stamina terpakai sebelum regen mulai (s). */
	UPROPERTY(EditAnywhere, Category = "Attributes|Stamina", meta = (ClampMin = "0"))
	float StaminaRegenDelay = 0.8f;

	/** Poise per detik setelah jeda tanpa kena (docs/23 Iterasi 4: 20/s). 0 = tanpa regen. */
	UPROPERTY(EditAnywhere, Category = "Attributes|Poise", meta = (ClampMin = "0"))
	float PoiseRegenPerSecond = 20.0f;

	/** Jeda setelah poise berkurang sebelum regen mulai (s). */
	UPROPERTY(EditAnywhere, Category = "Attributes|Poise", meta = (ClampMin = "0"))
	float PoiseRegenDelay = 1.5f;
};

/** Yang sudah diberikan, untuk dicabut lagi (mis. ganti set). */
USTRUCT()
struct FJDAbilitySet_GrantedHandles
{
	GENERATED_BODY()

	TArray<FGameplayAbilitySpecHandle> AbilityHandles;
	TArray<FActiveGameplayEffectHandle> EffectHandles;

	void TakeFromAbilitySystem(UJDAbilitySystemComponent* ASC);
};

/**
 * Paket awal satu karakter (docs/23 bagian 4.1): atribut awal, ability (+ input tag), GE pasif, buffer input.
 * Aset: DA_AbilitySet_Aksa (Iterasi 1), DA_AbilitySet_Jayadwara (Iterasi 6), minion & boss (Iterasi 5, 8).
 */
UCLASS(BlueprintType, Const)
class JAYADWARA_API UJDAbilitySet : public UDataAsset
{
	GENERATED_BODY()

public:
	/** Terapkan atribut awal, regen, GE, dan ability ke ASC. OutHandles boleh null. */
	void GiveToAbilitySystem(UJDAbilitySystemComponent* ASC, FJDAbilitySet_GrantedHandles* OutHandles = nullptr) const;

	UPROPERTY(EditAnywhere, Category = "Attributes")
	FJDAttributeDefaults Attributes;

	UPROPERTY(EditAnywhere, Category = "Abilities", meta = (TitleProperty = "Ability"))
	TArray<FJDAbilitySet_Ability> Abilities;

	UPROPERTY(EditAnywhere, Category = "Effects", meta = (TitleProperty = "Effect"))
	TArray<FJDAbilitySet_Effect> Effects;

	/** Tekanan tombol yang gagal (mis. animasi masih jalan) dicoba ulang selama ini (s). Manusia 0,2; raksasa 0,3. */
	UPROPERTY(EditAnywhere, Category = "Input", meta = (ClampMin = "0"))
	float InputBufferTime = 0.2f;
};
