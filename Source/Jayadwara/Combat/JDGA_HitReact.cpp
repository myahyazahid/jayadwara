#include "Combat/JDGA_HitReact.h"

#include "AbilitySystemComponent.h"
#include "Abilities/JDAttributeSet.h"
#include "Abilities/JDGameplayTags.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Combat/JDCombatProfile.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "TimerManager.h"

UJDGA_HitReact::UJDGA_HitReact()
{
	FGameplayTagContainer AssetTags;
	AssetTags.AddTag(JDGameplayTags::Ability_HitReact);
	SetAssetTags(AssetTags);

	ActivationBlockedTags.AddTag(JDGameplayTags::State_Dead);
	bRetriggerInstancedAbility = true;

	// Event.HitReact.* naik ke induknya: satu pemicu untuk ketiga jenis reaksi.
	FAbilityTriggerData Trigger;
	Trigger.TriggerTag = JDGameplayTags::Event_HitReact;
	Trigger.TriggerSource = EGameplayAbilityTriggerSource::GameplayEvent;
	AbilityTriggers.Add(Trigger);
}

FGameplayTag UJDGA_HitReact::GetEventTag(EJDHitReaction InReaction)
{
	switch (InReaction)
	{
	case EJDHitReaction::Light: return JDGameplayTags::Event_HitReact_Light;
	case EJDHitReaction::Stagger: return JDGameplayTags::Event_HitReact_Stagger;
	case EJDHitReaction::Knockdown: return JDGameplayTags::Event_HitReact_Knockdown;
	default: return FGameplayTag();
	}
}

EJDHitReaction UJDGA_HitReact::GetReactionFromTag(const FGameplayTag& EventTag)
{
	if (EventTag.MatchesTagExact(JDGameplayTags::Event_HitReact_Knockdown))
	{
		return EJDHitReaction::Knockdown;
	}
	if (EventTag.MatchesTagExact(JDGameplayTags::Event_HitReact_Stagger))
	{
		return EJDHitReaction::Stagger;
	}
	return EJDHitReaction::Light;
}

void UJDGA_HitReact::ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
	const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData)
{
	const UJDCombatProfile* Profile = GetCombatProfile();
	if (!Profile || !CommitAbility(Handle, ActorInfo, ActivationInfo))
	{
		EndAbility(Handle, ActorInfo, ActivationInfo, true, true);
		return;
	}

	Reaction = TriggerEventData ? GetReactionFromTag(TriggerEventData->EventTag) : EJDHitReaction::Light;
	ReactionInstigator = TriggerEventData ? TriggerEventData->Instigator.Get() : nullptr;
	const float DurationOverride = TriggerEventData ? TriggerEventData->EventMagnitude : 0.0f;
	AddedTags.Reset();

	switch (Reaction)
	{
	case EJDHitReaction::Stagger:
		BeginStagger(*Profile, DurationOverride > 0.0f ? DurationOverride : Profile->StaggerDuration);
		break;
	case EJDHitReaction::Knockdown:
		BeginKnockdown(*Profile, DurationOverride > 0.0f ? DurationOverride : Profile->KnockdownDuration);
		break;
	default:
		BeginLight(*Profile);
		break;
	}
}

void UJDGA_HitReact::BeginLight(const UJDCombatProfile& Profile)
{
	const bool bPlayer = IsPlayerAvatar();
	if (!bPlayer && !Profile.bHitReactArmorWhileAttacking)
	{
		InterruptCombat(false);
	}

	const UAbilitySystemComponent* ASC = GetAbilitySystemComponentFromActorInfo();
	const bool bPlayerAttacking = bPlayer && ASC && ASC->HasMatchingGameplayTag(JDGameplayTags::State_Attacking);
	float Duration = Profile.LightReactDuration;
	if (!Profile.HitReactMontages.IsEmpty() && !bPlayerAttacking)
	{
		UAnimMontage* Montage = Profile.HitReactMontages[LightVariant % Profile.HitReactMontages.Num()];
		LightVariant = (LightVariant + 1) % Profile.HitReactMontages.Num();
		if (Montage)
		{
			PlayReactionMontage(Montage);
			Duration = Montage->GetPlayLength();
		}
	}
	GetWorld()->GetTimerManager().SetTimer(PhaseTimer, this, &UJDGA_HitReact::FinishReaction, FMath::Max(Duration, 0.01f), false);
}

void UJDGA_HitReact::BeginStagger(const UJDCombatProfile& Profile, float Duration)
{
	InterruptCombat(true);
	AddStateTag(JDGameplayTags::State_Stagger);
	FaceInstigatorAndPush(Profile.StaggerPushback);
	PlayReactionMontage(Profile.StaggerMontage);
	GetWorld()->GetTimerManager().SetTimer(PhaseTimer, this, &UJDGA_HitReact::FinishReaction, FMath::Max(Duration, 0.01f), false);
}

void UJDGA_HitReact::BeginKnockdown(const UJDCombatProfile& Profile, float Duration)
{
	InterruptCombat(true);
	AddStateTag(JDGameplayTags::State_Knockdown);
	FaceInstigatorAndPush(Profile.KnockdownPushback);
	PlayReactionMontage(Profile.KnockdownMontage ? Profile.KnockdownMontage.Get() : Profile.StaggerMontage.Get());
	GetWorld()->GetTimerManager().SetTimer(PhaseTimer, this, &UJDGA_HitReact::BeginGetUp, FMath::Max(Duration, 0.01f), false);
}

void UJDGA_HitReact::BeginGetUp()
{
	const UJDCombatProfile* Profile = GetCombatProfile();
	if (!IsActive() || !Profile)
	{
		return;
	}
	// Bangun kebal: tidak bisa dipukuli terus di tanah (docs/23 Iterasi 4).
	AddStateTag(JDGameplayTags::State_Invulnerable);
	if (Profile->GetUpMontage)
	{
		PlayReactionMontage(Profile->GetUpMontage);
	}
	GetWorld()->GetTimerManager().SetTimer(PhaseTimer, this, &UJDGA_HitReact::FinishReaction, FMath::Max(Profile->GetUpDuration, 0.01f), false);
}

void UJDGA_HitReact::FinishReaction()
{
	if (IsActive())
	{
		EndAbility(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, true, false);
	}
}

void UJDGA_HitReact::InterruptCombat(bool bAllActions)
{
	if (bAllActions)
	{
		CancelAbilitiesWithAnyTag({ JDGameplayTags::Ability_Attack_Light, JDGameplayTags::Ability_Attack_Heavy,
			JDGameplayTags::Ability_Dodge, JDGameplayTags::Ability_Block });
	}
	else
	{
		CancelAbilitiesWithAnyTag({ JDGameplayTags::Ability_Attack_Light, JDGameplayTags::Ability_Attack_Heavy });
	}
	if (UJDCombatComponent* Combat = GetCombat())
	{
		Combat->EndAttack();
	}
}

void UJDGA_HitReact::FaceInstigatorAndPush(float PushSpeed)
{
	ACharacter* Character = Cast<ACharacter>(GetAvatarActorFromActorInfo());
	if (!Character)
	{
		return;
	}
	Character->GetCharacterMovement()->StopMovementImmediately();
	const AActor* Source = ReactionInstigator.Get();
	if (!Source || Source == Character)
	{
		return;
	}
	const FVector ToSource = (Source->GetActorLocation() - Character->GetActorLocation()).GetSafeNormal2D();
	if (ToSource.IsZero())
	{
		return;
	}
	Character->SetActorRotation(FRotator(0.0f, ToSource.Rotation().Yaw, 0.0f));
	if (PushSpeed > 0.0f)
	{
		// Dummy raksasa = dummy berskala: dorongan ikut skala aktor (seperti radius hit).
		Character->LaunchCharacter(-ToSource * PushSpeed * Character->GetActorScale3D().X, true, false);
	}
}

void UJDGA_HitReact::AddStateTag(const FGameplayTag& Tag)
{
	if (UAbilitySystemComponent* ASC = GetAbilitySystemComponentFromActorInfo())
	{
		ASC->AddLooseGameplayTag(Tag);
		AddedTags.Add(Tag);
	}
}

bool UJDGA_HitReact::IsPlayerAvatar() const
{
	const APawn* Pawn = Cast<APawn>(GetAvatarActorFromActorInfo());
	return Pawn && Pawn->IsPlayerControlled();
}

void UJDGA_HitReact::PlayReactionMontage(UAnimMontage* Montage)
{
	const ACharacter* Character = Cast<ACharacter>(GetAvatarActorFromActorInfo());
	USkeletalMeshComponent* Mesh = Character ? Character->GetMesh() : nullptr;
	UAnimInstance* Anim = Mesh ? Mesh->GetAnimInstance() : nullptr;
	if (!Anim || !Montage)
	{
		return;
	}
	// Laju terlihat 1,0 juga pada mesh raksasa (GlobalAnimRateScale dikompensasi, sama dengan montage serangan).
	if (Anim->Montage_Play(Montage, 1.0f / FMath::Max(Mesh->GlobalAnimRateScale, 0.01f)) > 0.0f)
	{
		PlayingMontage = Montage;
	}
}

void UJDGA_HitReact::StopReactionMontage()
{
	const ACharacter* Character = Cast<ACharacter>(GetAvatarActorFromActorInfo());
	UAnimInstance* Anim = Character && Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr;
	if (Anim && PlayingMontage && Anim->Montage_IsPlaying(PlayingMontage))
	{
		Anim->Montage_Stop(0.2f, PlayingMontage);
	}
	PlayingMontage = nullptr;
}

void UJDGA_HitReact::EndAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
	const FGameplayAbilityActivationInfo ActivationInfo, bool bReplicateEndAbility, bool bWasCancelled)
{
	if (IsActive())
	{
		if (UWorld* World = GetWorld())
		{
			World->GetTimerManager().ClearTimer(PhaseTimer);
		}
		UAbilitySystemComponent* ASC = GetAbilitySystemComponentFromActorInfo();
		if (ASC)
		{
			for (const FGameplayTag& Tag : AddedTags)
			{
				ASC->RemoveLooseGameplayTag(Tag);
			}
		}
		AddedTags.Reset();
		// Diganti reaksi baru (retrigger): montage baru langsung menggantikan, jangan dihentikan di sini.
		if (!bWasCancelled)
		{
			StopReactionMontage();
		}
		PlayingMontage = nullptr;

		const UJDCombatProfile* Profile = GetCombatProfile();
		if (!bWasCancelled && ASC && Profile && Profile->bResetPoiseAfterStagger && Reaction >= EJDHitReaction::Stagger)
		{
			ASC->SetNumericAttributeBase(UJDAttributeSet::GetPoiseAttribute(), ASC->GetNumericAttribute(UJDAttributeSet::GetMaxPoiseAttribute()));
		}
		Reaction = EJDHitReaction::None;
		ReactionInstigator.Reset();
	}
	Super::EndAbility(Handle, ActorInfo, ActivationInfo, bReplicateEndAbility, bWasCancelled);
}
