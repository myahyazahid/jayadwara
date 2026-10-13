#include "Characters/JDGiantCharacter.h"

#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Math/UnrealMathUtility.h"

AJDGiantCharacter::AJDGiantCharacter()
{
	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;

	// Tick hanya menyala selama efek tumbuh/menyusut (BeginScaleTransition).
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.bStartWithTickEnabled = false;

	UCharacterMovementComponent* Movement = GetCharacterMovement();
	Movement->bOrientRotationToMovement = true;
	Movement->AirControl = 0.35f;
	Movement->MinAnalogWalkSpeed = 20.0f;

	// SK_Jayadwara menghadap +Y (konvensi Mannequin); actor maju ke +X.
	GetMesh()->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f));

	CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
	CameraBoom->SetupAttachment(RootComponent);
	CameraBoom->bUsePawnControlRotation = true;
	CameraBoom->bEnableCameraLag = true;
	CameraBoom->CameraLagSpeed = 6.0f;

	FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
	FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
	FollowCamera->bUsePawnControlRotation = false;

	ApplyGiantScale();
}

void AJDGiantCharacter::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	ApplyGiantScale();
}

float AJDGiantCharacter::GetGiantScale() const
{
	return GiantHeightCm / FMath::Max(AuthoredHeightCm, 1.0f);
}

float AJDGiantCharacter::GetHumanScale() const
{
	return 1.0f / FMath::Max(GetGiantScale(), 1.0f);
}

float AJDGiantCharacter::GetGiantHalfHeight() const
{
	return AuthoredCapsuleHalfHeight * GetGiantScale();
}

void AJDGiantCharacter::BeginScaleTransition(bool bGrow, float Duration, TFunction<void()> OnFinished)
{
	if (bScaleTransitioning)
	{
		return;
	}

	bScaleTransitioning = true;
	bTransitionGrow = bGrow;
	TransitionDuration = FMath::Max(Duration, KINDA_SMALL_NUMBER);
	TransitionElapsed = 0.0f;
	TransitionFinished = MoveTemp(OnFinished);

	// Titik tapak kaki dijaga tetap selama skala berubah (pusat kapsul naik/turun mengikuti skala).
	TransitionFootZ = GetActorLocation().Z - GetGiantHalfHeight() * GetActorScale3D().Z;

	UCharacterMovementComponent* Movement = GetCharacterMovement();
	Movement->StopMovementImmediately();
	Movement->DisableMovement();

	const float StartScale = bGrow ? GetHumanScale() : 1.0f;
	SetActorScale3D(FVector(StartScale));
	ApplyCameraScale(GetGiantScale() * StartScale);

	SetActorTickEnabled(true);
}

void AJDGiantCharacter::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	if (!bScaleTransitioning)
	{
		return;
	}

	TransitionElapsed += DeltaSeconds;
	const float Alpha = FMath::Clamp(TransitionElapsed / TransitionDuration, 0.0f, 1.0f);
	const float Eased = FMath::InterpEaseInOut(0.0f, 1.0f, Alpha, 2.0f);

	// Interpolasi geometris: 1 -> 24x terasa merata, bukan melesat di akhir.
	const float Human = GetHumanScale();
	const float From = bTransitionGrow ? Human : 1.0f;
	const float To = bTransitionGrow ? 1.0f : Human;
	const float Scale = From * FMath::Pow(To / From, Eased);

	SetActorScale3D(FVector(Scale));
	FVector Location = GetActorLocation();
	Location.Z = TransitionFootZ + GetGiantHalfHeight() * Scale;
	SetActorLocation(Location, false, nullptr, ETeleportType::TeleportPhysics);
	ApplyCameraScale(GetGiantScale() * Scale);

	if (Alpha >= 1.0f)
	{
		FinishScaleTransition();
	}
}

void AJDGiantCharacter::FinishScaleTransition()
{
	bScaleTransitioning = false;
	SetActorTickEnabled(false);

	if (bTransitionGrow)
	{
		// Skala aktor kembali pas 1: Anim Dynamics selendang/kain tidak boleh dijalankan pada komponen berskala.
		SetActorScale3D(FVector::OneVector);
		ApplyCameraScale(GetGiantScale());
		GetMesh()->ResetAnimInstanceDynamics(ETeleportType::ResetPhysics);
		GetCharacterMovement()->SetMovementMode(MOVE_Falling);
	}

	TFunction<void()> Callback = MoveTemp(TransitionFinished);
	TransitionFinished = nullptr;
	if (Callback)
	{
		Callback();
	}
}

void AJDGiantCharacter::ApplyCameraScale(float EffectiveScale)
{
	CameraBoom->TargetArmLength = AuthoredCameraDistance * EffectiveScale;
	CameraBoom->SocketOffset = FVector(0.0f, 0.0f, 40.0f * EffectiveScale);
	CameraBoom->ProbeSize = 12.0f * EffectiveScale;
}

void AJDGiantCharacter::ApplyGiantScale()
{
	const float Scale = GetGiantScale();
	const float Froude = FMath::Sqrt(Scale);   // kecepatan & waktu makhluk besar naik ~ akar ukuran

	const float HalfHeight = AuthoredCapsuleHalfHeight * Scale;
	GetCapsuleComponent()->SetCapsuleSize(AuthoredCapsuleRadius * Scale, HalfHeight);

	GetMesh()->SetRelativeScale3D(FVector(GiantHeightCm / FMath::Max(MeshHeightCm, 1.0f)));
	GetMesh()->SetRelativeLocation(FVector(0.0f, 0.0f, -HalfHeight));
	// Animasi manusia diputar 1/sqrt(skala) kali: langkah berat & kaki menapak pada kecepatan Froude. Sumbu Speed
	// BlendSpace raksasa dikali sqrt(skala) oleh Tools/ue_setup_giant.py supaya cocok.
	GetMesh()->GlobalAnimRateScale = 1.0f / Froude;

	UCharacterMovementComponent* Movement = GetCharacterMovement();
	Movement->MaxWalkSpeed = HumanWalkSpeed * Froude;
	Movement->JumpZVelocity = HumanJumpZVelocity * Froude;
	Movement->BrakingDecelerationWalking = 2000.0f * Froude;
	Movement->RotationRate = FRotator(0.0f, HumanTurnRate / Froude, 0.0f);
	Movement->MaxStepHeight = 45.0f * Scale;

	ApplyCameraScale(Scale);
}
