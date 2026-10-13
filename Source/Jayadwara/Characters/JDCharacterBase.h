#pragma once

#include "CoreMinimal.h"
#include "AbilitySystemInterface.h"
#include "GameFramework/Character.h"
#include "GameplayTagContainer.h"
#include "JDCharacterBase.generated.h"

class UInputAction;
class UJDAbilitySet;
class UJDAbilitySystemComponent;
class UJDAttributeSet;
class UJDCombatComponent;
class UJDInputConfig;
struct FInputActionValue;

/**
 * Basis semua karakter: Aksa, Jayadwara, musuh (docs/12 "Karakter & Transformasi").
 * Gerak dasar yang dikendalikan pemain (Move/Look/Jump, Enhanced Input) ada di sini karena dipakai mode manusia dan raksasa;
 * musuh tidak terpengaruh (SetupPlayerInputComponent hanya jalan saat dikendalikan pemain).
 *
 * GAS (docs/23 Iterasi 1, R1): ASC + UJDAttributeSet ada di karakter. AbilitySet diberikan saat BeginPlay
 * (atribut awal, ability, regen). Aksi combat diikat lewat InputConfig ke input tag ASC. UJDCombatComponent (hitbox,
 * hit-stop, profil combat per skala) dipakai semua karakter (Iterasi 2).
 */
UCLASS(Abstract)
class JAYADWARA_API AJDCharacterBase : public ACharacter, public IAbilitySystemInterface
{
	GENERATED_BODY()

public:
	AJDCharacterBase();

	virtual UAbilitySystemComponent* GetAbilitySystemComponent() const override;

	UFUNCTION(BlueprintPure, Category = "Abilities")
	UJDAbilitySystemComponent* GetJDAbilitySystemComponent() const { return AbilitySystemComponent; }

	UFUNCTION(BlueprintPure, Category = "Abilities")
	const UJDAttributeSet* GetAttributeSet() const { return AttributeSet; }

	UFUNCTION(BlueprintPure, Category = "Combat")
	UJDCombatComponent* GetCombatComponent() const { return CombatComponent; }

	virtual void PossessedBy(AController* NewController) override;
	virtual void UnPossessed() override;

protected:
	virtual void BeginPlay() override;
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

	/** Health habis. Basis: pasang State.Dead + log; mati/checkpoint/roboh ditangani turunan (Iterasi 5, 6). */
	virtual void HandleOutOfHealth(AActor* DamageInstigator, float DamageAmount);

	void Move(const FInputActionValue& Value);
	void Look(const FInputActionValue& Value);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Abilities")
	TObjectPtr<UJDAbilitySystemComponent> AbilitySystemComponent;

	UPROPERTY()
	TObjectPtr<UJDAttributeSet> AttributeSet;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat")
	TObjectPtr<UJDCombatComponent> CombatComponent;

	/** Atribut awal, ability, dan buffer input karakter ini (DA_AbilitySet_*). */
	UPROPERTY(EditDefaultsOnly, Category = "Abilities")
	TObjectPtr<UJDAbilitySet> AbilitySet;

	/** Aksi combat -> input tag (DA_InputConfig_*). Hanya dipakai saat dikendalikan pemain. */
	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UJDInputConfig> InputConfig;

	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UInputAction> MoveAction;

	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UInputAction> LookAction;

	/** Opsional. Konten Third Person bawaan 5.6 memisahkan look mouse (IA_MouseLook) dari look gamepad (IA_Look). */
	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UInputAction> MouseLookAction;

	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UInputAction> JumpAction;

private:
	void AbilityInputPressed(FGameplayTag InputTag);
	void AbilityInputReleased(FGameplayTag InputTag);
};
