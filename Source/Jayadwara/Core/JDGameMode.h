#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "JDGameMode.generated.h"

/**
 * Game mode dasar. Di editor dipakai turunan BP_JDGameMode yang menunjuk BP_Aksa dan BP_JDPlayerController.
 */
UCLASS()
class JAYADWARA_API AJDGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	AJDGameMode();
};
