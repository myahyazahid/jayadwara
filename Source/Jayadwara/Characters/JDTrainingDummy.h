#pragma once

#include "CoreMinimal.h"
#include "Characters/JDCharacterBase.h"
#include "JDTrainingDummy.generated.h"

struct FOnAttributeChangeData;

/**
 * Target latihan di Test_Combat (docs/23 Iterasi 2): punya atribut GAS seperti musuh, tidak bergerak, tidak mati.
 * Tiap kena menampilkan angka damage melayang; Health & Poise penuh lagi setelah ResetDelay tanpa dipukul (atau
 * sesaat setelah Health habis). Mode menyerang berkala (latihan tangkis/parry) ditambahkan di Iterasi 3.
 */
UCLASS()
class JAYADWARA_API AJDTrainingDummy : public AJDCharacterBase
{
	GENERATED_BODY()

public:
	AJDTrainingDummy();

protected:
	virtual void BeginPlay() override;
	virtual void HandleOutOfHealth(AActor* DamageInstigator, float DamageAmount) override;

	/** Detik tanpa dipukul sebelum atribut penuh lagi. */
	UPROPERTY(EditAnywhere, Category = "Dummy", meta = (ClampMin = "0.1"))
	float ResetDelay = 3.0f;

	/** Tampilkan angka damage di atas kepala (debug draw, hanya build non-Shipping). */
	UPROPERTY(EditAnywhere, Category = "Dummy")
	bool bShowDamageNumbers = true;

private:
	void OnHealthChanged(const FOnAttributeChangeData& Data);
	void ResetAttributes();

	FTimerHandle ResetTimer;
	int32 ComboHits = 0;
	float ComboDamage = 0.0f;
};
