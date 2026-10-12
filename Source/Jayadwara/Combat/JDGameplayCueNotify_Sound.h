#pragma once

#include "CoreMinimal.h"
#include "GameplayCueNotify_Static.h"
#include "JDGameplayCueNotify_Sound.generated.h"

class USoundBase;

/**
 * Gameplay Cue sekali-bunyi (docs/23 R5): putar salah satu Sounds secara acak di titik kena, pitch acak tipis.
 * Dipakai lewat Blueprint turunan GC_* di /Game/Jayadwara/Abilities/GameplayCues (Gameplay Cue Tag di Class Defaults),
 * dibuat Tools/ue_setup_combat.py. Ganti SFX placeholder -> final cukup mengganti isi Sounds.
 */
UCLASS(Blueprintable)
class JAYADWARA_API UJDGameplayCueNotify_Sound : public UGameplayCueNotify_Static
{
	GENERATED_BODY()

public:
	virtual bool OnExecute_Implementation(AActor* MyTarget, const FGameplayCueParameters& Parameters) const override;

	/** Variasi suara; satu dipilih acak tiap kali. */
	UPROPERTY(EditDefaultsOnly, Category = "Sound")
	TArray<TObjectPtr<USoundBase>> Sounds;

	UPROPERTY(EditDefaultsOnly, Category = "Sound", meta = (ClampMin = "0"))
	float VolumeMultiplier = 1.0f;

	/** Pitch acak antara X dan Y (raksasa: turunkan, mis. 0,6-0,7). */
	UPROPERTY(EditDefaultsOnly, Category = "Sound")
	FVector2D PitchRange = FVector2D(0.94f, 1.06f);
};
