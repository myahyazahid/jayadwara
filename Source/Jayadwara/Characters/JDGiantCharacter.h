#pragma once

#include "CoreMinimal.h"
#include "Characters/JDCharacterBase.h"
#include "JDGiantCharacter.generated.h"

class UCameraComponent;
class USpringArmComponent;

/**
 * Jayadwara, wujud raksasa (docs/12 "Karakter & Transformasi"). Gerak & input dari AJDCharacterBase.
 *
 * Skala raksasa dipasang di sini, bukan saat import (docs/13 D4, revisi Iterasi 6): SK_Jayadwara diimpor di skala 1
 * (199 cm, konvensi Mannequin) lalu komponen mesh diskalakan GiantHeightCm / AuthoredHeightCm. Kapsul, kamera, dan
 * gerak ikut diturunkan dari skala yang sama di OnConstruction, jadi tinggi raksasa cukup diubah di satu angka.
 * Kecepatan & lompatan memakai skala Froude (x sqrt(skala)) dan animasi diputar 1/sqrt(skala) kali supaya terasa
 * berat tanpa kaki meluncur; angka final dituning di Fase 1.
 * Transformasi (ganti pawn) dan UJDSyncComponent menyusul di Fase 1 (Feb 2027).
 */
UCLASS()
class JAYADWARA_API AJDGiantCharacter : public AJDCharacterBase
{
	GENERATED_BODY()

public:
	AJDGiantCharacter();

	virtual void OnConstruction(const FTransform& Transform) override;

	/** Faktor skala mesh = GiantHeightCm / AuthoredHeightCm. */
	UFUNCTION(BlueprintPure, Category = "Giant")
	float GetGiantScale() const;

protected:
	/** Tinggi raksasa di game (cm). Placeholder ±45 m sampai greybox Fase 1 (docs/13 D4). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Giant", meta = (ClampMin = "100"))
	float GiantHeightCm = 4500.0f;

	/** Tinggi badan model di skala 1 tanpa tanduk (cm), dasar perhitungan skala (docs/14). */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Giant", meta = (ClampMin = "1"))
	float AuthoredHeightCm = 190.0f;

	/** Ukuran kapsul di skala 1 (cm); dikalikan skala raksasa. */
	UPROPERTY(EditDefaultsOnly, Category = "Giant")
	float AuthoredCapsuleRadius = 40.0f;

	UPROPERTY(EditDefaultsOnly, Category = "Giant")
	float AuthoredCapsuleHalfHeight = 95.0f;

	/** Nilai gerak mode manusia (sama dengan AJDHumanCharacter) sebelum diskalakan. */
	UPROPERTY(EditDefaultsOnly, Category = "Giant|Movement")
	float HumanWalkSpeed = 500.0f;

	UPROPERTY(EditDefaultsOnly, Category = "Giant|Movement")
	float HumanJumpZVelocity = 500.0f;

	UPROPERTY(EditDefaultsOnly, Category = "Giant|Movement")
	float HumanTurnRate = 500.0f;

	/** Panjang boom kamera di skala 1 (cm); dikalikan skala raksasa. */
	UPROPERTY(EditDefaultsOnly, Category = "Giant|Camera")
	float AuthoredCameraDistance = 300.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
	TObjectPtr<USpringArmComponent> CameraBoom;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
	TObjectPtr<UCameraComponent> FollowCamera;

private:
	void ApplyGiantScale();
};
