#include "Characters/JDCharacterBase.h"

AJDCharacterBase::AJDCharacterBase()
{
	// Gerak ditangani CharacterMovementComponent (tick sendiri); actor-nya tidak perlu tick.
	PrimaryActorTick.bCanEverTick = false;
}
