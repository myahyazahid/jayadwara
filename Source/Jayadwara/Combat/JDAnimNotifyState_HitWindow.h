#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimNotifies/AnimNotifyState.h"
#include "JDAnimNotifyState_HitWindow.generated.h"

/**
 * Jendela hitbox di montage serangan (docs/12 "Hit detection"): selama aktif, UJDCombatComponent pemilik mesh
 * menyapu sphere dari socket/tulang SocketName tiap frame. Nama tulang Mannequin (hand_r, foot_r, ...) supaya sama
 * untuk Aksa dan Jayadwara.
 */
UCLASS(meta = (DisplayName = "JD Hit Window"))
class JAYADWARA_API UJDAnimNotifyState_HitWindow : public UAnimNotifyState
{
	GENERATED_BODY()

public:
	virtual void NotifyBegin(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, float TotalDuration, const FAnimNotifyEventReference& EventReference) override;
	virtual void NotifyTick(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, float FrameDeltaTime, const FAnimNotifyEventReference& EventReference) override;
	virtual void NotifyEnd(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, const FAnimNotifyEventReference& EventReference) override;
	virtual FString GetNotifyName_Implementation() const override;

	/** Tulang/socket asal hitbox. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Hit")
	FName SocketName = TEXT("hand_r");

	/** Radius (cm, skala 1); 0 = HitRadius dari UJDCombatProfile. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Hit", meta = (ClampMin = "0"))
	float RadiusOverride = 0.0f;
};
