#include "Characters/JDCharacterBase.h"

#include "EnhancedInputComponent.h"
#include "GameFramework/Controller.h"
#include "InputActionValue.h"
#include "Jayadwara.h"

AJDCharacterBase::AJDCharacterBase()
{
	// Gerak ditangani CharacterMovementComponent (tick sendiri); actor-nya tidak perlu tick.
	PrimaryActorTick.bCanEverTick = false;
}

void AJDCharacterBase::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
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
		Input->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AJDCharacterBase::Move);
	}
	if (LookAction)
	{
		Input->BindAction(LookAction, ETriggerEvent::Triggered, this, &AJDCharacterBase::Look);
	}
	if (MouseLookAction)
	{
		Input->BindAction(MouseLookAction, ETriggerEvent::Triggered, this, &AJDCharacterBase::Look);
	}
	if (JumpAction)
	{
		Input->BindAction(JumpAction, ETriggerEvent::Started, this, &ACharacter::Jump);
		Input->BindAction(JumpAction, ETriggerEvent::Completed, this, &ACharacter::StopJumping);
	}
}

void AJDCharacterBase::Move(const FInputActionValue& Value)
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

void AJDCharacterBase::Look(const FInputActionValue& Value)
{
	const FVector2D Axis = Value.Get<FVector2D>();
	AddControllerYawInput(Axis.X);
	AddControllerPitchInput(Axis.Y);
}
