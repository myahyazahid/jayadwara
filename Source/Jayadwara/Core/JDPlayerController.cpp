#include "Core/JDPlayerController.h"

#include "Characters/JDGiantCharacter.h"
#include "Components/CapsuleComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "Engine/LocalPlayer.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
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

void AJDPlayerController::SetupInputComponent()
{
	Super::SetupInputComponent();

	if (!TransformAction)
	{
		UE_LOG(LogJayadwara, Warning, TEXT("%s: Transform Action kosong; transformasi tidak bisa dipicu dari tombol."), *GetName());
		return;
	}

	if (UEnhancedInputComponent* Input = Cast<UEnhancedInputComponent>(InputComponent))
	{
		Input->BindAction(TransformAction, ETriggerEvent::Started, this, &AJDPlayerController::ToggleTransformation);
	}
}

void AJDPlayerController::ToggleTransformation()
{
	if (bTransforming)
	{
		return;
	}

	if (IsGiant())
	{
		RevertToHuman();
	}
	else
	{
		TransformToGiant();
	}
}

void AJDPlayerController::TransformToGiant()
{
	APawn* Current = GetPawn();
	if (bTransforming || IsGiant() || !Current)
	{
		return;
	}

	UWorld* World = GetWorld();
	if (!GiantPawnClass || !World)
	{
		UE_LOG(LogJayadwara, Warning, TEXT("%s: Giant Pawn Class kosong; isi di Blueprint (Class Defaults > Transformation)."), *GetName());
		return;
	}

	// Raksasa muncul setinggi manusia tepat di lokasi & arah Aksa, lalu tumbuh dari situ.
	const AJDGiantCharacter* Defaults = GiantPawnClass->GetDefaultObject<AJDGiantCharacter>();
	const float StartScale = Defaults->GetHumanScale();

	FVector Location = Current->GetActorLocation();
	ACharacter* HumanCharacter = Cast<ACharacter>(Current);
	if (HumanCharacter)
	{
		Location.Z -= HumanCharacter->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
	}
	Location.Z += Defaults->GetGiantHalfHeight() * StartScale;

	const FTransform SpawnTransform(FRotator(0.0f, Current->GetActorRotation().Yaw, 0.0f), Location, FVector(StartScale));
	AJDGiantCharacter* Giant = World->SpawnActorDeferred<AJDGiantCharacter>(
		GiantPawnClass, SpawnTransform, nullptr, nullptr, ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
	if (!Giant)
	{
		return;
	}
	Giant->FinishSpawning(SpawnTransform);

	// Pawn manusia disembunyikan, bukan dihapus; gerak dimatikan supaya tidak jatuh menembus lantai tanpa kolisi.
	HumanPawn = Current;
	if (HumanCharacter)
	{
		HumanCharacter->GetCharacterMovement()->StopMovementImmediately();
		HumanCharacter->GetCharacterMovement()->DisableMovement();
	}
	Current->SetActorHiddenInGame(true);
	Current->SetActorEnableCollision(false);

	GiantPawn = Giant;
	bTransforming = true;
	PossessKeepingView(Giant);

	TWeakObjectPtr<AJDPlayerController> WeakThis(this);
	Giant->BeginScaleTransition(true, TransformDuration, [WeakThis]()
	{
		if (AJDPlayerController* Self = WeakThis.Get())
		{
			Self->OnTransformedToGiant();
		}
	});
}

void AJDPlayerController::OnTransformedToGiant()
{
	bTransforming = false;
}

void AJDPlayerController::RevertToHuman()
{
	if (bTransforming || !IsGiant())
	{
		return;
	}

	bTransforming = true;

	TWeakObjectPtr<AJDPlayerController> WeakThis(this);
	GiantPawn->BeginScaleTransition(false, TransformDuration, [WeakThis]()
	{
		if (AJDPlayerController* Self = WeakThis.Get())
		{
			Self->OnRevertedToHuman();
		}
	});
}

void AJDPlayerController::OnRevertedToHuman()
{
	AJDGiantCharacter* Giant = GiantPawn;
	APawn* Human = HumanPawn;
	GiantPawn = nullptr;
	HumanPawn = nullptr;
	bTransforming = false;

	if (!Giant || !Human)
	{
		return;
	}

	// Aksa muncul di tapak kaki raksasa yang sudah menyusut sebesar manusia, menghadap arah yang sama.
	FVector Location = Giant->GetActorLocation();
	Location.Z -= Giant->GetGiantHalfHeight() * Giant->GetActorScale3D().Z;
	ACharacter* HumanCharacter = Cast<ACharacter>(Human);
	if (HumanCharacter)
	{
		Location.Z += HumanCharacter->GetCapsuleComponent()->GetScaledCapsuleHalfHeight() + 2.0f;
	}

	Human->SetActorLocationAndRotation(Location, FRotator(0.0f, Giant->GetActorRotation().Yaw, 0.0f), false, nullptr, ETeleportType::TeleportPhysics);
	Human->SetActorEnableCollision(true);
	Human->SetActorHiddenInGame(false);
	if (HumanCharacter)
	{
		HumanCharacter->GetCharacterMovement()->SetMovementMode(MOVE_Falling);
	}

	PossessKeepingView(Human);
	Giant->Destroy();
}

void AJDPlayerController::PossessKeepingView(APawn* NewPawn)
{
	const FRotator View = GetControlRotation();
	Possess(NewPawn);
	SetControlRotation(View);
}
