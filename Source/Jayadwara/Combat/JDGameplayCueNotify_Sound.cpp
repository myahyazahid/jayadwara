#include "Combat/JDGameplayCueNotify_Sound.h"

#include "GameFramework/Actor.h"
#include "Kismet/GameplayStatics.h"
#include "NiagaraFunctionLibrary.h"
#include "Sound/SoundBase.h"

bool UJDGameplayCueNotify_Sound::OnExecute_Implementation(AActor* MyTarget, const FGameplayCueParameters& Parameters) const
{
	if (!MyTarget)
	{
		return false;
	}

	const FVector Location = Parameters.Location.IsNearlyZero() ? MyTarget->GetActorLocation() : FVector(Parameters.Location);
	bool bPlayed = false;

	if (USoundBase* Sound = Sounds.IsEmpty() ? nullptr : Sounds[FMath::RandRange(0, Sounds.Num() - 1)])
	{
		const float Pitch = FMath::FRandRange(PitchRange.X, PitchRange.Y);
		UGameplayStatics::PlaySoundAtLocation(MyTarget, Sound, Location, VolumeMultiplier, Pitch);
		bPlayed = true;
	}

	if (Effect)
	{
		const FVector Normal = FVector(Parameters.Normal).IsNearlyZero() ? FVector::UpVector : FVector(Parameters.Normal);
		UNiagaraFunctionLibrary::SpawnSystemAtLocation(MyTarget, Effect, Location, Normal.Rotation(), FVector(EffectScale));
		bPlayed = true;
	}
	return bPlayed;
}
