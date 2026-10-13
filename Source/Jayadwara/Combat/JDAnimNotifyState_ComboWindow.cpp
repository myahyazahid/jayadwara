#include "Combat/JDAnimNotifyState_ComboWindow.h"

#include "AbilitySystemComponent.h"
#include "AbilitySystemGlobals.h"
#include "Abilities/JDGameplayTags.h"
#include "Components/SkeletalMeshComponent.h"

namespace
{
	UAbilitySystemComponent* FindASC(const USkeletalMeshComponent* MeshComp)
	{
		return UAbilitySystemGlobals::GetAbilitySystemComponentFromActor(MeshComp ? MeshComp->GetOwner() : nullptr);
	}
}

void UJDAnimNotifyState_ComboWindow::NotifyBegin(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, float TotalDuration, const FAnimNotifyEventReference& EventReference)
{
	Super::NotifyBegin(MeshComp, Animation, TotalDuration, EventReference);
	if (UAbilitySystemComponent* ASC = FindASC(MeshComp))
	{
		ASC->SetLooseGameplayTagCount(JDGameplayTags::State_Combat_ComboWindow, 1);
	}
}

void UJDAnimNotifyState_ComboWindow::NotifyEnd(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, const FAnimNotifyEventReference& EventReference)
{
	if (UAbilitySystemComponent* ASC = FindASC(MeshComp))
	{
		ASC->SetLooseGameplayTagCount(JDGameplayTags::State_Combat_ComboWindow, 0);
	}
	Super::NotifyEnd(MeshComp, Animation, EventReference);
}
