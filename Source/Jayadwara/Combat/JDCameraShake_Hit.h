#pragma once

#include "CoreMinimal.h"
#include "Camera/CameraShakeBase.h"
#include "JDCameraShake_Hit.generated.h"

/**
 * Shake pendek saat pukulan pemain kena (docs/23 Iterasi 2). Perlin noise kecil di rotasi + lokasi, ±0,15 s.
 * Besarnya diskalakan HitCameraShakeScale di UJDCombatProfile (raksasa lebih besar). Bisa dipakai langsung atau
 * dibuat turunan Blueprint untuk tuning.
 */
UCLASS()
class JAYADWARA_API UJDCameraShake_Hit : public UCameraShakeBase
{
	GENERATED_BODY()

public:
	UJDCameraShake_Hit(const FObjectInitializer& ObjectInitializer);
};
