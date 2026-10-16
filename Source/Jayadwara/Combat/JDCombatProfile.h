#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "GameplayTagContainer.h"
#include "JDCombatProfile.generated.h"

class UAnimMontage;
class UCameraShakeBase;

/** Satu langkah serangan: montage + besaran damage. */
USTRUCT(BlueprintType)
struct FJDAttackStep
{
	GENERATED_BODY()

	/** Montage berisi notify JD Hit Window (+ JD Combo Window kalau bisa disambung). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack")
	TObjectPtr<UAnimMontage> Montage = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack", meta = (ClampMin = "0"))
	float Damage = 10.0f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack", meta = (ClampMin = "0"))
	float PoiseDamage = 5.0f;

	/** Gameplay Cue saat kena (SFX/VFX). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack", meta = (Categories = "GameplayCue"))
	FGameplayTag HitCue;

	/** Pengali laju montage langkah ini (x MontagePlayRate profil). Mis. pukulan berat placeholder diperlambat. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack", meta = (ClampMin = "0.05"))
	float PlayRate = 1.0f;

	/** Stamina yang dipakai; ability gagal aktif kalau stamina kurang (docs/23 bagian 5: pukulan berat 25). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack", meta = (ClampMin = "0"))
	float StaminaCost = 0.0f;

	/**
	 * Gerak saat langkah dimulai (cm, searah hadap; negatif = mundur), lewat root motion source selama MoveDuration.
	 * 0 = hanya root motion animasi. Dipakai pembuka terjang & mundur (docs/07 "Combo & arah").
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack|Move", meta = (Units = "cm"))
	float MoveDistance = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack|Move", meta = (ClampMin = "0.05", Units = "s"))
	float MoveDuration = 0.2f;

	/** Gerak maju berhenti UJDCombatProfile::LungeStopDistance sebelum target (MoveDistance jadi batas atas). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Attack|Move")
	bool bStopAtTarget = false;
};

/** Montage per arah relatif hadap karakter (dodge 4 arah, Q10). Kosong = tanpa animasi (gerak tetap jalan). */
USTRUCT(BlueprintType)
struct FJDDirectionalMontages
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Montage")
	TObjectPtr<UAnimMontage> Forward = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Montage")
	TObjectPtr<UAnimMontage> Backward = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Montage")
	TObjectPtr<UAnimMontage> Left = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Montage")
	TObjectPtr<UAnimMontage> Right = nullptr;
};

/**
 * Combat per skala (docs/12 "Combat (satu sistem, dua skala)", docs/23 bagian 5). Ability combat sama untuk Aksa dan
 * Jayadwara; yang berbeda hanya isi profil ini: montage, laju montage, radius hitbox, damage, hit-stop, shake.
 * Aset: DA_CombatProfile_Human (Iterasi 2), DA_CombatProfile_Giant (Iterasi 6), DA_CombatProfile_Dummy (Iterasi 3).
 * Angka tangkis/parry/dodge milik pihak yang bertahan; durasi dalam detik nyata (bukan waktu animasi).
 */
UCLASS(BlueprintType, Const)
class JAYADWARA_API UJDCombatProfile : public UDataAsset
{
	GENERATED_BODY()

public:
	/** Combo pukulan ringan, berurutan (docs/07 & docs/23: 4 pukulan, damage 10 / 10 / 12 / 20). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Light Combo", meta = (TitleProperty = "Montage"))
	TArray<FJDAttackStep> LightCombo;

	// ------------------------------------------------------------------ combo & arah (docs/07 "Combo & arah")
	// Arah input dihitung relatif ke target terdekat, bukan ke kamera. Maju/mundur memilih pembuka pengganti langkah 1;
	// kiri/kanan dan tanpa target = combo biasa (kiri/kanan untuk memilih target, Iterasi 4). Combo berlanjut dari langkah 2.

	/** Pembuka maju + pukul saat target lebih jauh dari LungeMinDistance (terjang). Montage kosong = langkah 1 biasa. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Light Combo|Direction")
	FJDAttackStep LungeAttack;

	/** Pembuka mundur + pukul (sapuan / pukulan sambil mundur). Montage kosong = langkah 1 biasa. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Light Combo|Direction")
	FJDAttackStep BackAttack;

	/** Jarak cari target untuk menentukan arah (sementara: target terdekat; UJDTargetingComponent di Iterasi 4). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Light Combo|Direction", meta = (ClampMin = "0", Units = "cm"))
	float TargetSearchRadius = 800.0f;

	/** Target lebih dekat dari ini = maju + pukul jadi langkah 1 biasa (tidak perlu terjang). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Light Combo|Direction", meta = (ClampMin = "0", Units = "cm"))
	float LungeMinDistance = 250.0f;

	/** Terjang berhenti sejauh ini dari target (jarak antar-pusat kapsul). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Light Combo|Direction", meta = (ClampMin = "0", Units = "cm"))
	float LungeStopDistance = 100.0f;

	/** Batas cos sudut input vs arah ke target: >= ini = maju, <= minus ini = mundur (0,5 = kerucut 60 derajat). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Light Combo|Direction", meta = (ClampMin = "0", ClampMax = "1"))
	float DirectionThreshold = 0.5f;

	/** Laju semua montage serangan yang terlihat (manusia 1,0; raksasa 1,0 sejak 16 Okt 2026, dulu ±0,55). GlobalAnimRateScale mesh dikompensasi ability. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Animation", meta = (ClampMin = "0.05"))
	float MontagePlayRate = 1.0f;

	/** Radius sphere trace hitbox (cm) kalau notify tidak menimpa. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Hit", meta = (ClampMin = "1"))
	float HitRadius = 30.0f;

	/** Lama hit-stop (s, waktu dunia): penyerang & korban nyaris berhenti sesaat. 0 = tanpa hit-stop. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Hit|Feel", meta = (ClampMin = "0"))
	float HitStopDuration = 0.06f;

	/** Time dilation lokal selama hit-stop. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Hit|Feel", meta = (ClampMin = "0.001", ClampMax = "1"))
	float HitStopTimeDilation = 0.05f;

	/** Shake kamera pemain saat pukulannya kena (kosong = tanpa shake). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Hit|Feel")
	TSubclassOf<UCameraShakeBase> HitCameraShake;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Hit|Feel", meta = (ClampMin = "0"))
	float HitCameraShakeScale = 1.0f;

	// ------------------------------------------------------------------ serangan udara (docs/07 "Serangan udara")

	/** Pukulan ringan saat melompat/jatuh. Montage kosong = combo darat biasa. Animasi tanpa root motion (gerak dari lompatan). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Air Attack")
	FJDAttackStep AirAttack;

	/** Maksimal pukulan udara per lompatan (reset saat mendarat). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Air Attack", meta = (ClampMin = "1"))
	int32 AirComboMax = 2;

	/** "Ngambang": tiap pukulan udara, kecepatan jatuh dinolkan dan gravitasi dikali AirHangGravityScale selama AirHangTime. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Air Attack", meta = (ClampMin = "0", Units = "s"))
	float AirHangTime = 0.3f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Air Attack", meta = (ClampMin = "0", ClampMax = "1"))
	float AirHangGravityScale = 0.1f;

	/** Pukulan berat saat di udara: menukik ke bawah, gelombang kejut saat mendarat. Montage kosong = pukulan berat biasa. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Air Attack")
	FJDAttackStep AirSlam;

	/** Kecepatan menukik (cm/s). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Air Attack", meta = (ClampMin = "0"))
	float AirSlamSpeed = 2000.0f;

	/** Radius gelombang kejut di titik mendarat (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Air Attack", meta = (ClampMin = "0", Units = "cm"))
	float AirSlamRadius = 250.0f;

	/** Jeda setelah mendarat sebelum bisa bergerak/menyerang lagi. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Air Attack", meta = (ClampMin = "0", Units = "s"))
	float AirSlamRecovery = 0.35f;

	/** Pukulan berat (docs/23 bagian 5: damage 30, poise 40, stamina 25). Bisa memotong combo ringan di jendela combo. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Heavy Attack")
	FJDAttackStep HeavyAttack;

	/**
	 * Cabang finisher: pukulan berat yang memotong combo ringan di langkah ke-i (indeks 0 = setelah pukulan 1). Slot tidak
	 * ada / montage kosong = HeavyAttack. Pukulan berat dari diam selalu HeavyAttack.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Heavy Attack", meta = (TitleProperty = "Montage"))
	TArray<FJDAttackStep> HeavyFinishers;

	/** Pukulan berat setelah langkah combo ringan LightStep (INDEX_NONE = dari diam). */
	const FJDAttackStep& GetHeavyAttack(int32 LightStep) const
	{
		return HeavyFinishers.IsValidIndex(LightStep) && HeavyFinishers[LightStep].Montage ? HeavyFinishers[LightStep] : HeavyAttack;
	}

	// ------------------------------------------------------------------ dodge (Iterasi 3)

	/** Animasi dodge per arah (opsional). Gerak dodge dari root motion source, bukan animasi. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dodge")
	FJDDirectionalMontages DodgeMontages;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dodge", meta = (ClampMin = "0", Units = "cm"))
	float DodgeDistance = 400.0f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dodge", meta = (ClampMin = "0.05", Units = "s"))
	float DodgeDuration = 0.35f;

	/** i-frame: State.Invulnerable dari IFrameStart selama IFrameDuration setelah dodge mulai. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dodge", meta = (ClampMin = "0", Units = "s"))
	float DodgeIFrameStart = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dodge", meta = (ClampMin = "0", Units = "s"))
	float DodgeIFrameDuration = 0.25f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dodge", meta = (ClampMin = "0"))
	float DodgeStaminaCost = 20.0f;

	// ------------------------------------------------------------------ tangkis & parry (Iterasi 3)

	/** Pose tangkis: frame BlockHoldTime (detik animasi) montage ini ditahan selama tombol ditahan. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Block")
	TObjectPtr<UAnimMontage> BlockMontage = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Block", meta = (ClampMin = "0"))
	float BlockHoldTime = 0.2f;

	/** Porsi damage & poise damage yang ditahan (0,8 = sisa 20%). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Block", meta = (ClampMin = "0", ClampMax = "1"))
	float BlockDamageReduction = 0.8f;

	/** Stamina hilang tiap pukulan ditangkis; stamina habis = guard break. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Block", meta = (ClampMin = "0"))
	float BlockStaminaPerHit = 15.0f;

	/** Lebar kerucut depan (derajat) tempat serangan bisa ditangkis/di-parry; dari belakang tetap kena. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Block", meta = (ClampMin = "0", ClampMax = "360"))
	float BlockAngle = 140.0f;

	/** Laju jalan selama menangkis (x MaxWalkSpeed). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Block", meta = (ClampMin = "0", ClampMax = "1"))
	float BlockMoveSpeedScale = 0.4f;

	/** Dorongan mundur saat pukulan ditangkis (cm/s). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Block", meta = (ClampMin = "0"))
	float BlockPushback = 300.0f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Block", meta = (ClampMin = "0", Units = "s"))
	float GuardBreakStaggerDuration = 1.0f;

	/** Jendela parry setelah tombol tangkis ditekan (manusia 0,2; raksasa 0,25). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Block", meta = (ClampMin = "0", Units = "s"))
	float ParryWindow = 0.2f;

	/** Tekan tangkis lagi dalam waktu ini setelah tekanan sebelumnya = tanpa jendela parry baru (anti spam). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Block", meta = (ClampMin = "0", Units = "s"))
	float ParryLockout = 0.5f;

	/** Lama penyerang stagger setelah di-parry. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Block", meta = (ClampMin = "0", Units = "s"))
	float ParryStaggerDuration = 1.0f;

	// ------------------------------------------------------------------ stagger

	/** Animasi stagger karakter ini (opsional; reaksi lengkap di Iterasi 4). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Stagger")
	TObjectPtr<UAnimMontage> StaggerMontage = nullptr;
};
