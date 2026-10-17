#include "Combat/JDAnimNotifyState_HitWindow.h"

#include "Combat/JDCombatComponent.h"
#include "Components/SkeletalMeshComponent.h"

namespace
{
	UJDCombatComponent* FindCombat(const USkeletalMeshComponent* MeshComp)
	{
		// Preview editor (Persona) tidak punya komponen combat -> notify diam.
		const AActor* Owner = MeshComp ? MeshComp->GetOwner() : nullptr;
		return Owner ? Owner->FindComponentByClass<UJDCombatComponent>() : nullptr;
	}
}

void UJDAnimNotifyState_HitWindow::NotifyBegin(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, float TotalDuration, const FAnimNotifyEventReference& EventReference)
{
	Super::NotifyBegin(MeshComp, Animation, TotalDuration, EventReference);
	if (UJDCombatComponent* Combat = FindCombat(MeshComp))
	{
		Combat->BeginHitWindow(SocketName, RadiusOverride, bNewHit);
	}
}

void UJDAnimNotifyState_HitWindow::NotifyTick(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, float FrameDeltaTime, const FAnimNotifyEventReference& EventReference)
{
	Super::NotifyTick(MeshComp, Animation, FrameDeltaTime, EventReference);
	if (UJDCombatComponent* Combat = FindCombat(MeshComp))
	{
		Combat->UpdateHitWindow();
	}
}

void UJDAnimNotifyState_HitWindow::NotifyEnd(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, const FAnimNotifyEventReference& EventReference)
{
	if (UJDCombatComponent* Combat = FindCombat(MeshComp))
	{
		Combat->UpdateHitWindow();
		Combat->EndHitWindow();
	}
	Super::NotifyEnd(MeshComp, Animation, EventReference);
}

FString UJDAnimNotifyState_HitWindow::GetNotifyName_Implementation() const
{
	return FString::Printf(TEXT("Hit %s"), *SocketName.ToString());
}
