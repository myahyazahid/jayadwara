#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "GameplayTagContainer.h"
#include "JDInputConfig.generated.h"

class UInputAction;

/** Satu Input Action yang memicu ability lewat input tag. */
USTRUCT(BlueprintType)
struct FJDInputAction
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	TObjectPtr<const UInputAction> InputAction = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input", meta = (Categories = "Input"))
	FGameplayTag InputTag;
};

/**
 * Input Action -> input tag (docs/23 bagian 4.1). Karakter mengikat tiap aksi di sini ke UJDAbilitySystemComponent
 * (tekan / lepas); ability yang diberikan dengan tag yang sama (UJDAbilitySet) yang menanggapi. Gerak, kamera, dan
 * lompat tetap diikat langsung di AJDCharacterBase; transformasi di AJDPlayerController.
 * Aset: DA_InputConfig_Human (dibuat Tools/ue_setup_combat.py).
 */
UCLASS(BlueprintType, Const)
class JAYADWARA_API UJDInputConfig : public UDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input", meta = (TitleProperty = "InputTag"))
	TArray<FJDInputAction> AbilityInputActions;
};
