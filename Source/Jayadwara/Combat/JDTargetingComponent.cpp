#include "Combat/JDTargetingComponent.h"

#include "Combat/JDCombatComponent.h"
#include "Combat/JDCombatProfile.h"
#include "DrawDebugHelpers.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/RootMotionSource.h"
#include "HAL/IConsoleManager.h"

static TAutoConsoleVariable<bool> CVarDebugTarget(
	TEXT("JD.Debug.Target"), false,
	TEXT("1 = gambar kerucut soft target (kuning), radius warp (biru), dan target terpilih (merah)."));

UJDTargetingComponent::UJDTargetingComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickGroup = TG_PostPhysics;
}

const UJDCombatProfile* UJDTargetingComponent::GetProfile() const
{
	const UJDCombatComponent* Combat = GetOwner() ? GetOwner()->FindComponentByClass<UJDCombatComponent>() : nullptr;
	return Combat ? Combat->GetCombatProfile() : nullptr;
}

bool UJDTargetingComponent::IsTargetingEnabled() const
{
	// Musuh memilih target lewat AI (Iterasi 5); dummy latihan tidak boleh ikut bergeser.
	const APawn* Pawn = Cast<APawn>(GetOwner());
	return Pawn && Pawn->IsPlayerControlled() && !Pawn->IsHidden() && GetProfile();
}

float UJDTargetingComponent::GetGap(const AActor* Target) const
{
	const AActor* Owner = GetOwner();
	return FVector::Dist2D(Owner->GetActorLocation(), Target->GetActorLocation())
		- Owner->GetSimpleCollisionRadius() - Target->GetSimpleCollisionRadius();
}

void UJDTargetingComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	if (!IsTargetingEnabled())
	{
		SoftTarget.Reset();
		return;
	}
	const APawn* Pawn = CastChecked<APawn>(GetOwner());
	FVector Input = Pawn->GetLastMovementInputVector();
	Input.Z = 0.0f;
	Input = Input.SizeSquared() > 0.01f ? Input.GetSafeNormal() : FVector::ZeroVector;
	SoftTarget = FindTarget(Input);

	if (CVarDebugTarget.GetValueOnGameThread())
	{
		DrawDebug(Input);
	}
}

AActor* UJDTargetingComponent::FindTarget(const FVector& Direction) const
{
	const APawn* Owner = Cast<APawn>(GetOwner());
	const UJDCombatProfile* Profile = GetProfile();
	const UWorld* World = GetWorld();
	if (!Owner || !Profile || !World || Profile->TargetSearchRadius <= 0.0f)
	{
		return nullptr;
	}

	FVector Aim = Direction.IsNearlyZero() ? Owner->GetActorForwardVector() : Direction;
	Aim.Z = 0.0f;
	Aim = Aim.GetSafeNormal();
	const float CosHalf = FMath::Cos(FMath::DegreesToRadians(Profile->SoftTargetHalfAngle));
	const FVector Origin = Owner->GetActorLocation();

	AActor* Best = nullptr;
	float BestScore = TNumericLimits<float>::Max();
	for (TActorIterator<APawn> It(World); It; ++It)
	{
		APawn* Other = *It;
		if (!UJDCombatComponent::IsValidTarget(Owner, Other))
		{
			continue;
		}
		const FVector To = (Other->GetActorLocation() - Origin) * FVector(1.0f, 1.0f, 0.0f);
		const float Dist = To.Size();
		if (Dist > Profile->TargetSearchRadius + Other->GetSimpleCollisionRadius())
		{
			continue;
		}
		const float Cos = Dist > KINDA_SMALL_NUMBER ? FVector::DotProduct(To / Dist, Aim) : 1.0f;
		if (Cos < CosHalf)
		{
			continue;
		}
		// Skor: jarak relatif + sudut relatif (0 = tepat di tengah kerucut).
		const float AngleFrac = FMath::Acos(FMath::Clamp(Cos, -1.0f, 1.0f)) / FMath::DegreesToRadians(Profile->SoftTargetHalfAngle);
		const float Score = Dist / Profile->TargetSearchRadius + Profile->SoftTargetAngleWeight * AngleFrac;
		if (Score < BestScore)
		{
			BestScore = Score;
			Best = Other;
		}
	}
	return Best;
}

AActor* UJDTargetingComponent::WarpForAttack(const FVector& InputDirection)
{
	ACharacter* Character = Cast<ACharacter>(GetOwner());
	const UJDCombatProfile* Profile = GetProfile();
	if (!Character || !Profile || !IsTargetingEnabled())
	{
		return nullptr;
	}
	AActor* Target = FindTarget(InputDirection);
	if (!Target)
	{
		return nullptr;
	}

	const FVector Start = Character->GetActorLocation();
	const FVector ToTarget = (Target->GetActorLocation() - Start).GetSafeNormal2D();
	if (ToTarget.IsZero())
	{
		return Target;
	}
	Character->SetActorRotation(FRotator(0.0f, ToTarget.Rotation().Yaw, 0.0f));

	UCharacterMovementComponent* Movement = Character->GetCharacterMovement();
	const float Gap = GetGap(Target);
	if (!Movement || Movement->IsFalling() || Gap > Profile->WarpMaxGap)
	{
		return Target;
	}
	const float Slide = FMath::Clamp(Gap - Profile->WarpStopGap, 0.0f, Profile->WarpMaxSlide);
	if (Slide < 1.0f)
	{
		return Target;
	}

	// Geser di awal ancang-ancang (override root motion animasi), lalu berhenti di tempat; root motion animasi lanjut.
	TSharedPtr<FRootMotionSource_MoveToForce> Move = MakeShared<FRootMotionSource_MoveToForce>();
	Move->InstanceName = TEXT("JDWarp");
	Move->AccumulateMode = ERootMotionAccumulateMode::Override;
	Move->Priority = 600;
	Move->StartLocation = Start;
	Move->TargetLocation = Start + ToTarget * Slide;
	Move->Duration = Profile->WarpDuration;
	Move->bRestrictSpeedToExpected = true;
	Move->FinishVelocityParams.Mode = ERootMotionFinishVelocityMode::SetVelocity;
	Move->FinishVelocityParams.SetVelocity = FVector::ZeroVector;
	Movement->ApplyRootMotionSource(Move);
	return Target;
}

void UJDTargetingComponent::DrawDebug(const FVector& Direction) const
{
	const AActor* Owner = GetOwner();
	const UJDCombatProfile* Profile = GetProfile();
	UWorld* World = GetWorld();
	if (!Owner || !Profile || !World)
	{
		return;
	}
	const FVector Aim = Direction.IsNearlyZero() ? Owner->GetActorForwardVector().GetSafeNormal2D() : Direction;
	const FVector Origin = Owner->GetActorLocation();
	const float Half = FMath::DegreesToRadians(Profile->SoftTargetHalfAngle);
	DrawDebugCone(World, Origin, Aim, Profile->TargetSearchRadius, Half, 0.01f, 16, FColor::Yellow, false, -1.0f, 0, 2.0f);
	DrawDebugCircle(World, Origin, Profile->WarpMaxGap + Owner->GetSimpleCollisionRadius(), 48, FColor::Blue, false, -1.0f, 0, 2.0f,
		FVector(1.0f, 0.0f, 0.0f), FVector(0.0f, 1.0f, 0.0f), false);
	if (const AActor* Target = SoftTarget.Get())
	{
		DrawDebugSphere(World, Target->GetActorLocation(), Target->GetSimpleCollisionRadius() * 1.2f, 12, FColor::Red, false, -1.0f, 0, 2.0f);
	}
}
