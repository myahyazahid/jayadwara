#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "JDHUDWidget.generated.h"

class UAbilitySystemComponent;
class UProgressBar;
class UTextBlock;
class UVerticalBox;
struct FGameplayAttribute;

/**
 * HUD debug Fase 1 (docs/23 bagian 2: fungsional, bukan visual final). Membaca atribut GAS pawn yang sedang
 * dikendalikan (ikut berganti saat transformasi) setiap frame.
 *
 * Bisa dipakai langsung (tanpa WBP): kalau tidak ada layout dari Widget Blueprint, kelas ini membuat sendiri bar
 * Health/Stamina di kiri bawah. WBP_HUD_* turunan boleh menaruh ProgressBar bernama HealthBar, StaminaBar, SyncBar,
 * TransformEnergyBar (+ TextBlock *Text) di mana saja; yang tidak ada dilewati. Bar untuk atribut ber-Max 0
 * disembunyikan (mis. Sync saat jadi Aksa).
 */
UCLASS()
class JAYADWARA_API UJDHUDWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	/** Health / MaxHealth pawn pemain (0 kalau tidak ada). */
	UFUNCTION(BlueprintPure, Category = "HUD")
	float GetHealthPercent() const;

	UFUNCTION(BlueprintPure, Category = "HUD")
	float GetStaminaPercent() const;

	UFUNCTION(BlueprintPure, Category = "HUD")
	float GetSyncPercent() const;

	UFUNCTION(BlueprintPure, Category = "HUD")
	float GetTransformEnergyPercent() const;

protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

	UPROPERTY(BlueprintReadOnly, Category = "HUD", meta = (BindWidgetOptional))
	TObjectPtr<UProgressBar> HealthBar;

	UPROPERTY(BlueprintReadOnly, Category = "HUD", meta = (BindWidgetOptional))
	TObjectPtr<UProgressBar> StaminaBar;

	UPROPERTY(BlueprintReadOnly, Category = "HUD", meta = (BindWidgetOptional))
	TObjectPtr<UProgressBar> SyncBar;

	UPROPERTY(BlueprintReadOnly, Category = "HUD", meta = (BindWidgetOptional))
	TObjectPtr<UProgressBar> TransformEnergyBar;

	UPROPERTY(BlueprintReadOnly, Category = "HUD", meta = (BindWidgetOptional))
	TObjectPtr<UTextBlock> HealthText;

	UPROPERTY(BlueprintReadOnly, Category = "HUD", meta = (BindWidgetOptional))
	TObjectPtr<UTextBlock> StaminaText;

	UPROPERTY(BlueprintReadOnly, Category = "HUD", meta = (BindWidgetOptional))
	TObjectPtr<UTextBlock> SyncText;

	UPROPERTY(BlueprintReadOnly, Category = "HUD", meta = (BindWidgetOptional))
	TObjectPtr<UTextBlock> TransformEnergyText;

private:
	UAbilitySystemComponent* GetPawnASC() const;
	float GetPercent(const FGameplayAttribute& Value, const FGameplayAttribute& Max) const;

	/** Layout bawaan (kiri bawah) saat kelas dipakai tanpa WBP. */
	void BuildDefaultLayout();
	void AddDefaultRow(UVerticalBox* Box, const FText& Label, const FLinearColor& Color, TObjectPtr<UProgressBar>& OutBar, TObjectPtr<UTextBlock>& OutText);

	void UpdateRow(UProgressBar* Bar, UTextBlock* Text, const FGameplayAttribute& Value, const FGameplayAttribute& Max) const;
};
