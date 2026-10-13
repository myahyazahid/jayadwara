#include "Characters/JDTrainingDummy.h"

#include "Abilities/JDAbilitySystemComponent.h"
#include "Abilities/JDAttributeSet.h"
#include "Abilities/JDGameplayTags.h"
#include "Components/CapsuleComponent.h"
#include "DrawDebugHelpers.h"
#include "Engine/World.h"
#include "TimerManager.h"

AJDTrainingDummy::AJDTrainingDummy()
{
	// Diam di tempat: tanpa AI controller, kapsul setinggi Manny.
	AutoPossessAI = EAutoPossessAI::Disabled;
	GetCapsuleComponent()->InitCapsuleSize(42.0f, 96.0f);
}

void AJDTrainingDummy::BeginPlay()
{
	Super::BeginPlay();

	if (AbilitySystemComponent)
	{
		AbilitySystemComponent->GetGameplayAttributeValueChangeDelegate(UJDAttributeSet::GetHealthAttribute())
			.AddUObject(this, &AJDTrainingDummy::OnHealthChanged);
	}
}

void AJDTrainingDummy::OnHealthChanged(const FOnAttributeChangeData& Data)
{
	const float Damage = Data.OldValue - Data.NewValue;
	if (Damage <= 0.0f)
	{
		return;
	}

	++ComboHits;
	ComboDamage += Damage;

	if (bShowDamageNumbers)
	{
		const float HalfHeight = GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
		const FVector Offset(FMath::FRandRange(-20.0f, 20.0f), FMath::FRandRange(-20.0f, 20.0f), HalfHeight + 30.0f + 12.0f * (ComboHits % 4));
		DrawDebugString(GetWorld(), GetActorLocation() + Offset, FString::Printf(TEXT("-%.0f"), Damage), nullptr,
			FColor::Yellow, 0.9f, true, 1.6f);
		DrawDebugString(GetWorld(), GetActorLocation() + FVector(0.0f, 0.0f, HalfHeight + 90.0f),
			FString::Printf(TEXT("%d hit / %.0f"), ComboHits, ComboDamage), nullptr, FColor::White, ResetDelay, true, 1.2f);
	}

	GetWorldTimerManager().SetTimer(ResetTimer, this, &AJDTrainingDummy::ResetAttributes, ResetDelay, false);
}

void AJDTrainingDummy::HandleOutOfHealth(AActor* DamageInstigator, float DamageAmount)
{
	// Tidak mati: penuh lagi sebentar lagi.
	GetWorldTimerManager().SetTimer(ResetTimer, this, &AJDTrainingDummy::ResetAttributes, 1.0f, false);
}

void AJDTrainingDummy::ResetAttributes()
{
	ComboHits = 0;
	ComboDamage = 0.0f;
	if (!AbilitySystemComponent)
	{
		return;
	}
	AbilitySystemComponent->SetNumericAttributeBase(UJDAttributeSet::GetHealthAttribute(),
		AbilitySystemComponent->GetNumericAttribute(UJDAttributeSet::GetMaxHealthAttribute()));
	AbilitySystemComponent->SetNumericAttributeBase(UJDAttributeSet::GetPoiseAttribute(),
		AbilitySystemComponent->GetNumericAttribute(UJDAttributeSet::GetMaxPoiseAttribute()));
	AbilitySystemComponent->SetLooseGameplayTagCount(JDGameplayTags::State_Dead, 0);
}
