#pragma once

#include "CoreMinimal.h"
#include "BoneContainer.h"
#include "BonePose.h"
#include "BoneControllers/AnimNode_SkeletalControlBase.h"
#include "AnimNode_JDCapeChains.generated.h"

/** Satu rantai kain: tulang awal..akhir (berurutan induk-anak, mis. cape_c_01..cape_c_06). */
USTRUCT(BlueprintType)
struct JAYADWARA_API FJDCapeChain
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, Category = "Cape")
	FBoneReference StartBone;

	UPROPERTY(EditAnywhere, Category = "Cape")
	FBoneReference EndBone;
};

/** Kapsul penolak di antara dua tulang (mis. thigh_l -> calf_l). Radius dalam cm ruang komponen (skala aktor 1). */
USTRUCT(BlueprintType)
struct JAYADWARA_API FJDCapeCollider
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, Category = "Cape")
	FBoneReference BoneA;

	UPROPERTY(EditAnywhere, Category = "Cape")
	FBoneReference BoneB;

	UPROPERTY(EditAnywhere, Category = "Cape", meta = (ClampMin = "0"))
	float Radius = 100.0f;
};

/**
 * Simulasi rantai kain jubah (docs/26 J1c) — pengganti ringan Chaos Cloth/Anim Dynamics yang bisa diatur dari kode.
 *
 * Tiap rantai = partikel di kepala tiap tulang + ujung (ekstrapolasi ruas terakhir), disimulasikan di RUANG DUNIA
 * (Verlet, sub-langkah 1/60 s): gravitasi, hambatan udara (kecepatan dunia diredam -> saat badan jatuh/terbang kain
 * tertahan udara sehingga TERANGKAT, saat lari kain tertinggal ke belakang), pegas lemah ke pose animasi (bentuk
 * jubah kembali saat diam), panjang ruas tetap (follow-the-leader dari akar), batas sudut terhadap pose animasi, dan
 * kapsul penolak (paha/betis/pinggul) supaya tidak menembus kaki. Akar rantai menempel ke pose animasi.
 * Hasil: rotasi tiap tulang rantai diputar dari arah animasi ke arah simulasi. Node ruang komponen.
 */
USTRUCT(BlueprintInternalUseOnly)
struct JAYADWARA_API FAnimNode_JDCapeChains : public FAnimNode_SkeletalControlBase
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, Category = "Cape")
	TArray<FJDCapeChain> Chains;

	UPROPERTY(EditAnywhere, Category = "Cape")
	TArray<FJDCapeCollider> Colliders;

	/** Percepatan gravitasi (cm/s²); dunia nyata 980. Raksasa 45 m tetap g normal -> kain terasa berat & lambat. */
	UPROPERTY(EditAnywhere, Category = "Cape|Simulasi", meta = (PinHiddenByDefault))
	float Gravity = 980.0f;

	/** Hambatan udara (1/s): makin besar makin kuat kain tertahan udara (terangkat saat jatuh, tertinggal saat lari). */
	UPROPERTY(EditAnywhere, Category = "Cape|Simulasi", meta = (ClampMin = "0", PinHiddenByDefault))
	float AirDrag = 2.0f;

	/** Pegas ke pose animasi (1/s²): makin besar makin cepat kembali ke bentuk jubah & makin sedikit terangkat. */
	UPROPERTY(EditAnywhere, Category = "Cape|Simulasi", meta = (ClampMin = "0", PinHiddenByDefault))
	float Stiffness = 5.0f;

	/** Sudut maksimum tiap ruas dari arah animasinya (derajat) — pengaman supaya kain tidak terlempar (pelajaran R3d). */
	UPROPERTY(EditAnywhere, Category = "Cape|Simulasi", meta = (ClampMin = "0", ClampMax = "179", PinHiddenByDefault))
	float MaxAngleDeg = 75.0f;

	/** Jarak tambahan partikel dari permukaan kapsul (cm ruang komponen): tebal kain di antara rantai. */
	UPROPERTY(EditAnywhere, Category = "Cape|Simulasi", meta = (ClampMin = "0", PinHiddenByDefault))
	float CollisionMargin = 90.0f;

	/** Iterasi batasan per sub-langkah. */
	UPROPERTY(EditAnywhere, Category = "Cape|Simulasi", meta = (ClampMin = "1", ClampMax = "8"))
	int32 Iterations = 3;

	/** Akar berpindah lebih jauh dari ini dalam satu frame (cm dunia) = teleport -> simulasi direset. */
	UPROPERTY(EditAnywhere, Category = "Cape|Simulasi")
	float TeleportDistance = 20000.0f;

	FAnimNode_JDCapeChains() = default;

	// FAnimNode_SkeletalControlBase
	virtual void UpdateInternal(const FAnimationUpdateContext& Context) override;
	virtual void EvaluateSkeletalControl_AnyThread(FComponentSpacePoseContext& Output, TArray<FBoneTransform>& OutBoneTransforms) override;
	virtual bool IsValidToEvaluate(const USkeleton* Skeleton, const FBoneContainer& RequiredBones) override;
	virtual void ResetDynamics(ETeleportType InTeleportType) override;
	virtual bool NeedsDynamicReset() const override { return true; }

private:
	virtual void InitializeBoneReferences(const FBoneContainer& RequiredBones) override;

	struct FChainState
	{
		TArray<FCompactPoseBoneIndex> Bones;
		TArray<FVector> Pos;       // partikel dunia: kepala tiap tulang + ujung
		TArray<FVector> Prev;
		TArray<FVector> PrevTarget;
	};
	TArray<FChainState> ChainStates;
	float PendingDeltaTime = 0.0f;
	bool bReset = true;
};
