#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "JDPlayerController.generated.h"

class AJDGiantCharacter;
class UInputAction;
class UInputMappingContext;
class UJDHUDWidget;

/**
 * Pemain. Memasang mapping context mode manusia (docs/12 "Input") dan menangani transformasi manusia <-> Jayadwara.
 *
 * Transformasi = ganti pawn (docs/12 "Karakter & Transformasi"): pawn manusia disembunyikan (bukan dihapus), pawn
 * raksasa di-spawn di lokasinya setinggi manusia lalu tumbuh (AJDGiantCharacter::BeginScaleTransition). Kembali ke
 * manusia: raksasa menyusut, pawn manusia ditampilkan lagi, pawn raksasa dihapus. Efek ini sementara; animasi & VFX
 * transformasi sungguhan menyusul. IMC_Giant dan syarat/meter Sync ditambahkan di Fase 1 (Feb 2027).
 *
 * GAS (docs/23 Iterasi 1): input ability pawn diproses sekali per frame di PostProcessInput; HUD debug (UJDHUDWidget)
 * dibuat di sini supaya bertahan saat pawn berganti; cheat "JD.*" lewat UJDCheatManager.
 */
UCLASS()
class JAYADWARA_API AJDPlayerController : public APlayerController
{
	GENERATED_BODY()

public:
	AJDPlayerController();

	/** Tombol transformasi: manusia -> Jayadwara, atau sebaliknya. */
	UFUNCTION(BlueprintCallable, Category = "Transformation")
	void ToggleTransformation();

	UFUNCTION(BlueprintCallable, Category = "Transformation")
	void TransformToGiant();

	UFUNCTION(BlueprintCallable, Category = "Transformation")
	void RevertToHuman();

	UFUNCTION(BlueprintPure, Category = "Transformation")
	bool IsGiant() const { return GiantPawn != nullptr; }

protected:
	virtual void BeginPlay() override;
	virtual void SetupInputComponent() override;
	virtual void PostProcessInput(const float DeltaTime, const bool bGamePaused) override;
	virtual void OnPossess(APawn* InPawn) override;

	/** IMC mode manusia. Array karena konten Third Person bawaan 5.6 bisa memisahkan mouse look ke IMC sendiri. */
	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TArray<TObjectPtr<UInputMappingContext>> HumanMappingContexts;

	/** Aksi tombol transformasi (T). Harus dipetakan di salah satu IMC di atas. */
	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UInputAction> TransformAction;

	/** Kelas pawn Jayadwara (BP_Jayadwara) yang di-spawn saat bertransformasi. */
	UPROPERTY(EditDefaultsOnly, Category = "Transformation")
	TSubclassOf<AJDGiantCharacter> GiantPawnClass;

	/** HUD debug (bar atribut). Kosong = tanpa HUD. Bisa diganti WBP_HUD_* turunan UJDHUDWidget. */
	UPROPERTY(EditDefaultsOnly, Category = "UI")
	TSubclassOf<UJDHUDWidget> HUDWidgetClass;

	/** Lama efek tumbuh/menyusut (detik). */
	UPROPERTY(EditDefaultsOnly, Category = "Transformation", meta = (ClampMin = "0.1"))
	float TransformDuration = 2.0f;

private:
	void OnTransformedToGiant();
	void OnRevertedToHuman();

	/** Possess tanpa menggeser arah kamera (Possess mengatur ulang control rotation mengikuti pawn). */
	void PossessKeepingView(APawn* NewPawn);

	UPROPERTY(Transient)
	TObjectPtr<APawn> HumanPawn;

	UPROPERTY(Transient)
	TObjectPtr<AJDGiantCharacter> GiantPawn;

	UPROPERTY(Transient)
	TObjectPtr<UJDHUDWidget> HUDWidget;

	bool bTransforming = false;
};
