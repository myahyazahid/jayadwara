#include "Characters/JDHumanCharacter.h"

#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "EnhancedInputComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"
#include "GameFramework/SpringArmComponent.h"
#include "InputActionValue.h"
#include "Jayadwara.h"

AJDHumanCharacter::AJDHumanCharacter()
{
	GetCapsuleComponent()->InitCapsuleSize(42.0f, 96.0f);

	// Kamera mengikuti arah kontrol, badan menghadap arah gerak.
	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;

	UCharacterMovementComponent* Movement = GetCharacterMovement();
	Movement->bOrientRotationToMovement = true;
	Movement->RotationRate = FRotator(0.0f, 500.0f, 0.0f);
	Movement->JumpZVelocity = 500.0f;
	Movement->AirControl = 0.35f;
	Movement->MaxWalkSpeed = 500.0f;
	Movement->MinAnalogWalkSpeed = 20.0f;
	Movement->BrakingDecelerationWalking = 2000.0f;

	CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
	CameraBoom->SetupAttachment(RootComponent);
	CameraBoom->TargetArmLength = 400.0f;
	CameraBoom->bUsePawnControlRotation = true;

	FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
	FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
	FollowCamera->bUsePawnControlRotation = false;
}

void AJDHumanCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	UEnhancedInputComponent* Input = Cast<UEnhancedInputComponent>(PlayerInputComponent);
	if (!Input)
	{
		UE_LOG(LogJayadwara, Error, TEXT("%s: input component bukan Enhanced Input; cek Project Settings > Input > Default Classes."), *GetName());
		return;
	}

	if (!MoveAction || !LookAction || !JumpAction)
	{
		UE_LOG(LogJayadwara, Warning, TEXT("%s: Move/Look/Jump Action belum diisi di Blueprint (Class Defaults > Input)."), *GetName());
	}

	if (MoveAction)
	{
		Input->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AJDHumanCharacter::Move);
	}
	if (LookAction)
	{
		Input->BindAction(LookAction, ETriggerEvent::Triggered, this, &AJDHumanCharacter::Look);
	}
	if (MouseLookAction)
	{
		Input->BindAction(MouseLookAction, ETriggerEvent::Triggered, this, &AJDHumanCharacter::Look);
	}
	if (JumpAction)
	{
		Input->BindAction(JumpAction, ETriggerEvent::Started, this, &ACharacter::Jump);
		Input->BindAction(JumpAction, ETriggerEvent::Completed, this, &ACharacter::StopJumping);
	}
}

void AJDHumanCharacter::Move(const FInputActionValue& Value)
{
	if (!Controller)
	{
		return;
	}

	// Maju/samping relatif terhadap arah kamera (yaw saja).
	const FVector2D Axis = Value.Get<FVector2D>();
	const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
	const FRotationMatrix YawMatrix(YawRotation);

	AddMovementInput(YawMatrix.GetUnitAxis(EAxis::X), Axis.Y);
	AddMovementInput(YawMatrix.GetUnitAxis(EAxis::Y), Axis.X);
}

void AJDHumanCharacter::Look(const FInputActionValue& Value)
{
	const FVector2D Axis = Value.Get<FVector2D>();
	AddControllerYawInput(Axis.X);
	AddControllerPitchInput(Axis.Y);
}
