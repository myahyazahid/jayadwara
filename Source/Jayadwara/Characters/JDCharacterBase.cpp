#include "Characters/JDCharacterBase.h"

#include "Abilities/JDAbilitySet.h"
#include "Abilities/JDAbilitySystemComponent.h"
#include "Abilities/JDAttributeSet.h"
#include "Abilities/JDGameplayTags.h"
#include "Abilities/JDInputConfig.h"
#include "Combat/JDCombatComponent.h"
#include "EnhancedInputComponent.h"
#include "GameFramework/Controller.h"
#include "InputActionValue.h"
#include "Jayadwara.h"

AJDCharacterBase::AJDCharacterBase()
{
	// Gerak ditangani CharacterMovementComponent (tick sendiri); actor-nya tidak perlu tick.
	PrimaryActorTick.bCanEverTick = false;

	AbilitySystemComponent = CreateDefaultSubobject<UJDAbilitySystemComponent>(TEXT("AbilitySystem"));
	// Subobject AttributeSet milik actor pemilik ASC otomatis terdaftar di ASC saat InitializeComponent.
	AttributeSet = CreateDefaultSubobject<UJDAttributeSet>(TEXT("AttributeSet"));
	CombatComponent = CreateDefaultSubobject<UJDCombatComponent>(TEXT("Combat"));
}

UAbilitySystemComponent* AJDCharacterBase::GetAbilitySystemComponent() const
{
	return AbilitySystemComponent;
}

void AJDCharacterBase::BeginPlay()
{
	Super::BeginPlay();

	if (!AbilitySystemComponent)
	{
		return;
	}
	AbilitySystemComponent->InitAbilityActorInfo(this, this);

	AttributeSet->OnOutOfHealth.AddUObject(this, &AJDCharacterBase::HandleOutOfHealth);

	if (AbilitySet)
	{
		AbilitySet->GiveToAbilitySystem(AbilitySystemComponent);
	}
	else
	{
		UE_LOG(LogJayadwara, Warning, TEXT("%s: Ability Set kosong; atribut tetap 0 (Class Defaults > Abilities)."), *GetName());
	}
}

void AJDCharacterBase::PossessedBy(AController* NewController)
{
	Super::PossessedBy(NewController);

	// Controller berubah (transformasi, AI): actor info ASC harus menunjuk controller baru.
	if (AbilitySystemComponent)
	{
		AbilitySystemComponent->InitAbilityActorInfo(this, this);
	}
}

void AJDCharacterBase::UnPossessed()
{
	if (AbilitySystemComponent)
	{
		AbilitySystemComponent->ClearAbilityInput();
	}
	Super::UnPossessed();
}

void AJDCharacterBase::HandleOutOfHealth(AActor* DamageInstigator, float DamageAmount)
{
	UE_LOG(LogJayadwara, Log, TEXT("%s: Health habis (damage terakhir %.1f dari %s)"), *GetName(), DamageAmount, *GetNameSafe(DamageInstigator));
	if (AbilitySystemComponent)
	{
		AbilitySystemComponent->SetLooseGameplayTagCount(JDGameplayTags::State_Dead, 1);
	}
}

void AJDCharacterBase::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	UEnhancedInputComponent* Input = Cast<UEnhancedInputComponent>(PlayerInputComponent);
	if (!Input)
	{
		UE_LOG(LogJayadwara, Error, TEXT("%s: input component bukan Enhanced Input; cek Project Settings > Input > Default Classes."), *GetName());
		return;
	}

	if (!MoveAction || !LookAction || !JumpAction)
	{
		UE_LOG(LogJayadwara, Warning, TEXT("%s: Move/Look/Jump Action belum diisi di Blueprint (Class Defaults > Input)."), *GetName());
	}

	if (MoveAction)
	{
		Input->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AJDCharacterBase::Move);
	}
	if (LookAction)
	{
		Input->BindAction(LookAction, ETriggerEvent::Triggered, this, &AJDCharacterBase::Look);
	}
	if (MouseLookAction)
	{
		Input->BindAction(MouseLookAction, ETriggerEvent::Triggered, this, &AJDCharacterBase::Look);
	}
	if (JumpAction)
	{
		Input->BindAction(JumpAction, ETriggerEvent::Started, this, &ACharacter::Jump);
		Input->BindAction(JumpAction, ETriggerEvent::Completed, this, &ACharacter::StopJumping);
	}

	// Aksi combat: tekan/lepas diteruskan ke ASC sebagai input tag; aktivasi diproses di AJDPlayerController::PostProcessInput.
	if (InputConfig)
	{
		for (const FJDInputAction& Entry : InputConfig->AbilityInputActions)
		{
			if (Entry.InputAction && Entry.InputTag.IsValid())
			{
				Input->BindAction(Entry.InputAction, ETriggerEvent::Started, this, &AJDCharacterBase::AbilityInputPressed, Entry.InputTag);
				Input->BindAction(Entry.InputAction, ETriggerEvent::Completed, this, &AJDCharacterBase::AbilityInputReleased, Entry.InputTag);
			}
		}
	}
}

void AJDCharacterBase::AbilityInputPressed(FGameplayTag InputTag)
{
	if (AbilitySystemComponent)
	{
		AbilitySystemComponent->AbilityInputTagPressed(InputTag);
	}
}

void AJDCharacterBase::AbilityInputReleased(FGameplayTag InputTag)
{
	if (AbilitySystemComponent)
	{
		AbilitySystemComponent->AbilityInputTagReleased(InputTag);
	}
}

void AJDCharacterBase::Move(const FInputActionValue& Value)
{
	if (!Controller)
	{
		return;
	}
	// Stagger (guard break, di-parry) dan mati menahan gerak.
	if (AbilitySystemComponent && (AbilitySystemComponent->HasMatchingGameplayTag(JDGameplayTags::State_Stagger)
		|| AbilitySystemComponent->HasMatchingGameplayTag(JDGameplayTags::State_Dead)))
	{
		return;
	}

	// Maju/samping relatif terhadap arah kamera (yaw saja).
	const FVector2D Axis = Value.Get<FVector2D>();
	const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
	const FRotationMatrix YawMatrix(YawRotation);

	AddMovementInput(YawMatrix.GetUnitAxis(EAxis::X), Axis.Y);
	AddMovementInput(YawMatrix.GetUnitAxis(EAxis::Y), Axis.X);
}

void AJDCharacterBase::Look(const FInputActionValue& Value)
{
	const FVector2D Axis = Value.Get<FVector2D>();
	AddControllerYawInput(Axis.X);
	AddControllerPitchInput(Axis.Y);
}
