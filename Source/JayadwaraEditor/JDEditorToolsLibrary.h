#pragma once

#include "CoreMinimal.h"
#include "GameplayTagContainer.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "JDEditorToolsLibrary.generated.h"

class UAnimBlueprint;
class UIKRetargeter;
class UPhysicsAsset;
class USkeletalMesh;

/** Satu rantai Anim Dynamics (tulang awal..akhir, mis. scarf_l_01..scarf_l_06). */
USTRUCT(BlueprintType)
struct FJDAnimDynamicsChain
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Jayadwara")
	FName StartBone;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Jayadwara")
	FName EndBone;

	/** Batas ayun tiap sendi (derajat, simetris) pada sumbu Y/Z bone; twist (X) dibatasi TwistLimit. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Jayadwara")
	float SwingLimit = 45.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Jayadwara")
	float TwistLimit = 10.0f;

	/** Ukuran kotak body simulasi (cm, ruang mesh skala 1). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Jayadwara")
	FVector BoxExtents = FVector(4.0f);

	/** Radius bola tabrakan tiap body terhadap SphereLimitBones (cm, skala 1). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Jayadwara")
	float CollisionRadius = 4.0f;
};

/**
 * Alat editor Jayadwara, dipanggil dari Python (unreal.JDEditorToolsLibrary.*). Dipakai Tools/ue_setup_giant.py.
 */
UCLASS()
class UJDEditorToolsLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/**
	 * Bangun ulang Physics Asset: satu kapsul per tulang di BodyBones, dipas ke vertex tulang itu + turunannya yang
	 * tidak punya body (jari, twist). Tulang yang namanya diawali ExcludePrefixes (selendang/kain/IK) tidak ikut.
	 * Constraint ke body induk terdekat (Limited, AngularLimitDeg), tabrakan antar-body dimatikan.
	 * @return jumlah body yang dibuat (0 = gagal).
	 */
	UFUNCTION(BlueprintCallable, Category = "Jayadwara|Editor")
	static int32 RebuildPhysicsAsset(UPhysicsAsset* PhysicsAsset, USkeletalMesh* Mesh, const TArray<FName>& BodyBones,
		const TArray<FString>& ExcludePrefixes, float AngularLimitDeg = 30.0f);

	/**
	 * Sisipkan node Anim Dynamics (satu per rantai) tepat sebelum Output Pose di AnimGraph, lalu compile.
	 * Node lama yang dibuat fungsi ini (komentar "JD_AnimDynamics") dihapus dulu, jadi aman dijalankan ulang.
	 * SphereLimitBones: tulang yang menolak rantai (mis. paha) dengan radius SphereLimitRadius (cm, skala 1).
	 * @return jumlah node Anim Dynamics yang disisipkan (-1 = gagal).
	 */
	UFUNCTION(BlueprintCallable, Category = "Jayadwara|Editor")
	static int32 AddAnimDynamicsChains(UAnimBlueprint* AnimBlueprint, const TArray<FJDAnimDynamicsChain>& Chains,
		const TArray<FName>& SphereLimitBones, float SphereLimitRadius = 12.0f, int32 SimulationSpace = 0,
		float ComponentLinearAccScale = 0.0f, float GravityScale = 1.0f);

	/**
	 * Lepas node AnimGraph yang nama kelasnya mengandung ClassNameContains (mis. "ControlRig"): pose masuk node itu
	 * disambung langsung ke tujuan keluarnya, node dihapus, ABP di-compile. Dipakai untuk membuang foot IK Mannequin
	 * (CR_Mannequin_FootIK) dari ABP_Jayadwara: rig itu mengandaikan orientasi tulang & skala Manny.
	 * @return jumlah node yang dilepas.
	 */
	UFUNCTION(BlueprintCallable, Category = "Jayadwara|Editor")
	static int32 BypassAnimGraphNodes(UAnimBlueprint* AnimBlueprint, const FString& ClassNameContains);

	/**
	 * Batch retarget (sama dengan IKRetargetBatchOperation.duplicate_and_retarget) tapi hasilnya LANGSUNG ditulis ke
	 * FolderPath. Versi Python tidak mengisi folder sehingga hasil jatuh ke /Game, dan memindahkannya memutus rujukan
	 * ABP -> animasi (UE 5.6.1). File bernama sama ditimpa. Aset referensi (BlendSpace, anim di ABP) ikut.
	 */
	UFUNCTION(BlueprintCallable, Category = "Jayadwara|Editor")
	static void RetargetAssetsToFolder(const TArray<UObject*>& Assets, USkeletalMesh* SourceMesh, USkeletalMesh* TargetMesh,
		UIKRetargeter* Retargeter, const FString& FolderPath, const FString& Suffix, bool bIncludeReferencedAssets = true);

	/**
	 * Gameplay Tag dari nama, untuk mengisi DataAsset dari Python (FGameplayTag::TagName tidak bisa di-set langsung).
	 * Tag yang tidak terdaftar -> tag kosong + error di log. Dipakai Tools/ue_setup_combat.py.
	 */
	UFUNCTION(BlueprintCallable, Category = "Jayadwara|Editor")
	static FGameplayTag MakeGameplayTag(FName TagName);
};
