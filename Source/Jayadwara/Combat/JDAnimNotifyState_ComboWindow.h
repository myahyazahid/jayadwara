#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimNotifies/AnimNotifyState.h"
#include "JDAnimNotifyState_ComboWindow.generated.h"

/**
 * Jendela sambung combo (docs/12 "Combo"): selama aktif pemilik mendapat tag State.Combat.ComboWindow; tekanan
 * pukulan ringan (atau yang di-buffer sesaat sebelumnya) memulai pukulan berikutnya.
 */
UCLASS(meta = (DisplayName = "JD Combo Window"))
class JAYADWARA_API UJDAnimNotifyState_ComboWindow : public UAnimNotifyState
{
	GENERATED_BODY()

public:
	virtual void NotifyBegin(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, float TotalDuration, const FAnimNotifyEventReference& EventReference) override;
	virtual void NotifyEnd(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, const FAnimNotifyEventReference& EventReference) override;
	virtual FString GetNotifyName_Implementation() const override { return TEXT("Combo Window"); }
};
