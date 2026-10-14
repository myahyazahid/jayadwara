#include "Characters/JDCapeComponent.h"

#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Character.h"
#include "Jayadwara.h"
#include "Materials/MaterialInstanceDynamic.h"

UJDCapeComponent::UJDCapeComponent()
{
	// Tick hanya menyala selama animasi lepas/pakai.
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = false;
}

void UJDCapeComponent::BeginPlay()
{
	Super::BeginPlay();

	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	TArray<USkeletalMeshComponent*> Meshes;
	GetOwner()->GetComponents(Meshes);
	for (USkeletalMeshComponent* Mesh : Meshes)
	{
		if (Mesh && (!Character || Mesh != Character->GetMesh()) && Mesh->GetFName() == CapeMeshName)
		{
			CapeMesh = Mesh;
			break;
		}
	}
	if (!CapeMesh)
	{
		return;
	}

	BaseRelativeLocation = CapeMesh->GetRelativeLocation();
	for (int32 i = 0; i < CapeMesh->GetNumMaterials(); ++i)
	{
		if (UMaterialInstanceDynamic* MID = CapeMesh->CreateAndSetMaterialInstanceDynamic(i))
		{
			CapeMaterials.Add(MID);
		}
	}
	ApplyProgress(0.0f);
}

void UJDCapeComponent::ToggleCape()
{
	const bool bWorn = State == EJDCapeState::Equipped || State == EJDCapeState::Returning;
	SetCapeEquipped(!bWorn);
}

void UJDCapeComponent::SetCapeEquipped(bool bEquip, bool bInstant)
{
	if (!CapeMesh)
	{
		UE_LOG(LogJayadwara, Warning, TEXT("%s: tidak ada komponen jubah '%s' di %s"), *GetName(), *CapeMeshName.ToString(), *GetNameSafe(GetOwner()));
		return;
	}

	if (bInstant)
	{
		ApplyProgress(bEquip ? 0.0f : 1.0f);
		SetComponentTickEnabled(false);
		SetState(bEquip ? EJDCapeState::Equipped : EJDCapeState::Removed);
		return;
	}

	const EJDCapeState Target = bEquip ? EJDCapeState::Returning : EJDCapeState::Removing;
	const EJDCapeState Rest = bEquip ? EJDCapeState::Equipped : EJDCapeState::Removed;
	if (State == Target || State == Rest)
	{
		return;
	}

	// Mesh & pose harus hidup selama animasi (juga saat kembali dari Removed).
	CapeMesh->SetVisibility(true, true);
	CapeMesh->SetComponentTickEnabled(true);
	SetState(Target);
	SetComponentTickEnabled(true);
}

void UJDCapeComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	if (State == EJDCapeState::Removing)
	{
		Progress = FMath::Min(1.0f, Progress + DeltaTime / RemoveDuration);
		ApplyProgress(Progress);
		if (Progress >= 1.0f)
		{
			SetComponentTickEnabled(false);
			SetState(EJDCapeState::Removed);
		}
	}
	else if (State == EJDCapeState::Returning)
	{
		Progress = FMath::Max(0.0f, Progress - DeltaTime / ReturnDuration);
		ApplyProgress(Progress);
		if (Progress <= 0.0f)
		{
			SetComponentTickEnabled(false);
			SetState(EJDCapeState::Equipped);
		}
	}
	else
	{
		SetComponentTickEnabled(false);
	}
}

void UJDCapeComponent::ApplyProgress(float Alpha)
{
	Progress = FMath::Clamp(Alpha, 0.0f, 1.0f);
	const float Eased = FMath::InterpEaseInOut(0.0f, 1.0f, Progress, 2.0f);

	for (UMaterialInstanceDynamic* MID : CapeMaterials)
	{
		MID->SetScalarParameterValue(DissolveParameter, Eased);
	}

	// Terangkat & mundur dalam ruang dunia, lalu dikembalikan ke ruang komponen induk (Mesh diputar -90° terhadap aktor).
	float Height = 0.0f;
	if (const ACharacter* Character = Cast<ACharacter>(GetOwner()))
	{
		Height = Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight() * 2.0f;
	}
	const FVector WorldOffset = (FVector::UpVector * LiftFraction - GetOwner()->GetActorForwardVector() * DriftFraction) * Height * Eased;
	const USceneComponent* Parent = CapeMesh->GetAttachParent();
	const FVector LocalOffset = Parent ? Parent->GetComponentTransform().InverseTransformVectorNoScale(WorldOffset) : WorldOffset;
	CapeMesh->SetRelativeLocation(BaseRelativeLocation + LocalOffset);
}

void UJDCapeComponent::SetState(EJDCapeState NewState)
{
	if (State == NewState)
	{
		return;
	}
	State = NewState;

	// Terlepas penuh: tidak dirender & pose tidak dihitung (tanpa biaya jubah saat combat, docs/26).
	if (CapeMesh && State == EJDCapeState::Removed)
	{
		CapeMesh->SetVisibility(false, true);
		CapeMesh->SetComponentTickEnabled(false);
	}
	OnCapeStateChanged.Broadcast(State);
}
