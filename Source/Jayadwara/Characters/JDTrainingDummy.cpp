#include "Characters/JDTrainingDummy.h"

#include "Abilities/JDAbilitySystemComponent.h"
#include "Abilities/JDAttributeSet.h"
#include "Abilities/JDGameplayTags.h"
#include "Components/CapsuleComponent.h"
#include "DrawDebugHelpers.h"
#include "Engine/World.h"
#include "Jayadwara.h"
#include "Kismet/GameplayStatics.h"
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
	SetAttackMode(bAttackMode);
}

void AJDTrainingDummy::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	GetWorldTimerManager().ClearAllTimersForObject(this);
	Super::EndPlay(EndPlayReason);
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

// ------------------------------------------------------------------ mode menyerang

void AJDTrainingDummy::SetAttackMode(bool bEnable)
{
	bAttackMode = bEnable;
	if (!HasActorBegunPlay())
	{
		return;
	}
	FTimerManager& Timers = GetWorldTimerManager();
	Timers.ClearTimer(WindUpTimer);
	Timers.ClearTimer(FlashTimer);
	if (bAttackMode)
	{
		Timers.SetTimer(AttackTimer, this, &AJDTrainingDummy::AttackTick, AttackInterval, true, 1.0f);
	}
	else
	{
		Timers.ClearTimer(AttackTimer);
	}
}

APawn* AJDTrainingDummy::GetAttackTarget() const
{
	APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0);
	const UAbilitySystemComponent* PlayerASC = Player ? Player->FindComponentByClass<UAbilitySystemComponent>() : nullptr;
	if (!Player || (PlayerASC && PlayerASC->HasMatchingGameplayTag(JDGameplayTags::State_Dead)))
	{
		return nullptr;
	}
	// Jarak antar-permukaan kapsul, supaya skala pemain (manusia/raksasa) tidak mengubah rasa jarak.
	const float PlayerRadius = Player->GetSimpleCollisionRadius();
	const float Gap = FVector::Dist2D(Player->GetActorLocation(), GetActorLocation()) - PlayerRadius
		- GetCapsuleComponent()->GetScaledCapsuleRadius();
	return Gap <= AttackRange * GetActorScale3D().X ? Player : nullptr;
}

void AJDTrainingDummy::FaceTarget(const APawn* Target)
{
	if (Target)
	{
		const FVector To = (Target->GetActorLocation() - GetActorLocation()).GetSafeNormal2D();
		SetActorRotation(FRotator(0.0f, To.Rotation().Yaw, 0.0f));
	}
}

void AJDTrainingDummy::AttackTick()
{
	const APawn* Target = GetAttackTarget();
	if (!Target || !AbilitySystemComponent || AbilitySystemComponent->HasMatchingGameplayTag(JDGameplayTags::State_Stagger)
		|| AbilitySystemComponent->HasMatchingGameplayTag(JDGameplayTags::State_Attacking))
	{
		return;
	}

	FaceTarget(Target);
	FlashCount = 0;
	FlashTelegraph();
	GetWorldTimerManager().SetTimer(FlashTimer, this, &AJDTrainingDummy::FlashTelegraph, 0.1f, true);
	GetWorldTimerManager().SetTimer(WindUpTimer, this, &AJDTrainingDummy::ReleaseAttack, FMath::Max(WindUpTime, 0.01f), false);
}

void AJDTrainingDummy::FlashTelegraph()
{
	// Kedip 0,1 s nyala / 0,1 s mati di atas kepala.
	const bool bOn = (FlashCount++ % 2) == 0;
	if (!bOn)
	{
		return;
	}
	const float Scale = GetActorScale3D().X;
	const FVector Head = GetActorLocation() + FVector(0.0f, 0.0f, GetCapsuleComponent()->GetScaledCapsuleHalfHeight() + 35.0f * Scale);
	DrawDebugSphere(GetWorld(), Head, 18.0f * Scale, 10, FColor::Red, false, 0.1f, 0, 3.0f * Scale);
	DrawDebugString(GetWorld(), Head + FVector(0.0f, 0.0f, 30.0f * Scale), TEXT("!"), nullptr, FColor::Red, 0.1f, true, 2.5f);
}

void AJDTrainingDummy::ReleaseAttack()
{
	GetWorldTimerManager().ClearTimer(FlashTimer);
	if (!AbilitySystemComponent || AbilitySystemComponent->HasMatchingGameplayTag(JDGameplayTags::State_Stagger))
	{
		return;
	}
	if (const APawn* Target = GetAttackTarget())
	{
		FaceTarget(Target);
	}
	const bool bActivated = AbilitySystemComponent->TryActivateAbilitiesByTag(FGameplayTagContainer(JDGameplayTags::Ability_Attack_Light));
	UE_LOG(LogJayadwara, Verbose, TEXT("%s: serang %s"), *GetName(), bActivated ? TEXT("ya") : TEXT("gagal aktif"));
}
