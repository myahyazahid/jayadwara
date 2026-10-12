#pragma once

#include "CoreMinimal.h"
#include "AbilitySystemComponent.h"
#include "AttributeSet.h"
#include "JDAttributeSet.generated.h"

/** Health habis. Instigator = pelaku damage terakhir (boleh null, mis. cheat). */
DECLARE_MULTICAST_DELEGATE_TwoParams(FJDOutOfHealthEvent, AActor* /*Instigator*/, float /*DamageAmount*/);

/**
 * Satu set atribut untuk semua karakter (docs/12 "Attribute", docs/23 bagian 4.1). Atribut yang tidak dipakai suatu
 * karakter bernilai 0 (mis. Sync untuk Aksa, TransformEnergy untuk Jayadwara & musuh).
 * Nilai awal di-set UJDGE_InitAttributes dari UJDAbilitySet. Damage masuk lewat meta-attribute IncomingDamage /
 * IncomingPoiseDamage (UJDGE_Damage), tidak langsung ke Health, supaya God mode, tangkis, dll. punya satu pintu.
 * Single-player: atribut tidak direplikasi.
 */
UCLASS()
class JAYADWARA_API UJDAttributeSet : public UAttributeSet
{
	GENERATED_BODY()

public:
	ATTRIBUTE_ACCESSORS_BASIC(UJDAttributeSet, Health)
	ATTRIBUTE_ACCESSORS_BASIC(UJDAttributeSet, MaxHealth)
	ATTRIBUTE_ACCESSORS_BASIC(UJDAttributeSet, Stamina)
	ATTRIBUTE_ACCESSORS_BASIC(UJDAttributeSet, MaxStamina)
	ATTRIBUTE_ACCESSORS_BASIC(UJDAttributeSet, Poise)
	ATTRIBUTE_ACCESSORS_BASIC(UJDAttributeSet, MaxPoise)
	ATTRIBUTE_ACCESSORS_BASIC(UJDAttributeSet, Sync)
	ATTRIBUTE_ACCESSORS_BASIC(UJDAttributeSet, MaxSync)
	ATTRIBUTE_ACCESSORS_BASIC(UJDAttributeSet, TransformEnergy)
	ATTRIBUTE_ACCESSORS_BASIC(UJDAttributeSet, MaxTransformEnergy)
	ATTRIBUTE_ACCESSORS_BASIC(UJDAttributeSet, IncomingDamage)
	ATTRIBUTE_ACCESSORS_BASIC(UJDAttributeSet, IncomingPoiseDamage)

	virtual void PreAttributeBaseChange(const FGameplayAttribute& Attribute, float& NewValue) const override;
	virtual void PreAttributeChange(const FGameplayAttribute& Attribute, float& NewValue) override;
	virtual void PostGameplayEffectExecute(const FGameplayEffectModCallbackData& Data) override;

	/** Dipanggil saat damage membuat Health turun dari > 0 ke 0. */
	mutable FJDOutOfHealthEvent OnOutOfHealth;

	UPROPERTY(BlueprintReadOnly, Category = "Attributes|Health")
	FGameplayAttributeData Health;

	UPROPERTY(BlueprintReadOnly, Category = "Attributes|Health")
	FGameplayAttributeData MaxHealth;

	/** Biaya dodge, tangkis, pukulan berat; regen lewat UJDAbilitySystemComponent (jeda setelah dipakai). */
	UPROPERTY(BlueprintReadOnly, Category = "Attributes|Stamina")
	FGameplayAttributeData Stamina;

	UPROPERTY(BlueprintReadOnly, Category = "Attributes|Stamina")
	FGameplayAttributeData MaxStamina;

	/** Habis -> stagger (Iterasi 4). */
	UPROPERTY(BlueprintReadOnly, Category = "Attributes|Poise")
	FGameplayAttributeData Poise;

	UPROPERTY(BlueprintReadOnly, Category = "Attributes|Poise")
	FGameplayAttributeData MaxPoise;

	/** Meter sinkronisasi, hanya Jayadwara (Iterasi 7). */
	UPROPERTY(BlueprintReadOnly, Category = "Attributes|Sync")
	FGameplayAttributeData Sync;

	UPROPERTY(BlueprintReadOnly, Category = "Attributes|Sync")
	FGameplayAttributeData MaxSync;

	/** Energi transformasi, hanya Aksa (docs/23 bagian 4.5, Iterasi 6). */
	UPROPERTY(BlueprintReadOnly, Category = "Attributes|Transform")
	FGameplayAttributeData TransformEnergy;

	UPROPERTY(BlueprintReadOnly, Category = "Attributes|Transform")
	FGameplayAttributeData MaxTransformEnergy;

	/** Meta-attribute: damage yang masuk, dipindah ke Health di PostGameplayEffectExecute. */
	UPROPERTY(BlueprintReadOnly, Category = "Attributes|Meta")
	FGameplayAttributeData IncomingDamage;

	UPROPERTY(BlueprintReadOnly, Category = "Attributes|Meta")
	FGameplayAttributeData IncomingPoiseDamage;

private:
	/** Batasi nilai sekarang ke [0, Max]; nilai Max tidak boleh negatif. */
	void ClampAttribute(const FGameplayAttribute& Attribute, float& NewValue) const;
};
