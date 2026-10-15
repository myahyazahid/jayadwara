#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "JDCapeComponent.generated.h"

class UMaterialInstanceDynamic;
class USkeletalMeshComponent;

UENUM(BlueprintType)
enum class EJDCapeState : uint8
{
	Equipped,
	Removing,
	Removed,
	Returning
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FJDCapeStateChanged, EJDCapeState, NewState);

/**
 * Jubah upacara raksasa (docs/26, K9 docs/14): mengatur mesh jubah terpisah (komponen SkeletalMesh bernama CapeMeshName
 * yang di-attach ke Mesh dan mengikuti pose lewat ABP Copy Pose From Mesh) — pakai, lepas, pakai kembali.
 *
 * Animasi sementara (prosedural, sampai animasi tangan & Niagara J4 dibuat): jubah terangkat sedikit dan mundur sambil
 * buyar jadi cahaya emas dari ujung bawah ke atas (parameter material "Dissolve" 0..1, M_Jayadwara2_Cape_Master);
 * pakai kembali = kebalikannya. Setelah lepas mesh disembunyikan & tick-nya dimatikan, jadi tidak ada biaya saat combat.
 * Tanpa komponen jubah di aktor (mis. Jayadwara lama) komponen ini diam.
 */
UCLASS(ClassGroup = (Jayadwara), meta = (BlueprintSpawnableComponent))
class JAYADWARA_API UJDCapeComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UJDCapeComponent();

	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	/** Pakai (true) atau lepas (false). bInstant = tanpa animasi. Diabaikan kalau sedang menuju state yang sama. */
	UFUNCTION(BlueprintCallable, Category = "Cape")
	void SetCapeEquipped(bool bEquip, bool bInstant = false);

	/** Lepas kalau terpakai/sedang dipakai, pakai kalau terlepas/sedang dilepas. Tombol Y sementara (AJDGiantCharacter). */
	UFUNCTION(BlueprintCallable, Category = "Cape")
	void ToggleCape();

	UFUNCTION(BlueprintPure, Category = "Cape")
	EJDCapeState GetCapeState() const { return State; }

	UFUNCTION(BlueprintPure, Category = "Cape")
	bool HasCape() const { return CapeMesh != nullptr; }

	/** Untuk montage/Niagara di Blueprint (J4). */
	UPROPERTY(BlueprintAssignable, Category = "Cape")
	FJDCapeStateChanged OnCapeStateChanged;

protected:
	virtual void BeginPlay() override;

	/** Nama komponen SkeletalMesh jubah di Blueprint (Tools/ue_setup_jayadwara2_cape.py membuat "Cape"). */
	UPROPERTY(EditDefaultsOnly, Category = "Cape")
	FName CapeMeshName = TEXT("Cape");

	/** Durasi lepas biasa (detik); docs/07: ±2 s. */
	UPROPERTY(EditAnywhere, Category = "Cape", meta = (ClampMin = "0.05"))
	float RemoveDuration = 2.0f;

	/** Durasi pakai kembali (detik). */
	UPROPERTY(EditAnywhere, Category = "Cape", meta = (ClampMin = "0.05"))
	float ReturnDuration = 1.6f;

	/** Jubah terangkat sejauh ini x tinggi kapsul (setengah tinggi x 2) saat buyar. */
	UPROPERTY(EditAnywhere, Category = "Cape")
	float LiftFraction = 0.06f;

	/** Jubah mundur (ke belakang aktor) sejauh ini x tinggi kapsul saat buyar. */
	UPROPERTY(EditAnywhere, Category = "Cape")
	float DriftFraction = 0.05f;

	/** Nama parameter skalar material (0 = utuh, 1 = hilang). */
	UPROPERTY(EditDefaultsOnly, Category = "Cape")
	FName DissolveParameter = TEXT("Dissolve");

private:
	void SetState(EJDCapeState NewState);
	void ApplyProgress(float Alpha);

	UPROPERTY(Transient)
	TObjectPtr<USkeletalMeshComponent> CapeMesh;

	UPROPERTY(Transient)
	TArray<TObjectPtr<UMaterialInstanceDynamic>> CapeMaterials;

	EJDCapeState State = EJDCapeState::Equipped;
	/** 0 = terpakai penuh, 1 = hilang penuh. */
	float Progress = 0.0f;
	FVector BaseRelativeLocation = FVector::ZeroVector;
};
