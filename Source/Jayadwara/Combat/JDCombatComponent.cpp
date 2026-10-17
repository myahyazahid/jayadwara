#include "Combat/JDCombatComponent.h"

#include "AbilitySystemBlueprintLibrary.h"
#include "AbilitySystemComponent.h"
#include "AbilitySystemGlobals.h"
#include "Abilities/JDAttributeSet.h"
#include "Abilities/JDGameplayEffects.h"
#include "Abilities/JDGameplayTags.h"
#include "Combat/JDGA_HitReact.h"
#include "Animation/AnimInstance.h"
#include "Camera/CameraShakeBase.h"
#include "CoreGlobals.h"
#include "Components/SkeletalMeshComponent.h"
#include "DrawDebugHelpers.h"
#include "Engine/Engine.h"
#include "Engine/OverlapResult.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "HAL/IConsoleManager.h"
#include "Jayadwara.h"
#include "Kismet/GameplayStatics.h"
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

void UJDCombatComponent::BeginPlay()
{
	Super::BeginPlay();
	if (ACharacter* Character = Cast<ACharacter>(GetOwner()))
	{
		Character->LandedDelegate.AddDynamic(this, &UJDCombatComponent::HandleLanded);
	}
}

void UJDCombatComponent::HandleLanded(const FHitResult& Hit)
{
	AirAttacksUsed = 0;
	OnLanded.Broadcast();
}

bool UJDCombatComponent::CanAirAttack() const
{
	return AirAttacksUsed < (CombatProfile ? CombatProfile->AirComboMax : 0);
}

void UJDCombatComponent::ApplyAreaHit(const FVector& Center, float Radius)
{
	UWorld* World = GetWorld();
	AActor* Owner = GetOwner();
	if (!World || !Owner || !bAttackActive)
	{
		return;
	}
	TArray<FOverlapResult> Overlaps;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(JDAreaHit), false, Owner);
	World->OverlapMultiByObjectType(Overlaps, Center, FQuat::Identity, FCollisionObjectQueryParams(ECC_Pawn),
		FCollisionShape::MakeSphere(Radius), Params);

	const int32 HitsBefore = HitActors.Num();
	for (const FOverlapResult& Overlap : Overlaps)
	{
		AActor* Victim = Overlap.GetActor();
		if (!Victim)
		{
			continue;
		}
		const FVector Point = Victim->GetActorLocation();
		FHitResult Hit(Victim, Overlap.GetComponent(), Point, (Point - Center).GetSafeNormal());
		Hit.TraceStart = Center;
		Hit.TraceEnd = Point;
		ProcessHit(Hit);
	}
	if (HitActors.Num() == HitsBefore)
	{
		PlayHitCameraShake();
	}
	if (CVarDebugHitbox.GetValueOnGameThread())
	{
		DrawDebugSphere(World, Center, Radius, 24, FColor::Orange, false, 1.0f);
	}
}

void UJDCombatComponent::PlayHitCameraShake() const
{
	const APawn* OwnerPawn = Cast<APawn>(GetOwner());
	APlayerController* PC = OwnerPawn ? Cast<APlayerController>(OwnerPawn->GetController()) : nullptr;
	if (PC && CombatProfile && CombatProfile->HitCameraShake)
	{
		PC->ClientStartCameraShake(CombatProfile->HitCameraShake, CombatProfile->HitCameraShakeScale);
	}
}

void UJDCombatComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	EndHitStop();
	EndParrySlowMo();
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

AActor* UJDCombatComponent::FindNearestTarget(float Radius) const
{
	const APawn* Owner = Cast<APawn>(GetOwner());
	const UWorld* World = GetWorld();
	if (!Owner || !World || Radius <= 0.0f)
	{
		return nullptr;
	}
	const FVector Origin = Owner->GetActorLocation();
	AActor* Best = nullptr;
	float BestDistSq = FMath::Square(Radius);
	for (TActorIterator<APawn> It(World); It; ++It)
	{
		APawn* Other = *It;
		if (!IsValidTarget(Owner, Other))
		{
			continue;
		}
		const float DistSq = FVector::DistSquared2D(Origin, Other->GetActorLocation());
		if (DistSq < BestDistSq)
		{
			BestDistSq = DistSq;
			Best = Other;
		}
	}
	return Best;
}

bool UJDCombatComponent::IsValidTarget(const APawn* Owner, const APawn* Other)
{
	// Pihak lawan = beda status dikendalikan pemain; Aksa yang disembunyikan saat transformasi dilewati.
	if (!Owner || !Other || Other == Owner || Other->IsHidden() || Other->IsPlayerControlled() == Owner->IsPlayerControlled()
		|| !Other->FindComponentByClass<UJDCombatComponent>())
	{
		return false;
	}
	const UAbilitySystemComponent* ASC = UAbilitySystemGlobals::GetAbilitySystemComponentFromActor(Other);
	return ASC && !ASC->HasMatchingGameplayTag(JDGameplayTags::State_Dead);
}

void UJDCombatComponent::SetLightComboStep(int32 Step, bool bWasCancelled)
{
	if (Step == INDEX_NONE && bWasCancelled && LightComboStep != INDEX_NONE)
	{
		CancelledLightComboStep = LightComboStep;
		CancelledLightComboFrame = GFrameCounter;
	}
	LightComboStep = Step;
}

int32 UJDCombatComponent::GetComboStepForFinisher() const
{
	if (LightComboStep != INDEX_NONE)
	{
		return LightComboStep;
	}
	return CancelledLightComboFrame == GFrameCounter ? CancelledLightComboStep : INDEX_NONE;
}

void UJDCombatComponent::BeginHitWindow(FName SocketName, float RadiusOverride, bool bNewHit)
{
	if (!bAttackActive)
	{
		return;
	}
	if (bNewHit)
	{
		HitActors.Reset();
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
		// Hit-stop parry milik penangkis (angka parry milik pihak yang bertahan).
		if (VictimProfile)
		{
			StartHitStop(Victim, VictimProfile->ParryHitStopDuration, VictimProfile->ParryHitStopTimeDilation);
		}
		else if (CombatProfile)
		{
			StartHitStop(Victim, CombatProfile->HitStopDuration * 2.0f, CombatProfile->HitStopTimeDilation);
		}
		EndHitWindow();
		if (VictimCombat)
		{
			VictimCombat->HandleParrySuccess(Owner);
		}
		// Stagger penyerang di frame berikutnya: membatalkan ability & montage di tengah tick notify tidak aman.
		const float StaggerTime = VictimProfile ? VictimProfile->ParryStaggerDuration : 1.0f;
		GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,
			[this, StaggerTime, WeakVictim = TWeakObjectPtr<AActor>(Victim)]()
		{
			ApplyStagger(StaggerTime, WeakVictim.Get());
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
	const float PoiseBefore = TargetASC->GetNumericAttribute(UJDAttributeSet::GetPoiseAttribute());
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
			GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(VictimCombat,
				[VictimCombat, StaggerTime, WeakOwner = TWeakObjectPtr<AActor>(Owner)]()
			{
				VictimCombat->ApplyStagger(StaggerTime, WeakOwner.Get());
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
		SendEvent(Victim, JDGameplayTags::Event_Hit, Context);
		ExecuteCue(CurrentAttack.HitCue);

		// Reaksi dari poise (Iterasi 4). Poise yang sudah 0 (sedang stagger) tidak "habis" lagi.
		const float PoiseAfter = TargetASC->GetNumericAttribute(UJDAttributeSet::GetPoiseAttribute());
		const bool bPoiseBroken = PoiseBefore > 0.0f && PoiseAfter <= 0.0f;
		if (bPoiseBroken)
		{
			SendEvent(Victim, JDGameplayTags::Event_Poise_Broken, Context);
		}
		const EJDHitReaction Reaction = VictimCombat ? VictimCombat->ChooseHitReaction(bPoiseBroken, CurrentAttack.bKnockdown) : EJDHitReaction::None;
		if (Reaction != EJDHitReaction::None)
		{
			// Frame berikutnya: membatalkan ability & montage korban di tengah tick notify penyerang tidak aman.
			GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(VictimCombat,
				[VictimCombat, Reaction, WeakOwner = TWeakObjectPtr<AActor>(Owner)]()
			{
				VictimCombat->ApplyHitReaction(Reaction, WeakOwner.Get());
			}));
		}
		if (bPlayerInvolved && Reaction >= EJDHitReaction::Stagger)
		{
			ShowDebugMessage(Reaction == EJDHitReaction::Knockdown ? FString(TEXT("KNOCKDOWN")) : FString(TEXT("STAGGER")),
				Reaction == EJDHitReaction::Knockdown ? FColor::Red : FColor::Orange);
		}
		else if (IsPlayerActor(Victim))
		{
			ShowDebugMessage(FString::Printf(TEXT("Kena -%.0f"), Damage), FColor::Orange);
		}
	}

	StartHitStop(Victim);

	PlayHitCameraShake();

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

void UJDCombatComponent::HandleParrySuccess(AActor* Attacker)
{
	UWorld* World = GetWorld();
	if (!World || !CombatProfile)
	{
		return;
	}

	CounterTarget = Attacker;
	CounterExpireRealTime = World->GetRealTimeSeconds() + CombatProfile->ParryCounterWindow;

	const APawn* OwnerPawn = Cast<APawn>(GetOwner());
	APlayerController* PC = OwnerPawn ? Cast<APlayerController>(OwnerPawn->GetController()) : nullptr;
	if (PC && CombatProfile->ParryCameraShake)
	{
		PC->ClientStartCameraShake(CombatProfile->ParryCameraShake, CombatProfile->ParryCameraShakeScale);
	}

	// Slow-mo dimulai setelah hit-stop selesai supaya keduanya terbaca terpisah (beku sesaat -> lambat -> normal).
	if (CombatProfile->ParrySlowMoDuration > 0.0f && (IsPlayerActor(GetOwner()) || IsPlayerActor(Attacker)))
	{
		if (CombatProfile->ParryHitStopDuration > 0.0f)
		{
			World->GetTimerManager().SetTimer(ParrySlowMoTimer, this, &UJDCombatComponent::StartParrySlowMo,
				CombatProfile->ParryHitStopDuration, false);
		}
		else
		{
			StartParrySlowMo();
		}
	}

	// Tangkis dibatalkan & tepisan diputar di frame berikutnya: kita masih di dalam tick notify milik penyerang.
	World->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,
		[this, WeakAttacker = TWeakObjectPtr<AActor>(Attacker)]()
	{
		PlayParryDeflect(WeakAttacker);
	}));
}

void UJDCombatComponent::PlayParryDeflect(TWeakObjectPtr<AActor> Attacker)
{
	AActor* Owner = GetOwner();
	UAbilitySystemComponent* ASC = UAbilitySystemGlobals::GetAbilitySystemComponentFromActor(Owner);
	if (!Owner || !ASC || !CombatProfile || IsStaggered())
	{
		return;
	}

	// Tepisan menggantikan pose tangkis; tangkis harus berakhir supaya serangan balik (pukulan ringan) bisa aktif.
	const FGameplayTagContainer BlockTag(JDGameplayTags::Ability_Block);
	ASC->CancelAbilities(&BlockTag);

	if (Attacker.IsValid())
	{
		const FVector ToAttacker = (Attacker->GetActorLocation() - Owner->GetActorLocation()).GetSafeNormal2D();
		if (!ToAttacker.IsZero())
		{
			Owner->SetActorRotation(FRotator(0.0f, ToAttacker.Rotation().Yaw, 0.0f));
		}
	}

	const TArray<TObjectPtr<UAnimMontage>>& Montages = CombatProfile->ParryMontages;
	USkeletalMeshComponent* Mesh = GetOwnerMesh();
	UAnimInstance* Anim = Mesh ? Mesh->GetAnimInstance() : nullptr;
	if (Anim && !Montages.IsEmpty())
	{
		UAnimMontage* Montage = Montages[ParryVariant % Montages.Num()];
		ParryVariant = (ParryVariant + 1) % Montages.Num();
		if (Montage)
		{
			Anim->Montage_Play(Montage, CombatProfile->ParryMontageRate * CompensatedRate(Mesh));
		}
	}
}

AActor* UJDCombatComponent::ConsumeCounterTarget()
{
	const UWorld* World = GetWorld();
	AActor* Target = CounterTarget.Get();
	CounterTarget.Reset();
	if (!World || !Target || World->GetRealTimeSeconds() > CounterExpireRealTime)
	{
		return nullptr;
	}
	const UAbilitySystemComponent* ASC = UAbilitySystemGlobals::GetAbilitySystemComponentFromActor(Target);
	return ASC && !ASC->HasMatchingGameplayTag(JDGameplayTags::State_Dead) ? Target : nullptr;
}

void UJDCombatComponent::StartParrySlowMo()
{
	UWorld* World = GetWorld();
	if (!World || !CombatProfile)
	{
		return;
	}
	const float Dilation = CombatProfile->ParrySlowMoTimeDilation;
	UGameplayStatics::SetGlobalTimeDilation(this, Dilation);
	bParrySlowMoActive = true;
	// Timer dunia ikut melambat oleh global time dilation: durasi nyata = waktu dunia / dilation.
	World->GetTimerManager().SetTimer(ParrySlowMoTimer, this, &UJDCombatComponent::EndParrySlowMo,
		CombatProfile->ParrySlowMoDuration * Dilation, false);
}

void UJDCombatComponent::EndParrySlowMo()
{
	UWorld* World = GetWorld();
	if (World)
	{
		World->GetTimerManager().ClearTimer(ParrySlowMoTimer);
	}
	if (bParrySlowMoActive && World)
	{
		UGameplayStatics::SetGlobalTimeDilation(this, 1.0f);
	}
	bParrySlowMoActive = false;
}

void UJDCombatComponent::ApplyStagger(float Duration, AActor* Instigator)
{
	ApplyHitReaction(EJDHitReaction::Stagger, Instigator, Duration);
}

void UJDCombatComponent::ApplyHitReaction(EJDHitReaction Reaction, AActor* Instigator, float Duration)
{
	AActor* Owner = GetOwner();
	const FGameplayTag EventTag = UJDGA_HitReact::GetEventTag(Reaction);
	if (!Owner || !EventTag.IsValid())
	{
		return;
	}
	FGameplayEventData Payload;
	Payload.EventTag = EventTag;
	Payload.Instigator = Instigator;
	Payload.Target = Owner;
	Payload.EventMagnitude = FMath::Max(Duration, 0.0f);
	UAbilitySystemBlueprintLibrary::SendGameplayEventToActor(Owner, EventTag, Payload);
}

EJDHitReaction UJDCombatComponent::ChooseHitReaction(bool bPoiseBroken, bool bKnockdownAttack) const
{
	const UAbilitySystemComponent* ASC = UAbilitySystemGlobals::GetAbilitySystemComponentFromActor(GetOwner());
	if (!ASC || ASC->HasMatchingGameplayTag(JDGameplayTags::State_Dead) || IsKnockedDown())
	{
		return EJDHitReaction::None;
	}
	if (bPoiseBroken)
	{
		return bKnockdownAttack ? EJDHitReaction::Knockdown : EJDHitReaction::Stagger;
	}
	if (IsStaggered())
	{
		// Serangan bertanda Jatuh ke yang sedang terhuyung = jatuh; pukulan lain tidak mengubah stagger.
		return bKnockdownAttack ? EJDHitReaction::Knockdown : EJDHitReaction::None;
	}
	if (CombatProfile && CombatProfile->bHitReactArmorWhileAttacking && ASC->HasMatchingGameplayTag(JDGameplayTags::State_Attacking))
	{
		return EJDHitReaction::None;
	}
	return EJDHitReaction::Light;
}

bool UJDCombatComponent::IsStaggered() const
{
	const UAbilitySystemComponent* ASC = UAbilitySystemGlobals::GetAbilitySystemComponentFromActor(GetOwner());
	return ASC && ASC->HasMatchingGameplayTag(JDGameplayTags::State_Stagger);
}

bool UJDCombatComponent::IsKnockedDown() const
{
	const UAbilitySystemComponent* ASC = UAbilitySystemGlobals::GetAbilitySystemComponentFromActor(GetOwner());
	return ASC && ASC->HasMatchingGameplayTag(JDGameplayTags::State_Knockdown);
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

void UJDCombatComponent::StartHitStop(AActor* Victim)
{
	if (CombatProfile)
	{
		StartHitStop(Victim, CombatProfile->HitStopDuration, CombatProfile->HitStopTimeDilation);
	}
}

void UJDCombatComponent::StartHitStop(AActor* Victim, float Duration, float TimeDilation)
{
	UWorld* World = GetWorld();
	if (Duration <= 0.0f || !World)
	{
		return;
	}

	EndHitStop();
	HitStopActors = { GetOwner(), Victim };
	for (const TWeakObjectPtr<AActor>& Actor : HitStopActors)
	{
		if (Actor.IsValid())
		{
			Actor->CustomTimeDilation = TimeDilation;
		}
	}
	// Timer berjalan dengan waktu dunia, tidak ikut melambat oleh CustomTimeDilation aktor.
	World->GetTimerManager().SetTimer(HitStopTimer, this, &UJDCombatComponent::EndHitStop, Duration, false);
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
