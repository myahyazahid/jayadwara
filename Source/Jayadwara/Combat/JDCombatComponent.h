#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Combat/JDCombatProfile.h"
#include "JDCombatComponent.generated.h"

class UJDCombatProfile;

/** Hasil serangan yang mengenai karakter yang bertahan (docs/23 Iterasi 3). */
UENUM(BlueprintType)
enum class EJDHitOutcome : uint8
{
	Hit,
	/** Kena i-frame dodge: tanpa damage. */
	Dodged,
	/** Ditangkis: damage dikurangi, stamina penangkis berkurang. */
	Blocked,
	/** Ditangkis tapi stamina habis: penangkis stagger. */
	GuardBreak,
	/** Parry: tanpa damage, penyerang stagger. */
	Parried
};

/** Pukulan kena: korban, titik kena, langkah serangan. */
DECLARE_MULTICAST_DELEGATE_ThreeParams(FJDHitLandedEvent, AActor* /*Victim*/, const FHitResult& /*Hit*/, const FJDAttackStep& /*Attack*/);

/**
 * Hit detection & rasa pukulan (docs/12 "Combat", docs/23 Iterasi 2). Dipasang di AJDCharacterBase.
 *
 * Alur: ability serangan memanggil BeginAttack (langkah combo aktif, daftar korban dikosongkan) -> notify
 * JD Hit Window di montage memanggil Begin/Update/EndHitWindow -> sphere sweep dari socket antar-frame -> korban
 * ber-ASC yang belum kena di serangan ini menerima UJDGE_Damage, Gameplay Event Event.Hit, Gameplay Cue, hit-stop,
 * dan pemain mendapat camera shake. Satu korban maksimal satu kali per serangan.
 *
 * Bertahan (Iterasi 3): komponen milik korban memutuskan hasilnya (ResolveIncomingHit) dari tag ASC-nya:
 * State.Invulnerable -> Dodged, State.ParryWindow -> Parried (penyerang stagger, penangkis menepis lalu boleh serangan
 * balik: HandleParrySuccess), State.Blocking -> Blocked/GuardBreak.
 * Tangkis & parry hanya berlaku untuk serangan dari depan (BlockAngle). Stagger sementara (ApplyStagger) membatalkan
 * ability combat, memasang State.Stagger, dan menahan gerak; reaksi lengkap (poise, knockdown) di Iterasi 4.
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

	/**
	 * Target terdekat untuk arah combo (docs/07 "Combo & arah"): karakter lain yang terlihat, hidup, beda pihak, dalam
	 * Radius. Sementara sampai UJDTargetingComponent (Iterasi 4).
	 */
	AActor* FindNearestTarget(float Radius) const;

	/** Langkah combo ringan yang sedang jalan (dipanggil UJDGA_LightAttack; INDEX_NONE = combo berakhir). */
	void SetLightComboStep(int32 Step, bool bWasCancelled = false);

	/**
	 * Langkah combo ringan untuk cabang finisher pukulan berat: langkah yang sedang jalan, atau yang baru dipotong di frame
	 * ini (pukulan berat membatalkan combo sebelum ActivateAbility-nya jalan). INDEX_NONE = dari diam.
	 */
	int32 GetComboStepForFinisher() const;

	/** Masih boleh pukulan udara di lompatan ini (UJDCombatProfile::AirComboMax). */
	bool CanAirAttack() const;
	void NoteAirAttack() { ++AirAttacksUsed; }

	/**
	 * Serangan area (hantaman ke bawah): semua karakter ber-ASC dalam Radius dari Center kena CurrentAttack lewat jalur hit
	 * biasa (tangkis/parry/dodge, hit-stop, cue). Shake kamera pemain tetap jalan walau tidak ada yang kena.
	 */
	void ApplyAreaHit(const FVector& Center, float Radius);

	/** Pemilik mendarat (reset hitungan pukulan udara; hantaman ke bawah menunggu ini). */
	FSimpleMulticastDelegate OnLanded;

	/** Serangan berjalan tapi jendela hit sudah lewat: boleh dibatalkan dodge/tangkis (docs/23 bagian 5). */
	bool IsInAttackRecovery() const { return bAttackActive && bHitWindowDone; }

	/** Dipanggil komponen penyerang saat pukulannya mengenai pemilik komponen ini. Mengurangi stamina kalau ditangkis. */
	EJDHitOutcome ResolveIncomingHit(const AActor* Attacker);

	/**
	 * Pemilik komponen ini berhasil parry pukulan Attacker (dipanggil komponen penyerang): tangkis dibatalkan, tepisan
	 * ParryMontages diputar bergantian menghadap penyerang, shake kamera, slow-mo setelah hit-stop (kalau pemain
	 * terlibat), dan jendela serangan balik dibuka (docs/07 "Parry").
	 */
	void HandleParrySuccess(AActor* Attacker);

	/** Penyerang yang baru di-parry kalau jendela serangan balik masih terbuka (sekali pakai), selain itu nullptr. */
	AActor* ConsumeCounterTarget();

	/** Stagger selama Duration detik (dibatalkan ability combat, gerak ditahan, StaggerMontage profil diputar). */
	void ApplyStagger(float Duration);

	bool IsStaggered() const;

	void BeginHitWindow(FName SocketName, float RadiusOverride);
	void UpdateHitWindow();
	void EndHitWindow();

	FJDHitLandedEvent OnHitLanded;

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	/** Angka combat skala karakter ini (DA_CombatProfile_*). */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat")
	TObjectPtr<UJDCombatProfile> CombatProfile;

private:
	UFUNCTION()
	void HandleLanded(const FHitResult& Hit);

	void PlayHitCameraShake() const;
	USkeletalMeshComponent* GetOwnerMesh() const;
	FVector GetSocketLocation() const;
	void ProcessHit(const FHitResult& Hit);
	void StartHitStop(AActor* Victim);
	void StartHitStop(AActor* Victim, float Duration, float TimeDilation);
	void EndHitStop();
	void PlayParryDeflect(TWeakObjectPtr<AActor> Attacker);
	void StartParrySlowMo();
	void EndParrySlowMo();
	void EndStagger();
	void ShowDebugMessage(const FString& Message, const FColor& Color) const;

	FJDAttackStep CurrentAttack;
	bool bAttackActive = false;

	bool bHitWindowOpen = false;
	bool bHitWindowDone = false;
	FName HitSocket;
	float HitRadius = 30.0f;
	FVector LastSocketLocation = FVector::ZeroVector;

	UPROPERTY(Transient)
	TArray<TObjectPtr<AActor>> HitActors;

	TArray<TWeakObjectPtr<AActor>> HitStopActors;
	FTimerHandle HitStopTimer;

	FTimerHandle StaggerTimer;

	int32 ParryVariant = 0;
	TWeakObjectPtr<AActor> CounterTarget;
	double CounterExpireRealTime = 0.0;
	FTimerHandle ParrySlowMoTimer;
	bool bParrySlowMoActive = false;

	int32 LightComboStep = INDEX_NONE;
	int32 CancelledLightComboStep = INDEX_NONE;
	uint64 CancelledLightComboFrame = 0;

	int32 AirAttacksUsed = 0;
};
