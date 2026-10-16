#pragma once

#include "CoreMinimal.h"
#include "Characters/JDCharacterBase.h"
#include "JDGiantCharacter.generated.h"

class UCameraComponent;
class UJDCapeComponent;
class USpringArmComponent;

/**
 * Jayadwara, wujud raksasa (docs/12 "Karakter & Transformasi"). Gerak & input dari AJDCharacterBase.
 *
 * Skala raksasa di-bake ke SK_Jayadwara saat export Blender (docs/13 D4, revisi Iterasi 6b): mesh sudah setinggi
 * MeshHeightCm dan komponennya berskala 1 (Anim Dynamics tidak mendukung komponen berskala). Kapsul, kamera, dan gerak
 * diturunkan dari skala raksasa terhadap tinggi manusia (GiantHeightCm / AuthoredHeightCm) di OnConstruction.
 * Kecepatan lari = manusia x skala^SpeedScaleExponent dan animasi diputar skala^(SpeedScaleExponent - 1) kali, jadi kaki
 * tetap menapak. Sejak 16 Okt 2026 bawaannya "ala Mebius" (gesit, docs/07): exponent 0,83 (lari ±70 m/s, animasi ±0,6x),
 * berbalik 720°/s, akselerasi setara manusia. Rasa berat datang dari hit-stop, guncangan kamera, debu, dan suara, bukan
 * dari kelambatan. Exponent 0,5 = skala Froude (setelan berat lama). Lompatan tetap Froude x JumpBoost.
 * Transformasi (ganti pawn) dilakukan AJDPlayerController; pawn ini hanya menyediakan efek tumbuh/menyusut
 * (BeginScaleTransition). UJDSyncComponent menyusul di Fase 1 (Feb 2027).
 */
UCLASS()
class JAYADWARA_API AJDGiantCharacter : public AJDCharacterBase
{
	GENERATED_BODY()

public:
	AJDGiantCharacter();

	virtual void OnConstruction(const FTransform& Transform) override;
	virtual void Tick(float DeltaSeconds) override;

	/** Skala raksasa terhadap model manusia = GiantHeightCm / AuthoredHeightCm (dasar kapsul, kamera, gerak). */
	UFUNCTION(BlueprintPure, Category = "Giant")
	float GetGiantScale() const;

	/** Skala aktor yang membuat Jayadwara setinggi manusia (= 1 / GetGiantScale()); awal efek tumbuh, akhir efek menyusut. */
	UFUNCTION(BlueprintPure, Category = "Giant")
	float GetHumanScale() const;

	/** Setengah tinggi kapsul pada skala aktor 1 (cm). */
	UFUNCTION(BlueprintPure, Category = "Giant")
	float GetGiantHalfHeight() const;

	/**
	 * Pengali kecepatan gerak raksasa terhadap manusia = skala^SpeedScaleExponent. Animasi locomotion diputar
	 * GetSpeedScale() / GetGiantScale() kali; sumbu Speed BlendSpace raksasa dikali nilai ini (Tools/ue_setup_jayadwara2.py,
	 * Tools/ue_setup_giant.py) supaya kaki menapak.
	 */
	UFUNCTION(BlueprintPure, Category = "Giant")
	float GetSpeedScale() const;

	UFUNCTION(BlueprintPure, Category = "Giant")
	bool IsScaleTransitioning() const { return bScaleTransitioning; }

	UFUNCTION(BlueprintPure, Category = "Giant")
	UJDCapeComponent* GetCapeComponent() const { return CapeControl; }

	/**
	 * Efek transformasi sederhana: skala aktor tumbuh dari setinggi manusia ke penuh (bGrow) atau sebaliknya, kaki tetap
	 * menapak, kamera ikut. Gerak dimatikan selama efek; OnFinished dipanggil setelah selesai (skala akhir pas 1 atau skala
	 * manusia). Pengganti sementara sampai animasi & VFX transformasi dibuat (Agu - Sep 2027).
	 */
	void BeginScaleTransition(bool bGrow, float Duration, TFunction<void()> OnFinished = nullptr);

protected:
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

	/** Tinggi raksasa di game (cm). Placeholder ±45 m sampai greybox Fase 1 (docs/13 D4). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Giant", meta = (ClampMin = "100"))
	float GiantHeightCm = 4500.0f;

	/** Tinggi badan model saat dibuat di Blender, tanpa tanduk (cm), dasar perhitungan skala (docs/14). */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Giant", meta = (ClampMin = "1"))
	float AuthoredHeightCm = 190.0f;

	/**
	 * Tinggi badan SK_Jayadwara sebagaimana diimpor (cm) = GIANT_HEIGHT_M di Art/Scripts/16_make_lods.py.
	 * Komponen mesh diskalakan GiantHeightCm / MeshHeightCm, jadi 1 selama keduanya sama.
	 */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Giant", meta = (ClampMin = "1"))
	float MeshHeightCm = 4500.0f;

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

	/** Akselerasi manusia (cm/s²), nilai bawaan CharacterMovement; dikali GetSpeedScale() supaya raksasa secepat manusia mencapai lari penuh. */
	UPROPERTY(EditDefaultsOnly, Category = "Giant|Movement")
	float HumanMaxAcceleration = 2048.0f;

	/**
	 * Kelincahan: kecepatan = manusia x skala^exponent. 0,5 = Froude (berat, lari ±24 m/s, animasi ±0,2x);
	 * 0,83 = ala Mebius (lari ±70 m/s, animasi ±0,6x); 1,0 = animasi kecepatan normal (lari ±118 m/s).
	 * Setelah diubah, jalankan ulang Tools/ue_setup_giant_speed.py supaya BlendSpace & montage combat ikut.
	 */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Giant|Movement", meta = (ClampMin = "0.5", ClampMax = "1.0"))
	float SpeedScaleExponent = 0.83f;

	/** Kecepatan berbalik badan raksasa (°/s), tidak diskalakan. Manusia 500; ala Mebius 720. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Giant|Movement", meta = (ClampMin = "10"))
	float GiantTurnRate = 720.0f;

	/** Pengali kecepatan lompat di atas skala Froude (tinggi lompatan naik kuadratnya). 1,25 → ±1,56x tinggi proporsional. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Giant|Movement", meta = (ClampMin = "0.5"))
	float JumpBoost = 1.25f;

	/** Panjang boom kamera di skala 1 (cm); dikalikan skala raksasa. */
	UPROPERTY(EditDefaultsOnly, Category = "Giant|Camera")
	float AuthoredCameraDistance = 300.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
	TObjectPtr<USpringArmComponent> CameraBoom;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
	TObjectPtr<UCameraComponent> FollowCamera;

	/** Pakai/lepas jubah upacara (docs/26); diam kalau Blueprint tidak punya komponen mesh "Cape". */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Cape")
	TObjectPtr<UJDCapeComponent> CapeControl;

private:
	void ApplyGiantScale();

	/** Kamera diturunkan dari skala efektif (skala raksasa x skala aktor): panjang boom, offset, probe. */
	void ApplyCameraScale(float EffectiveScale);

	void FinishScaleTransition();

	/** SEMENTARA (docs/26 J1b): tombol Y = lepas/pakai jubah. Diganti pemicu lock-on & aksi combat pertama di J4. */
	void DebugToggleCape();

	bool bScaleTransitioning = false;
	bool bTransitionGrow = true;
	float TransitionDuration = 1.0f;
	float TransitionElapsed = 0.0f;
	float TransitionFootZ = 0.0f;
	TFunction<void()> TransitionFinished;
};
