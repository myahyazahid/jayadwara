#include "Combat/JDCombatComponent.h"

#include "AbilitySystemBlueprintLibrary.h"
#include "AbilitySystemComponent.h"
#include "AbilitySystemGlobals.h"
#include "Abilities/JDGameplayEffects.h"
#include "Abilities/JDGameplayTags.h"
#include "Camera/CameraShakeBase.h"
#include "Components/SkeletalMeshComponent.h"
#include "DrawDebugHelpers.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/PlayerController.h"
#include "HAL/IConsoleManager.h"
#include "TimerManager.h"

static TAutoConsoleVariable<bool> CVarDebugHitbox(
	TEXT("JD.Debug.Hitbox"), false,
	TEXT("1 = gambar sweep hitbox (hijau) dan titik kena (merah) selama JD Hit Window."));

UJDCombatComponent::UJDCombatComponent()
{
	// Hitbox digerakkan tick notify montage, bukan tick komponen.
	PrimaryComponentTick.bCanEverTick = false;
}

void UJDCombatComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	EndHitStop();
	Super::EndPlay(EndPlayReason);
}

USkeletalMeshComponent* UJDCombatComponent::GetOwnerMesh() const
{
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	return Character ? Character->GetMesh() : GetOwner()->FindComponentByClass<USkeletalMeshComponent>();
}

FVector UJDCombatComponent::GetSocketLocation() const
{
	const USkeletalMeshComponent* Mesh = GetOwnerMesh();
	return Mesh ? Mesh->GetSocketLocation(HitSocket) : GetOwner()->GetActorLocation();
}

void UJDCombatComponent::BeginAttack(const FJDAttackStep& Attack)
{
	EndHitWindow();
	CurrentAttack = Attack;
	bAttackActive = true;
	HitActors.Reset();
}

void UJDCombatComponent::EndAttack()
{
	EndHitWindow();
	bAttackActive = false;
	HitActors.Reset();
}

void UJDCombatComponent::BeginHitWindow(FName SocketName, float RadiusOverride)
{
	if (!bAttackActive)
	{
		return;
	}
	bHitWindowOpen = true;
	HitSocket = SocketName;
	HitRadius = RadiusOverride > 0.0f ? RadiusOverride : (CombatProfile ? CombatProfile->HitRadius : 30.0f);
	LastSocketLocation = GetSocketLocation();
	UpdateHitWindow();
}

void UJDCombatComponent::UpdateHitWindow()
{
	UWorld* World = GetWorld();
	if (!bHitWindowOpen || !World)
	{
		return;
	}

	const FVector Start = LastSocketLocation;
	const FVector End = GetSocketLocation();
	LastSocketLocation = End;

	FCollisionQueryParams Params(SCENE_QUERY_STAT(JDHitWindow), false, GetOwner());
	TArray<FHitResult> Hits;
	World->SweepMultiByObjectType(Hits, Start, End, FQuat::Identity, FCollisionObjectQueryParams(ECC_Pawn),
		FCollisionShape::MakeSphere(HitRadius), Params);

	if (CVarDebugHitbox.GetValueOnGameThread())
	{
		DrawDebugCapsule(World, (Start + End) * 0.5f, (End - Start).Size() * 0.5f + HitRadius, HitRadius,
			FRotationMatrix::MakeFromZ(End - Start).ToQuat(), FColor::Green, false, 0.5f);
	}

	for (const FHitResult& Hit : Hits)
	{
		ProcessHit(Hit);
	}
}

void UJDCombatComponent::EndHitWindow()
{
	bHitWindowOpen = false;
}

void UJDCombatComponent::ProcessHit(const FHitResult& Hit)
{
	AActor* Owner = GetOwner();
	AActor* Victim = Hit.GetActor();
	if (!Victim || Victim == Owner || HitActors.Contains(Victim))
	{
		return;
	}

	UAbilitySystemComponent* SourceASC = UAbilitySystemGlobals::GetAbilitySystemComponentFromActor(Owner);
	UAbilitySystemComponent* TargetASC = UAbilitySystemGlobals::GetAbilitySystemComponentFromActor(Victim);
	if (!SourceASC || !TargetASC)
	{
		return;
	}
	HitActors.Add(Victim);

	const FVector HitLocation = Hit.bStartPenetrating ? FVector(Hit.TraceEnd) : FVector(Hit.ImpactPoint);

	// Damage lewat GE (jalur yang sama untuk semua sumber), dengan hit result di context untuk cue & reaksi.
	FGameplayEffectSpecHandle Spec = UJDGE_Damage::MakeSpec(SourceASC, CurrentAttack.Damage, CurrentAttack.PoiseDamage);
	if (Spec.IsValid())
	{
		Spec.Data->GetContext().AddHitResult(Hit, true);
		SourceASC->ApplyGameplayEffectSpecToTarget(*Spec.Data.Get(), TargetASC);
	}

	// Event untuk reaksi kena (UJDGA_HitReact, Iterasi 4).
	FGameplayEventData Payload;
	Payload.EventTag = JDGameplayTags::Event_Hit;
	Payload.Instigator = Owner;
	Payload.Target = Victim;
	Payload.EventMagnitude = CurrentAttack.Damage;
	Payload.ContextHandle = Spec.IsValid() ? Spec.Data->GetContext() : FGameplayEffectContextHandle();
	UAbilitySystemBlueprintLibrary::SendGameplayEventToActor(Victim, JDGameplayTags::Event_Hit, Payload);

	if (CurrentAttack.HitCue.IsValid())
	{
		FGameplayCueParameters Cue;
		Cue.Location = HitLocation;
		Cue.Normal = Hit.ImpactNormal;
		Cue.Instigator = Owner;
		Cue.EffectCauser = Owner;
		Cue.RawMagnitude = CurrentAttack.Damage;
		TargetASC->ExecuteGameplayCue(CurrentAttack.HitCue, Cue);
	}

	StartHitStop(Victim);

	if (CombatProfile && CombatProfile->HitCameraShake)
	{
		const APawn* OwnerPawn = Cast<APawn>(Owner);
		if (APlayerController* PC = OwnerPawn ? Cast<APlayerController>(OwnerPawn->GetController()) : nullptr)
		{
			PC->ClientStartCameraShake(CombatProfile->HitCameraShake, CombatProfile->HitCameraShakeScale);
		}
	}

	if (CVarDebugHitbox.GetValueOnGameThread())
	{
		DrawDebugSphere(GetWorld(), HitLocation, HitRadius, 12, FColor::Red, false, 1.0f);
	}

	OnHitLanded.Broadcast(Victim, Hit, CurrentAttack);
}

void UJDCombatComponent::StartHitStop(AActor* Victim)
{
	UWorld* World = GetWorld();
	if (!CombatProfile || CombatProfile->HitStopDuration <= 0.0f || !World)
	{
		return;
	}

	EndHitStop();
	HitStopActors = { GetOwner(), Victim };
	for (const TWeakObjectPtr<AActor>& Actor : HitStopActors)
	{
		if (Actor.IsValid())
		{
			Actor->CustomTimeDilation = CombatProfile->HitStopTimeDilation;
		}
	}
	// Timer berjalan dengan waktu dunia, tidak ikut melambat oleh CustomTimeDilation aktor.
	World->GetTimerManager().SetTimer(HitStopTimer, this, &UJDCombatComponent::EndHitStop, CombatProfile->HitStopDuration, false);
}

void UJDCombatComponent::EndHitStop()
{
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(HitStopTimer);
	}
	for (const TWeakObjectPtr<AActor>& Actor : HitStopActors)
	{
		if (Actor.IsValid())
		{
			Actor->CustomTimeDilation = 1.0f;
		}
	}
	HitStopActors.Reset();
}
