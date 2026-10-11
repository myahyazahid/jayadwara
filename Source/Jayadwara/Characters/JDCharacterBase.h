#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "JDCharacterBase.generated.h"

/**
 * Basis semua karakter: Aksa, Jayadwara, musuh (docs/12 "Karakter & Transformasi").
 * AbilitySystemComponent, UJDAttributeSet, dan UJDCombatComponent ditambahkan di Fase 1.
 */
UCLASS(Abstract)
class JAYADWARA_API AJDCharacterBase : public ACharacter
{
	GENERATED_BODY()

public:
	AJDCharacterBase();
};
