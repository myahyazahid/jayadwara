#include "Core/JDPlayerController.h"

#include "Engine/LocalPlayer.h"
#include "EnhancedInputSubsystems.h"
#include "InputMappingContext.h"
#include "Jayadwara.h"

void AJDPlayerController::BeginPlay()
{
	Super::BeginPlay();

	if (!IsLocalPlayerController())
	{
		return;
	}

	if (HumanMappingContexts.IsEmpty())
	{
		UE_LOG(LogJayadwara, Warning, TEXT("%s: Human Mapping Contexts kosong; isi di Blueprint (Class Defaults > Input)."), *GetName());
		return;
	}

	UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(GetLocalPlayer());
	if (!Subsystem)
	{
		return;
	}

	for (UInputMappingContext* Context : HumanMappingContexts)
	{
		if (Context)
		{
			Subsystem->AddMappingContext(Context, 0);
		}
	}
}
