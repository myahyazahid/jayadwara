#pragma once

#include "CoreMinimal.h"
#include "Characters/JDCharacterBase.h"
#include "JDHumanCharacter.generated.h"

class UCameraComponent;
class USpringArmComponent;

/**
 * Aksa dalam mode manusia: kamera orang-ketiga; gerak & input dari AJDCharacterBase.
 * Mesh, animasi, dan Input Action diisi di Blueprint turunan (BP_Aksa). Combo silat dan scanner Netra menyusul di Fase 1.
 */
UCLASS()
class JAYADWARA_API AJDHumanCharacter : public AJDCharacterBase
{
	GENERATED_BODY()

public:
	AJDHumanCharacter();

protected:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
	TObjectPtr<USpringArmComponent> CameraBoom;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
	TObjectPtr<UCameraComponent> FollowCamera;
};
