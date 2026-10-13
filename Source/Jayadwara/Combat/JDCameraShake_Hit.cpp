#include "Combat/JDCameraShake_Hit.h"

#include "Shakes/PerlinNoiseCameraShakePattern.h"

namespace
{
	FPerlinNoiseShaker Shaker(float Amplitude, float Frequency)
	{
		FPerlinNoiseShaker Out;
		Out.Amplitude = Amplitude;
		Out.Frequency = Frequency;
		return Out;
	}
}

UJDCameraShake_Hit::UJDCameraShake_Hit(const FObjectInitializer& ObjectInitializer)
	: Super(ObjectInitializer.SetDefaultSubobjectClass<UPerlinNoiseCameraShakePattern>(TEXT("RootShakePattern")))
{
	bSingleInstance = true;

	if (UPerlinNoiseCameraShakePattern* Pattern = Cast<UPerlinNoiseCameraShakePattern>(GetRootShakePattern()))
	{
		Pattern->Duration = 0.15f;
		Pattern->BlendInTime = 0.02f;
		Pattern->BlendOutTime = 0.08f;

		Pattern->LocationAmplitudeMultiplier = 1.0f;
		Pattern->LocationFrequencyMultiplier = 1.0f;
		Pattern->X = Shaker(1.5f, 40.0f);
		Pattern->Y = Shaker(1.5f, 40.0f);
		Pattern->Z = Shaker(2.0f, 45.0f);

		Pattern->RotationAmplitudeMultiplier = 1.0f;
		Pattern->RotationFrequencyMultiplier = 1.0f;
		Pattern->Pitch = Shaker(0.6f, 35.0f);
		Pattern->Yaw = Shaker(0.4f, 35.0f);
		Pattern->Roll = Shaker(0.5f, 30.0f);
		Pattern->FOV = Shaker(0.0f, 0.0f);
	}
}
