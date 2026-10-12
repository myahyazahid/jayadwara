#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "GameplayTagContainer.h"
#include "JDCombatProfile.generated.h"

class UAnimMontage;
class UCameraShakeBase;

/** Satu langkah serangan: montage + besaran damage. */
USTRUCT(BlueprintType)
struct FJDAttackStep
{
	GENERATED_BODY()

	/** Montage berisi notify JD Hit Window (+ JD Combo Window kalau bisa disambung). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack")
	TObjectPtr<UAnimMontage> Montage = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack", meta = (ClampMin = "0"))
	float Damage = 10.0f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack", meta = (ClampMin = "0"))
	float PoiseDamage = 5.0f;

	/** Gameplay Cue saat kena (SFX/VFX). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack", meta = (Categories = "GameplayCue"))
	FGameplayTag HitCue;
};

/**
 * Combat per skala (docs/12 "Combat (satu sistem, dua skala)", docs/23 bagian 5). Ability combat sama untuk Aksa dan
 * Jayadwara; yang berbeda hanya isi profil ini: montage, laju montage, radius hitbox, damage, hit-stop, shake.
 * Aset: DA_CombatProfile_Human (Iterasi 2), DA_CombatProfile_Giant (Iterasi 6).
 */
UCLASS(BlueprintType, Const)
class JAYADWARA_API UJDCombatProfile : public UDataAsset
{
	GENERATED_BODY()

public:
	/** Combo pukulan ringan, berurutan (docs/23: 3 pukulan, damage 10 / 10 / 18). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Light Combo", meta = (TitleProperty = "Montage"))
	TArray<FJDAttackStep> LightCombo;

	/** Laju semua montage serangan (manusia 1,0; raksasa ±0,55). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Animation", meta = (ClampMin = "0.05"))
	float MontagePlayRate = 1.0f;

	/** Radius sphere trace hitbox (cm) kalau notify tidak menimpa. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Hit", meta = (ClampMin = "1"))
	float HitRadius = 30.0f;

	/** Lama hit-stop (s, waktu dunia): penyerang & korban nyaris berhenti sesaat. 0 = tanpa hit-stop. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Hit|Feel", meta = (ClampMin = "0"))
	float HitStopDuration = 0.06f;

	/** Time dilation lokal selama hit-stop. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Hit|Feel", meta = (ClampMin = "0.001", ClampMax = "1"))
	float HitStopTimeDilation = 0.05f;

	/** Shake kamera pemain saat pukulannya kena (kosong = tanpa shake). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Hit|Feel")
	TSubclassOf<UCameraShakeBase> HitCameraShake;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Hit|Feel", meta = (ClampMin = "0"))
	float HitCameraShakeScale = 1.0f;
};
