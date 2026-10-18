#include "Abilities/JDAbilitySystemComponent.h"

#include "Abilities/JDAttributeSet.h"
#include "Abilities/JDGameplayAbility.h"
#include "Abilities/JDGameplayEffects.h"
#include "Abilities/JDGameplayTags.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "HAL/IConsoleManager.h"
#include "TimerManager.h"

static TAutoConsoleVariable<bool> CVarDebugInput(
	TEXT("JD.Debug.Input"), false,
	TEXT("1 = tampilkan input tag yang ditekan/dilepas di layar (uji pemetaan keyboard-mouse & gamepad)."));

namespace
{
	EJDAbilityActivationPolicy GetPolicy(const FGameplayAbilitySpec& Spec)
	{
		const UJDGameplayAbility* Ability = Cast<UJDGameplayAbility>(Spec.Ability);
		return Ability ? Ability->GetActivationPolicy() : EJDAbilityActivationPolicy::OnInputTriggered;
	}

	void DebugInput(const FGameplayTag& InputTag, bool bPressed, int32 NumAbilities)
	{
		if (CVarDebugInput.GetValueOnGameThread() && GEngine)
		{
			GEngine->AddOnScreenDebugMessage(INDEX_NONE, 2.0f, bPressed ? FColor::Cyan : FColor::Silver,
				FString::Printf(TEXT("%s %s (%d ability)"), *InputTag.ToString(), bPressed ? TEXT("ditekan") : TEXT("dilepas"), NumAbilities));
		}
	}
}

UJDAbilitySystemComponent::UJDAbilitySystemComponent()
{
	// Single-player: tidak perlu replikasi GE ke proxy.
	SetIsReplicatedByDefault(false);
}

void UJDAbilitySystemComponent::FindSpecsWithInputTag(const FGameplayTag& InputTag, TArray<FGameplayAbilitySpecHandle>& OutHandles) const
{
	for (const FGameplayAbilitySpec& Spec : ActivatableAbilities.Items)
	{
		if (Spec.Ability && Spec.GetDynamicSpecSourceTags().HasTagExact(InputTag))
		{
			OutHandles.Add(Spec.Handle);
		}
	}
}

void UJDAbilitySystemComponent::AbilityInputTagPressed(const FGameplayTag& InputTag)
{
	if (!InputTag.IsValid())
	{
		return;
	}

	TArray<FGameplayAbilitySpecHandle> Handles;
	FindSpecsWithInputTag(InputTag, Handles);
	DebugInput(InputTag, true, Handles.Num());

	for (const FGameplayAbilitySpecHandle& Handle : Handles)
	{
		InputPressedSpecHandles.AddUnique(Handle);
		InputHeldSpecHandles.AddUnique(Handle);
	}
}

void UJDAbilitySystemComponent::AbilityInputTagReleased(const FGameplayTag& InputTag)
{
	if (!InputTag.IsValid())
	{
		return;
	}

	TArray<FGameplayAbilitySpecHandle> Handles;
	FindSpecsWithInputTag(InputTag, Handles);
	DebugInput(InputTag, false, Handles.Num());

	for (const FGameplayAbilitySpecHandle& Handle : Handles)
	{
		InputReleasedSpecHandles.AddUnique(Handle);
		InputHeldSpecHandles.Remove(Handle);
	}
}

void UJDAbilitySystemComponent::ProcessAbilityInput(float DeltaTime, bool bGamePaused)
{
	const UWorld* World = GetWorld();
	const double Now = World ? World->GetTimeSeconds() : 0.0;

	// Buffer lama: coba lagi sampai berhasil atau kedaluwarsa; tekanan baru menggantikannya.
	if (BufferedSpecHandle.IsValid())
	{
		if (!InputPressedSpecHandles.IsEmpty() || Now - BufferedAtTime > InputBufferTime)
		{
			BufferedSpecHandle = FGameplayAbilitySpecHandle();
		}
		else if (const FGameplayAbilitySpec* Spec = FindAbilitySpecFromHandle(BufferedSpecHandle))
		{
			if (Spec->IsActive() || TryActivateAbility(BufferedSpecHandle))
			{
				BufferedSpecHandle = FGameplayAbilitySpecHandle();
			}
		}
		else
		{
			BufferedSpecHandle = FGameplayAbilitySpecHandle();
		}
	}

	TArray<FGameplayAbilitySpecHandle, TInlineAllocator<8>> ToActivate;

	// Ditahan: ability WhileInputActive yang belum aktif.
	for (const FGameplayAbilitySpecHandle& Handle : InputHeldSpecHandles)
	{
		const FGameplayAbilitySpec* Spec = FindAbilitySpecFromHandle(Handle);
		if (Spec && Spec->Ability && !Spec->IsActive() && GetPolicy(*Spec) == EJDAbilityActivationPolicy::WhileInputActive)
		{
			ToActivate.AddUnique(Handle);
		}
	}

	// Ditekan frame ini: yang sudah aktif menerima event InputPressed (lanjut combo), yang belum aktif dicoba.
	for (const FGameplayAbilitySpecHandle& Handle : InputPressedSpecHandles)
	{
		FGameplayAbilitySpec* Spec = FindAbilitySpecFromHandle(Handle);
		if (!Spec || !Spec->Ability)
		{
			continue;
		}
		Spec->InputPressed = true;
		if (Spec->IsActive())
		{
			AbilitySpecInputPressed(*Spec);
		}
		else if (GetPolicy(*Spec) != EJDAbilityActivationPolicy::OnSpawn)
		{
			// WhileInputActive juga: tekan & lepas di frame yang sama (FPS rendah) tetap mengaktifkan, mis. parry sekali tekan.
			ToActivate.AddUnique(Handle);
		}
	}

	for (const FGameplayAbilitySpecHandle& Handle : ToActivate)
	{
		const bool bActivated = TryActivateAbility(Handle);
		if (!bActivated && InputPressedSpecHandles.Contains(Handle))
		{
			const FGameplayAbilitySpec* Spec = FindAbilitySpecFromHandle(Handle);
			if (Spec && GetPolicy(*Spec) == EJDAbilityActivationPolicy::OnInputTriggered && InputBufferTime > 0.0f)
			{
				BufferedSpecHandle = Handle;
				BufferedAtTime = Now;
			}
		}
	}

	for (const FGameplayAbilitySpecHandle& Handle : InputReleasedSpecHandles)
	{
		FGameplayAbilitySpec* Spec = FindAbilitySpecFromHandle(Handle);
		if (!Spec || !Spec->Ability)
		{
			continue;
		}
		Spec->InputPressed = false;
		if (Spec->IsActive())
		{
			AbilitySpecInputReleased(*Spec);
		}
	}

	InputPressedSpecHandles.Reset();
	InputReleasedSpecHandles.Reset();
}

void UJDAbilitySystemComponent::ClearAbilityInput()
{
	InputPressedSpecHandles.Reset();
	InputReleasedSpecHandles.Reset();
	InputHeldSpecHandles.Reset();
	BufferedSpecHandle = FGameplayAbilitySpecHandle();
}

void UJDAbilitySystemComponent::AbilitySpecInputPressed(FGameplayAbilitySpec& Spec)
{
	Super::AbilitySpecInputPressed(Spec);

	// Event InputPressed untuk ability task WaitInputPress (lanjut combo, parry). Engine hanya mengirimnya lewat jalur
	// InputID lama; jalur input tag harus mengirim sendiri.
	if (Spec.IsActive())
	{
		const UGameplayAbility* Instance = Spec.GetPrimaryInstance();
		const FPredictionKey Key = Instance ? Instance->GetCurrentActivationInfo().GetActivationPredictionKey() : FPredictionKey();
		InvokeReplicatedEvent(EAbilityGenericReplicatedEvent::InputPressed, Spec.Handle, Key);
	}
}

void UJDAbilitySystemComponent::AbilitySpecInputReleased(FGameplayAbilitySpec& Spec)
{
	Super::AbilitySpecInputReleased(Spec);

	// Untuk WaitInputRelease (lepas tangkis).
	if (Spec.IsActive())
	{
		const UGameplayAbility* Instance = Spec.GetPrimaryInstance();
		const FPredictionKey Key = Instance ? Instance->GetCurrentActivationInfo().GetActivationPredictionKey() : FPredictionKey();
		InvokeReplicatedEvent(EAbilityGenericReplicatedEvent::InputReleased, Spec.Handle, Key);
	}
}

// ------------------------------------------------------------------ regen stamina & poise

void UJDAbilitySystemComponent::ConfigureStaminaRegen(float PerSecond, float Delay)
{
	FJDAttributeRegen& Regen = Regens[JDRegen::Stamina];
	Regen.Attribute = UJDAttributeSet::GetStaminaAttribute();
	Regen.Effect = UJDGE_StaminaRegen::StaticClass();
	Regen.DataTag = JDGameplayTags::Data_StaminaRegen;
	Regen.TickPeriod = UJDGE_StaminaRegen::TickPeriod;
	ConfigureRegen(JDRegen::Stamina, PerSecond, Delay);
}

void UJDAbilitySystemComponent::ConfigurePoiseRegen(float PerSecond, float Delay)
{
	FJDAttributeRegen& Regen = Regens[JDRegen::Poise];
	Regen.Attribute = UJDAttributeSet::GetPoiseAttribute();
	Regen.Effect = UJDGE_PoiseRegen::StaticClass();
	Regen.DataTag = JDGameplayTags::Data_PoiseRegen;
	Regen.TickPeriod = UJDGE_PoiseRegen::TickPeriod;
	ConfigureRegen(JDRegen::Poise, PerSecond, Delay);
}

void UJDAbilitySystemComponent::ConfigureRegen(int32 Index, float PerSecond, float Delay)
{
	FJDAttributeRegen& Regen = Regens[Index];
	Regen.PerSecond = FMath::Max(PerSecond, 0.0f);
	Regen.Delay = FMath::Max(Delay, 0.0f);

	if (!Regen.ChangedHandle.IsValid())
	{
		Regen.ChangedHandle = GetGameplayAttributeValueChangeDelegate(Regen.Attribute)
			.AddUObject(this, &UJDAbilitySystemComponent::OnRegenAttributeChanged, Index);
	}

	StopRegen(Index);
	StartRegen(Index);
}

void UJDAbilitySystemComponent::OnRegenAttributeChanged(const FOnAttributeChangeData& Data, int32 Index)
{
	FJDAttributeRegen& Regen = Regens[Index];
	if (Data.NewValue >= Data.OldValue || Regen.PerSecond <= 0.0f)
	{
		return;
	}

	// Atribut terpakai / kena: regen berhenti, mulai lagi setelah jeda (dihitung ulang tiap pemakaian).
	StopRegen(Index);
	if (UWorld* World = GetWorld())
	{
		if (Regen.Delay > 0.0f)
		{
			World->GetTimerManager().SetTimer(Regen.DelayTimer,
				FTimerDelegate::CreateUObject(this, &UJDAbilitySystemComponent::StartRegen, Index), Regen.Delay, false);
		}
		else
		{
			StartRegen(Index);
		}
	}
}

void UJDAbilitySystemComponent::StartRegen(int32 Index)
{
	FJDAttributeRegen& Regen = Regens[Index];
	if (Regen.PerSecond <= 0.0f || Regen.Handle.IsValid() || !Regen.Effect)
	{
		return;
	}

	FGameplayEffectSpecHandle Spec = MakeOutgoingSpec(Regen.Effect, 1.0f, MakeEffectContext());
	if (Spec.IsValid())
	{
		Spec.Data->SetSetByCallerMagnitude(Regen.DataTag, Regen.PerSecond * Regen.TickPeriod);
		Regen.Handle = ApplyGameplayEffectSpecToSelf(*Spec.Data.Get());
	}
}

void UJDAbilitySystemComponent::StopRegen(int32 Index)
{
	FJDAttributeRegen& Regen = Regens[Index];
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(Regen.DelayTimer);
	}
	if (Regen.Handle.IsValid())
	{
		RemoveActiveGameplayEffect(Regen.Handle);
		Regen.Handle.Invalidate();
	}
}

void UJDAbilitySystemComponent::OnUnregister()
{
	if (UWorld* World = GetWorld())
	{
		for (FJDAttributeRegen& Regen : Regens)
		{
			World->GetTimerManager().ClearTimer(Regen.DelayTimer);
		}
	}
	Super::OnUnregister();
}
