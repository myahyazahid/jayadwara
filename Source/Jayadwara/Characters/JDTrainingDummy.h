#pragma once

#include "CoreMinimal.h"
#include "Characters/JDCharacterBase.h"
#include "JDTrainingDummy.generated.h"

struct FOnAttributeChangeData;

/**
 * Target latihan di Test_Combat (docs/23 Iterasi 2): punya atribut GAS seperti musuh, tidak bergerak, tidak mati.
 * Tiap kena menampilkan angka damage melayang; Health & Poise penuh lagi setelah ResetDelay tanpa dipukul (atau
 * sesaat setelah Health habis).
 *
 * Mode menyerang (Iterasi 3, latihan tangkis/parry/dodge): tiap AttackInterval, kalau pemain dalam AttackRange, dummy
 * menghadap pemain, memberi aba-aba yang terbaca (penanda "!" merah berkedip selama WindUpTime), lalu memukul lewat
 * ability pukulan ringan dari ability set-nya (langkah pertama DA_CombatProfile_Dummy). Bisa di-parry (dummy stagger).
 * Nyalakan per actor (bAttackMode) atau semua lewat cheat JD.Dummy.Attack 0/1.
 */
UCLASS()
class JAYADWARA_API AJDTrainingDummy : public AJDCharacterBase
{
	GENERATED_BODY()

public:
	AJDTrainingDummy();

	UFUNCTION(BlueprintCallable, Category = "Dummy")
	void SetAttackMode(bool bEnable);

	UFUNCTION(BlueprintPure, Category = "Dummy")
	bool IsAttackMode() const { return bAttackMode; }

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void HandleOutOfHealth(AActor* DamageInstigator, float DamageAmount) override;

	/** Detik tanpa dipukul sebelum atribut penuh lagi. */
	UPROPERTY(EditAnywhere, Category = "Dummy", meta = (ClampMin = "0.1"))
	float ResetDelay = 3.0f;

	/** Tampilkan angka damage di atas kepala (debug draw, hanya build non-Shipping). */
	UPROPERTY(EditAnywhere, Category = "Dummy")
	bool bShowDamageNumbers = true;

	UPROPERTY(EditAnywhere, Category = "Dummy|Attack")
	bool bAttackMode = false;

	/** Jarak antar-serangan (s, dari aba-aba ke aba-aba). */
	UPROPERTY(EditAnywhere, Category = "Dummy|Attack", meta = (ClampMin = "0.5"))
	float AttackInterval = 2.5f;

	/** Lama aba-aba sebelum memukul (docs/23 bagian 5: wind-up 0,5 s dengan kedip). */
	UPROPERTY(EditAnywhere, Category = "Dummy|Attack", meta = (ClampMin = "0"))
	float WindUpTime = 0.5f;

	/** Jarak maksimal ke pemain untuk menyerang (cm pada skala 1; dikali skala aktor). */
	UPROPERTY(EditAnywhere, Category = "Dummy|Attack", meta = (ClampMin = "0"))
	float AttackRange = 250.0f;

private:
	void OnHealthChanged(const FOnAttributeChangeData& Data);
	void ResetAttributes();

	void AttackTick();
	void FlashTelegraph();
	void ReleaseAttack();
	APawn* GetAttackTarget() const;
	void FaceTarget(const APawn* Target);

	FTimerHandle ResetTimer;
	FTimerHandle AttackTimer;
	FTimerHandle WindUpTimer;
	FTimerHandle FlashTimer;
	int32 FlashCount = 0;
	int32 ComboHits = 0;
	float ComboDamage = 0.0f;
};
