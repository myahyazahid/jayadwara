#include "AnimGraphNode_JDCapeChains.h"

#define LOCTEXT_NAMESPACE "JDCapeChains"

FText UAnimGraphNode_JDCapeChains::GetNodeTitle(ENodeTitleType::Type TitleType) const
{
	return GetControllerDescription();
}

FText UAnimGraphNode_JDCapeChains::GetTooltipText() const
{
	return LOCTEXT("Tooltip", "Simulasi rantai jubah Jayadwara: gravitasi, hambatan udara (terangkat saat jatuh), pegas ke pose, kapsul kaki.");
}

FText UAnimGraphNode_JDCapeChains::GetControllerDescription() const
{
	return LOCTEXT("Title", "JD Cape Chains");
}

#undef LOCTEXT_NAMESPACE
