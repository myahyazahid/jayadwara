#include "Combat/JDGameplayCueNotify_Sound.h"

#include "GameFramework/Actor.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"

bool UJDGameplayCueNotify_Sound::OnExecute_Implementation(AActor* MyTarget, const FGameplayCueParameters& Parameters) const
{
	if (Sounds.IsEmpty() || !MyTarget)
	{
		return false;
	}

	USoundBase* Sound = Sounds[FMath::RandRange(0, Sounds.Num() - 1)];
	if (!Sound)
	{
		return false;
	}

	const FVector Location = Parameters.Location.IsNearlyZero() ? MyTarget->GetActorLocation() : FVector(Parameters.Location);
	const float Pitch = FMath::FRandRange(PitchRange.X, PitchRange.Y);
	UGameplayStatics::PlaySoundAtLocation(MyTarget, Sound, Location, VolumeMultiplier, Pitch);
	return true;
}
