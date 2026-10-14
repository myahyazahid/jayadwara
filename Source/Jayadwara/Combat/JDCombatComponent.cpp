#include "Combat/JDCombatComponent.h"

#include "AbilitySystemBlueprintLibrary.h"
#include "AbilitySystemComponent.h"
#include "AbilitySystemGlobals.h"
#include "Abilities/JDAttributeSet.h"
#include "Abilities/JDGameplayEffects.h"
#include "Abilities/JDGameplayTags.h"
#include "Animation/AnimInstance.h"
#include "Camera/CameraShakeBase.h"
#include "Components/SkeletalMeshComponent.h"
#include "DrawDebugHelpers.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "HAL/IConsoleManager.h"
#include "Jayadwara.h"
#include "TimerManager.h"

static TAutoConsoleVariable<bool> CVarDebugHitbox(
	TEXT("JD.Debug.Hitbox"), false,
	TEXT("1 = gambar sweep hitbox (hijau) dan titik kena (merah) selama JD Hit Window."));

static TAutoConsoleVariable<bool> CVarDebugCombat(
	TEXT("JD.Debug.Combat"), true,
	TEXT("1 = tulis hasil serangan yang melibatkan pemain di layar (PARRY, tangkis, guard break, dodge, kena)."));

namespace
{
	bool IsPlayerActor(const AActor* Actor)
	{
		const APawn* Pawn = Cast<APawn>(Actor);
		return Pawn && Pawn->IsPlayerControlled();
	}

	/** Laju montage yang terlihat 1,0 pada mesh mana pun (raksasa: GlobalAnimRateScale dikompensasi). */
	float CompensatedRate(const USkeletalMeshComponent* Mesh)
	{
		return 1.0f / FMath::Max(Mesh ? Mesh->GlobalAnimRateScale : 1.0f, 0.01f);
	}
}

UJDCombatComponent::UJDCombatComponent()
{
	// Hitbox digerakkan tick notify montage, bukan tick komponen.
	PrimaryComponentTick.bCanEverTick = false;
}

void UJDCombatComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	EndHitStop();
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(StaggerTimer);
	}
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
	bHitWindowDone = false;
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
	// Radius ikut skala aktor (dummy raksasa = BP_TrainingDummy berskala); Jayadwara berskala 1 dengan radius di profil.
	HitRadius = (RadiusOverride > 0.0f ? RadiusOverride : (CombatProfile ? CombatProfile->HitRadius : 30.0f)) * GetOwner()->GetActorScale3D().X;
	LastSocketLocation = GetSocketLocation();
	UE_LOG(LogJayadwara, Verbose, TEXT("%s: hit window %s buka di %s (radius %.0f)"), *GetNameSafe(GetOwner()), *HitSocket.ToString(),
		*LastSocketLocation.ToCompactString(), HitRadius);
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
		if (!bHitWindowOpen)
		{
			break;      // serangan di-parry di tengah sapuan
		}
		ProcessHit(Hit);
	}
}

void UJDCombatComponent::EndHitWindow()
{
	if (bHitWindowOpen)
	{
		UE_LOG(LogJayadwara, Verbose, TEXT("%s: hit window tutup di %s"), *GetNameSafe(GetOwner()), *GetSocketLocation().ToCompactString());
		bHitWindowDone = true;
	}
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

	UJDCombatComponent* VictimCombat = Victim->FindComponentByClass<UJDCombatComponent>();
	const UJDCombatProfile* VictimProfile = VictimCombat ? VictimCombat->GetCombatProfile() : nullptr;
	const EJDHitOutcome Outcome = VictimCombat ? VictimCombat->ResolveIncomingHit(Owner) : EJDHitOutcome::Hit;
	const bool bPlayerInvolved = IsPlayerActor(Owner) || IsPlayerActor(Victim);
	UE_LOG(LogJayadwara, Log, TEXT("Hit %s -> %s: %s (damage %.1f)"), *GetNameSafe(Owner), *GetNameSafe(Victim),
		*UEnum::GetDisplayValueAsText(Outcome).ToString(), CurrentAttack.Damage);
	const FVector HitLocation = Hit.bStartPenetrating ? FVector(Hit.TraceEnd) : FVector(Hit.ImpactPoint);

	auto ExecuteCue = [&](const FGameplayTag& CueTag)
	{
		if (CueTag.IsValid())
		{
			FGameplayCueParameters Cue;
			Cue.Location = HitLocation;
			Cue.Normal = Hit.ImpactNormal;
			Cue.Instigator = Owner;
			Cue.EffectCauser = Owner;
			Cue.RawMagnitude = CurrentAttack.Damage;
			TargetASC->ExecuteGameplayCue(CueTag, Cue);
		}
	};
	auto SendEvent = [&](AActor* Receiver, const FGameplayTag& EventTag, const FGameplayEffectContextHandle& Context)
	{
		FGameplayEventData Payload;
		Payload.EventTag = EventTag;
		Payload.Instigator = Owner;
		Payload.Target = Victim;
		Payload.EventMagnitude = CurrentAttack.Damage;
		Payload.ContextHandle = Context;
		UAbilitySystemBlueprintLibrary::SendGameplayEventToActor(Receiver, EventTag, Payload);
	};

	if (Outcome == EJDHitOutcome::Dodged)
	{
		if (bPlayerInvolved)
		{
			ShowDebugMessage(TEXT("Menghindar"), FColor::Cyan);
		}
		return;
	}

	if (Outcome == EJDHitOutcome::Parried)
	{
		ExecuteCue(JDGameplayTags::GameplayCue_Parry);
		SendEvent(Victim, JDGameplayTags::Event_Hit_Parried, FGameplayEffectContextHandle());
		SendEvent(Owner, JDGameplayTags::Event_Hit_Parried, FGameplayEffectContextHandle());
		StartHitStop(Victim, 2.0f);
		EndHitWindow();
		// Stagger penyerang di frame berikutnya: membatalkan ability & montage di tengah tick notify tidak aman.
		const float StaggerTime = VictimProfile ? VictimProfile->ParryStaggerDuration : 1.0f;
		GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this, [this, StaggerTime]()
		{
			ApplyStagger(StaggerTime);
		}));
		if (bPlayerInvolved)
		{
			ShowDebugMessage(TEXT("PARRY!"), FColor::Yellow);
		}
		return;
	}

	float Damage = CurrentAttack.Damage;
	float PoiseDamage = CurrentAttack.PoiseDamage;
	const bool bBlocked = Outcome == EJDHitOutcome::Blocked || Outcome == EJDHitOutcome::GuardBreak;
	if (bBlocked && VictimProfile)
	{
		Damage *= 1.0f - VictimProfile->BlockDamageReduction;
		PoiseDamage *= 1.0f - VictimProfile->BlockDamageReduction;
	}

	// Damage lewat GE (jalur yang sama untuk semua sumber), dengan hit result di context untuk cue & reaksi.
	FGameplayEffectSpecHandle Spec = UJDGE_Damage::MakeSpec(SourceASC, Damage, PoiseDamage);
	if (Spec.IsValid())
	{
		Spec.Data->GetContext().AddHitResult(Hit, true);
		SourceASC->ApplyGameplayEffectSpecToTarget(*Spec.Data.Get(), TargetASC);
	}
	const FGameplayEffectContextHandle Context = Spec.IsValid() ? Spec.Data->GetContext() : FGameplayEffectContextHandle();

	if (bBlocked)
	{
		ExecuteCue(JDGameplayTags::GameplayCue_Hit_Blocked);
		SendEvent(Victim, JDGameplayTags::Event_Hit_Blocked, Context);
		ACharacter* VictimCharacter = Cast<ACharacter>(Victim);
		if (VictimCharacter && VictimProfile && VictimProfile->BlockPushback > 0.0f)
		{
			const FVector Away = (Victim->GetActorLocation() - Owner->GetActorLocation()).GetSafeNormal2D();
			VictimCharacter->LaunchCharacter(Away * VictimProfile->BlockPushback, true, false);
		}
		if (Outcome == EJDHitOutcome::GuardBreak && VictimCombat)
		{
			const float StaggerTime = VictimProfile ? VictimProfile->GuardBreakStaggerDuration : 1.0f;
			GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(VictimCombat, [VictimCombat, StaggerTime]()
			{
				VictimCombat->ApplyStagger(StaggerTime);
			}));
		}
		if (bPlayerInvolved)
		{
			const bool bBreak = Outcome == EJDHitOutcome::GuardBreak;
			ShowDebugMessage(bBreak ? FString(TEXT("GUARD BREAK")) : FString::Printf(TEXT("Ditangkis (-%.0f)"), Damage),
				bBreak ? FColor::Red : FColor::Silver);
		}
	}
	else
	{
		// Event untuk reaksi kena (UJDGA_HitReact, Iterasi 4).
		SendEvent(Victim, JDGameplayTags::Event_Hit, Context);
		ExecuteCue(CurrentAttack.HitCue);
		if (IsPlayerActor(Victim))
		{
			ShowDebugMessage(FString::Printf(TEXT("Kena -%.0f"), Damage), FColor::Orange);
		}
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

EJDHitOutcome UJDCombatComponent::ResolveIncomingHit(const AActor* Attacker)
{
	UAbilitySystemComponent* ASC = UAbilitySystemGlobals::GetAbilitySystemComponentFromActor(GetOwner());
	if (!ASC)
	{
		return EJDHitOutcome::Hit;
	}
	if (ASC->HasMatchingGameplayTag(JDGameplayTags::State_Invulnerable))
	{
		return EJDHitOutcome::Dodged;
	}

	const bool bParry = ASC->HasMatchingGameplayTag(JDGameplayTags::State_ParryWindow);
	const bool bBlock = ASC->HasMatchingGameplayTag(JDGameplayTags::State_Blocking);
	if (!bParry && !bBlock)
	{
		return EJDHitOutcome::Hit;
	}

	// Tangkis & parry hanya untuk serangan dari depan.
	const float HalfAngle = FMath::DegreesToRadians((CombatProfile ? CombatProfile->BlockAngle : 140.0f) * 0.5f);
	const FVector ToAttacker = Attacker ? (Attacker->GetActorLocation() - GetOwner()->GetActorLocation()).GetSafeNormal2D() : FVector::ZeroVector;
	if (FVector::DotProduct(ToAttacker, GetOwner()->GetActorForwardVector().GetSafeNormal2D()) < FMath::Cos(HalfAngle))
	{
		return EJDHitOutcome::Hit;
	}
	if (bParry)
	{
		return EJDHitOutcome::Parried;
	}

	const float Cost = CombatProfile ? CombatProfile->BlockStaminaPerHit : 15.0f;
	ASC->ApplyModToAttribute(UJDAttributeSet::GetStaminaAttribute(), EGameplayModOp::Additive, -Cost);
	return ASC->GetNumericAttribute(UJDAttributeSet::GetStaminaAttribute()) <= 0.0f ? EJDHitOutcome::GuardBreak : EJDHitOutcome::Blocked;
}

void UJDCombatComponent::ApplyStagger(float Duration)
{
	UWorld* World = GetWorld();
	UAbilitySystemComponent* ASC = UAbilitySystemGlobals::GetAbilitySystemComponentFromActor(GetOwner());
	if (!World || !ASC || Duration <= 0.0f)
	{
		return;
	}

	const FGameplayTag CombatAbilities[] = { JDGameplayTags::Ability_Attack_Light, JDGameplayTags::Ability_Attack_Heavy,
		JDGameplayTags::Ability_Dodge, JDGameplayTags::Ability_Block };
	for (const FGameplayTag& Tag : CombatAbilities)
	{
		const FGameplayTagContainer WithTag(Tag);
		ASC->CancelAbilities(&WithTag);
	}
	EndAttack();

	ASC->SetLooseGameplayTagCount(JDGameplayTags::State_Stagger, 1);
	World->GetTimerManager().SetTimer(StaggerTimer, this, &UJDCombatComponent::EndStagger, Duration, false);

	if (ACharacter* Character = Cast<ACharacter>(GetOwner()))
	{
		Character->GetCharacterMovement()->StopMovementImmediately();
	}
	USkeletalMeshComponent* Mesh = GetOwnerMesh();
	UAnimInstance* Anim = Mesh ? Mesh->GetAnimInstance() : nullptr;
	if (Anim && CombatProfile && CombatProfile->StaggerMontage)
	{
		Anim->Montage_Play(CombatProfile->StaggerMontage, CompensatedRate(Mesh));
	}
}

bool UJDCombatComponent::IsStaggered() const
{
	const UAbilitySystemComponent* ASC = UAbilitySystemGlobals::GetAbilitySystemComponentFromActor(GetOwner());
	return ASC && ASC->HasMatchingGameplayTag(JDGameplayTags::State_Stagger);
}

void UJDCombatComponent::EndStagger()
{
	if (UAbilitySystemComponent* ASC = UAbilitySystemGlobals::GetAbilitySystemComponentFromActor(GetOwner()))
	{
		ASC->SetLooseGameplayTagCount(JDGameplayTags::State_Stagger, 0);
	}
	USkeletalMeshComponent* Mesh = GetOwnerMesh();
	UAnimInstance* Anim = Mesh ? Mesh->GetAnimInstance() : nullptr;
	if (Anim && CombatProfile && CombatProfile->StaggerMontage)
	{
		Anim->Montage_Stop(0.2f, CombatProfile->StaggerMontage);
	}
}

void UJDCombatComponent::ShowDebugMessage(const FString& Message, const FColor& Color) const
{
#if !UE_BUILD_SHIPPING
	if (CVarDebugCombat.GetValueOnGameThread() && GEngine)
	{
		GEngine->AddOnScreenDebugMessage(INDEX_NONE, 1.5f, Color, Message, true, FVector2D(1.6f, 1.6f));
	}
#endif
}

void UJDCombatComponent::StartHitStop(AActor* Victim, float DurationScale)
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
	World->GetTimerManager().SetTimer(HitStopTimer, this, &UJDCombatComponent::EndHitStop, CombatProfile->HitStopDuration * DurationScale, false);
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
