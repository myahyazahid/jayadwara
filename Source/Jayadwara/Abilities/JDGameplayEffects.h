#pragma once

#include "CoreMinimal.h"
#include "GameplayEffect.h"
#include "JDGameplayEffects.generated.h"

class UAbilitySystemComponent;

/*
 * Gameplay Effect inti didefinisikan di C++ (docs/23 R4): bisa dibaca & direview, besarannya lewat SetByCaller
 * (tag Data.*) yang diisi dari DataAsset atau kode. Tidak perlu GE_*.uasset untuk efek-efek ini.
 */

/**
 * Nilai awal atribut (Instant, Override). Max* dan nilai sekarang diisi angka yang sama dari SetByCaller
 * Data.Init.Max* (lihat UJDAbilitySet::FJDAttributeDefaults). Max diterapkan sebelum nilai sekarang supaya clamp benar.
 */
UCLASS()
class JAYADWARA_API UJDGE_InitAttributes : public UGameplayEffect
{
	GENERATED_BODY()

public:
	UJDGE_InitAttributes();
};

/**
 * Regen stamina (Infinite, periodik). Besar per tick = SetByCaller Data.StaminaRegen (= laju per detik x TickPeriod).
 * Dipasang & dilepas UJDAbilitySystemComponent: dilepas tiap stamina berkurang, dipasang lagi setelah jeda.
 */
UCLASS()
class JAYADWARA_API UJDGE_StaminaRegen : public UGameplayEffect
{
	GENERATED_BODY()

public:
	UJDGE_StaminaRegen();

	static constexpr float TickPeriod = 0.1f;
};

/**
 * Damage (Instant) ke meta-attribute IncomingDamage & IncomingPoiseDamage; UJDAttributeSet memindahkannya ke Health
 * dan Poise. Pakai MakeSpec supaya kedua SetByCaller selalu terisi.
 */
UCLASS()
class JAYADWARA_API UJDGE_Damage : public UGameplayEffect
{
	GENERATED_BODY()

public:
	UJDGE_Damage();

	/** Spec damage dari Source (pelaku; boleh ASC korban sendiri untuk cheat/lingkungan). */
	static FGameplayEffectSpecHandle MakeSpec(const UAbilitySystemComponent* Source, float Damage, float PoiseDamage = 0.0f);
};
