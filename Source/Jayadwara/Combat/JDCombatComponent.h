#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Combat/JDCombatProfile.h"
#include "JDCombatComponent.generated.h"

class UJDCombatProfile;

/** Pukulan kena: korban, titik kena, langkah serangan. */
DECLARE_MULTICAST_DELEGATE_ThreeParams(FJDHitLandedEvent, AActor* /*Victim*/, const FHitResult& /*Hit*/, const FJDAttackStep& /*Attack*/);

/**
 * Hit detection & rasa pukulan (docs/12 "Combat", docs/23 Iterasi 2). Dipasang di AJDCharacterBase.
 *
 * Alur: ability serangan memanggil BeginAttack (langkah combo aktif, daftar korban dikosongkan) -> notify
 * JD Hit Window di montage memanggil Begin/Update/EndHitWindow -> sphere sweep dari socket antar-frame -> korban
 * ber-ASC yang belum kena di serangan ini menerima UJDGE_Damage, Gameplay Event Event.Hit, Gameplay Cue, hit-stop,
 * dan pemain mendapat camera shake. Satu korban maksimal satu kali per serangan.
 */
UCLASS(ClassGroup = (Jayadwara), meta = (BlueprintSpawnableComponent))
class JAYADWARA_API UJDCombatComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UJDCombatComponent();

	UFUNCTION(BlueprintPure, Category = "Combat")
	const UJDCombatProfile* GetCombatProfile() const { return CombatProfile; }

	/** Mulai satu langkah serangan (dipanggil ability tiap pukulan). */
	void BeginAttack(const FJDAttackStep& Attack);

	/** Serangan selesai/dibatalkan: tutup hitbox. */
	void EndAttack();

	bool IsAttacking() const { return bAttackActive; }

	void BeginHitWindow(FName SocketName, float RadiusOverride);
	void UpdateHitWindow();
	void EndHitWindow();

	FJDHitLandedEvent OnHitLanded;

protected:
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	/** Angka combat skala karakter ini (DA_CombatProfile_*). */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat")
	TObjectPtr<UJDCombatProfile> CombatProfile;

private:
	USkeletalMeshComponent* GetOwnerMesh() const;
	FVector GetSocketLocation() const;
	void ProcessHit(const FHitResult& Hit);
	void StartHitStop(AActor* Victim);
	void EndHitStop();

	FJDAttackStep CurrentAttack;
	bool bAttackActive = false;

	bool bHitWindowOpen = false;
	FName HitSocket;
	float HitRadius = 30.0f;
	FVector LastSocketLocation = FVector::ZeroVector;

	UPROPERTY(Transient)
	TArray<TObjectPtr<AActor>> HitActors;

	TArray<TWeakObjectPtr<AActor>> HitStopActors;
	FTimerHandle HitStopTimer;
};
