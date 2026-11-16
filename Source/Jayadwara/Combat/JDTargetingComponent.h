#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "JDTargetingComponent.generated.h"

class UJDCombatProfile;

/**
 * Soft target & warp ke target (docs/23 Iterasi 4, Q3: soft target gaya Arkham untuk minion; lock-on boss di Iterasi 6).
 * Dipasang di AJDCharacterBase, hanya bekerja saat pemiliknya dikendalikan pemain. Angka dari UJDCombatProfile pemilik
 * (bagian Targeting), jadi manusia & raksasa memakai komponen yang sama.
 *
 * Soft target: musuh dalam kerucut SoftTargetHalfAngle searah stik/WASD (tanpa input: searah hadap) dan dalam
 * TargetSearchRadius; dipilih dari skor jarak + sudut. Dihitung ulang tiap frame untuk penanda HUD (UJDHUDWidget).
 *
 * Warp (WarpForAttack, dipanggil ability serangan di awal pukulan): pemilik diputar menghadap target, lalu kalau celah
 * ke target <= WarpMaxGap, digeser lewat root motion source selama WarpDuration sampai celah WarpStopGap (maks.
 * WarpMaxSlide). Target lebih jauh: putar badan saja, tidak ditarik (kejar pakai terjang).
 * Debug: JD.Debug.Target 1 menggambar kerucut, radius warp, dan target.
 */
UCLASS(ClassGroup = (Jayadwara), meta = (BlueprintSpawnableComponent))
class JAYADWARA_API UJDTargetingComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UJDTargetingComponent();

	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	/** Target terbaik searah Direction (bidang datar). Direction nol = searah hadap pemilik. */
	AActor* FindTarget(const FVector& Direction) const;

	/** Soft target frame ini (untuk HUD). Null kalau tidak ada atau pemilik bukan pemain. */
	UFUNCTION(BlueprintPure, Category = "Targeting")
	AActor* GetSoftTarget() const { return SoftTarget.Get(); }

	/** Putar & tarik pemilik ke soft target searah InputDirection sebelum pukulan. Return target (boleh null). */
	AActor* WarpForAttack(const FVector& InputDirection);

private:
	const UJDCombatProfile* GetProfile() const;
	bool IsTargetingEnabled() const;
	/** Jarak antar-permukaan kapsul pemilik & target di bidang datar. */
	float GetGap(const AActor* Target) const;
	void DrawDebug(const FVector& Direction) const;

	TWeakObjectPtr<AActor> SoftTarget;
};
