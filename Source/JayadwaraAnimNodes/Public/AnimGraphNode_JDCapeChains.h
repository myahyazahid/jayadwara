#pragma once

#include "CoreMinimal.h"
#include "AnimGraphNode_SkeletalControlBase.h"
#include "Animation/AnimNode_JDCapeChains.h"
#include "AnimGraphNode_JDCapeChains.generated.h"

/** Node AnimGraph untuk FAnimNode_JDCapeChains (simulasi rantai jubah, docs/26). */
UCLASS()
class JAYADWARAANIMNODES_API UAnimGraphNode_JDCapeChains : public UAnimGraphNode_SkeletalControlBase
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, Category = "Settings")
	FAnimNode_JDCapeChains Node;

	virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override;
	virtual FText GetTooltipText() const override;

protected:
	virtual FText GetControllerDescription() const override;
	virtual const FAnimNode_SkeletalControlBase* GetNode() const override { return &Node; }
};
