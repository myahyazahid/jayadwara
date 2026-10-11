#include "Characters/JDGiantCharacter.h"

#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"

AJDGiantCharacter::AJDGiantCharacter()
{
	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;

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

void AJDGiantCharacter::ApplyGiantScale()
{
	const float Scale = GetGiantScale();
	const float Froude = FMath::Sqrt(Scale);   // kecepatan & waktu makhluk besar naik ~ akar ukuran

	const float HalfHeight = AuthoredCapsuleHalfHeight * Scale;
	GetCapsuleComponent()->SetCapsuleSize(AuthoredCapsuleRadius * Scale, HalfHeight);

	GetMesh()->SetRelativeScale3D(FVector(Scale));
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

	CameraBoom->TargetArmLength = AuthoredCameraDistance * Scale;
	CameraBoom->SocketOffset = FVector(0.0f, 0.0f, 40.0f * Scale);
	CameraBoom->ProbeSize = 12.0f * Scale;
}
