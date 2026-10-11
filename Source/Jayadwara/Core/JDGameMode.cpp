#include "Core/JDGameMode.h"

#include "Characters/JDHumanCharacter.h"
#include "Core/JDPlayerController.h"

AJDGameMode::AJDGameMode()
{
	// Nilai cadangan; Blueprint turunan menggantinya dengan BP_Aksa (yang punya mesh & Input Action).
	DefaultPawnClass = AJDHumanCharacter::StaticClass();
	PlayerControllerClass = AJDPlayerController::StaticClass();
}
