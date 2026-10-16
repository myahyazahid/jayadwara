#include "Characters/JDGiantCharacter.h"

#include "Camera/CameraComponent.h"
#include "Characters/JDCapeComponent.h"
#include "Components/InputComponent.h"
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

	CapeControl = CreateDefaultSubobject<UJDCapeComponent>(TEXT("CapeControl"));

	ApplyGiantScale();
}

void AJDGiantCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	// SEMENTARA (docs/26 J1b): Y = lepas/pakai jubah, tanpa Input Action. Pemicu final (lock-on, aksi combat) di J4.
	PlayerInputComponent->BindKey(EKeys::Y, IE_Pressed, this, &AJDGiantCharacter::DebugToggleCape);
}

void AJDGiantCharacter::DebugToggleCape()
{
	if (CapeControl)
	{
		CapeControl->ToggleCape();
	}
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

float AJDGiantCharacter::GetSpeedScale() const
{
	return FMath::Pow(GetGiantScale(), SpeedScaleExponent);
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
	const float Froude = FMath::Sqrt(Scale);   // lompatan: kecepatan naik ~ akar ukuran (tinggi lompat sebanding ukuran)
	const float Speed = GetSpeedScale();       // gerak: skala^SpeedScaleExponent (0,83 = ala Mebius, 0,5 = Froude)

	const float HalfHeight = AuthoredCapsuleHalfHeight * Scale;
	GetCapsuleComponent()->SetCapsuleSize(AuthoredCapsuleRadius * Scale, HalfHeight);

	GetMesh()->SetRelativeScale3D(FVector(GiantHeightCm / FMath::Max(MeshHeightCm, 1.0f)));
	GetMesh()->SetRelativeLocation(FVector(0.0f, 0.0f, -HalfHeight));
	// Langkah raksasa = langkah manusia x Scale; supaya kaki menapak pada kecepatan manusia x Speed, animasi diputar
	// Speed / Scale kali. Sumbu Speed BlendSpace raksasa dikali Speed oleh Tools/ue_setup_giant_speed.py.
	GetMesh()->GlobalAnimRateScale = Speed / Scale;

	UCharacterMovementComponent* Movement = GetCharacterMovement();
	Movement->MaxWalkSpeed = HumanWalkSpeed * Speed;
	Movement->MaxAcceleration = HumanMaxAcceleration * Speed;   // lari penuh dalam waktu yang sama dengan manusia
	Movement->BrakingDecelerationWalking = 2000.0f * Speed;
	Movement->JumpZVelocity = HumanJumpZVelocity * Froude * JumpBoost;
	Movement->RotationRate = FRotator(0.0f, GiantTurnRate, 0.0f);
	Movement->MaxStepHeight = 45.0f * Scale;

	ApplyCameraScale(Scale);
}
