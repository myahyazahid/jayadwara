#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "JDPlayerController.generated.h"

class UInputMappingContext;

/**
 * Pemain. Memasang mapping context mode manusia (docs/12 "Input").
 * IMC_Giant dan pergantian pawn saat transformasi ditambahkan di Fase 1 (Feb 2027).
 */
UCLASS()
class JAYADWARA_API AJDPlayerController : public APlayerController
{
	GENERATED_BODY()

protected:
	virtual void BeginPlay() override;

	/** IMC mode manusia. Array karena konten Third Person bawaan 5.6 bisa memisahkan mouse look ke IMC sendiri. */
	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TArray<TObjectPtr<UInputMappingContext>> HumanMappingContexts;
};
