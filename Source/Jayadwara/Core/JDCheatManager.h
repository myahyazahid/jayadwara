#pragma once

#include "CoreMinimal.h"
#include "GameFramework/CheatManager.h"
#include "JDCheatManager.generated.h"

class UJDAbilitySystemComponent;

/**
 * Cheat & alat debug Fase 1 (docs/23 bagian 7). Perintah konsol berawalan "JD." didaftarkan di JDCheatManager.cpp
 * (nama UFUNCTION Exec tidak boleh bertitik) dan diteruskan ke fungsi di sini. Hanya di build non-Shipping;
 * cheat aktif otomatis di PIE dan Standalone (AGameModeBase::AllowCheats).
 *
 * Iterasi 1: JD.God, JD.Damage <n>, JD.Heal, JD.Stamina <n>. Iterasi 3: JD.Dummy.Attack <0|1>, JD.Input <tag> <1|0>
 * (keduanya tanpa cheat manager).
 * Perintah lain ditambahkan per iterasi.
 */
UCLASS()
class JAYADWARA_API UJDCheatManager : public UCheatManager
{
	GENERATED_BODY()

public:
	/** JD.God: damage tidak mengurangi Health (berlaku juga untuk pawn setelah transformasi). */
	void ToggleGod();

	/** JD.Damage <n>: damage lewat UJDGE_Damage ke pawn pemain (jalur yang sama dengan pukulan musuh). */
	void ApplyDamage(float Amount);

	/** JD.Heal: Health penuh, State.Dead dilepas. */
	void Heal();

	/** JD.Stamina <n>: kurangi stamina n (memicu jeda regen seperti dodge/tangkis). */
	void SpendStamina(float Amount);

	/** Dipanggil AJDPlayerController setiap possess: bawa status cheat ke pawn baru. */
	void ApplyToPawn(APawn* Pawn);

private:
	UJDAbilitySystemComponent* GetPawnASC() const;

	bool bGod = false;
};
