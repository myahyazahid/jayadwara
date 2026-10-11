#pragma once

#include "CoreMinimal.h"
#include "Characters/JDCharacterBase.h"
#include "JDHumanCharacter.generated.h"

class UCameraComponent;
class UInputAction;
class USpringArmComponent;
struct FInputActionValue;

/**
 * Aksa dalam mode manusia: gerak, kamera orang-ketiga, lompat.
 * Mesh, animasi, dan Input Action diisi di Blueprint turunan (BP_Aksa). Combo silat dan scanner Netra menyusul di Fase 1.
 */
UCLASS()
class JAYADWARA_API AJDHumanCharacter : public AJDCharacterBase
{
	GENERATED_BODY()

public:
	AJDHumanCharacter();

protected:
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

	void Move(const FInputActionValue& Value);
	void Look(const FInputActionValue& Value);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
	TObjectPtr<USpringArmComponent> CameraBoom;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
	TObjectPtr<UCameraComponent> FollowCamera;

	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UInputAction> MoveAction;

	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UInputAction> LookAction;

	/** Opsional. Konten Third Person bawaan 5.6 memisahkan look mouse (IA_MouseLook) dari look gamepad (IA_Look). */
	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UInputAction> MouseLookAction;

	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UInputAction> JumpAction;
};
