#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "JDCharacterBase.generated.h"

class UInputAction;
struct FInputActionValue;

/**
 * Basis semua karakter: Aksa, Jayadwara, musuh (docs/12 "Karakter & Transformasi").
 * Gerak dasar yang dikendalikan pemain (Move/Look/Jump, Enhanced Input) ada di sini karena dipakai mode manusia dan raksasa;
 * musuh tidak terpengaruh (SetupPlayerInputComponent hanya jalan saat dikendalikan pemain).
 * AbilitySystemComponent, UJDAttributeSet, dan UJDCombatComponent ditambahkan di Fase 1.
 */
UCLASS(Abstract)
class JAYADWARA_API AJDCharacterBase : public ACharacter
{
	GENERATED_BODY()

public:
	AJDCharacterBase();

protected:
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

	void Move(const FInputActionValue& Value);
	void Look(const FInputActionValue& Value);

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
