#include "Abilities/JDGameplayTags.h"

namespace JDGameplayTags
{
	UE_DEFINE_GAMEPLAY_TAG_COMMENT(Input_Attack_Light, "Input.Attack.Light", "Pukulan ringan: LMB / Square / X");
	UE_DEFINE_GAMEPLAY_TAG_COMMENT(Input_Attack_Heavy, "Input.Attack.Heavy", "Pukulan berat + finisher: E / Triangle / Y");
	UE_DEFINE_GAMEPLAY_TAG_COMMENT(Input_Dodge, "Input.Dodge", "Dodge: Left Shift / Circle / B");
	UE_DEFINE_GAMEPLAY_TAG_COMMENT(Input_Block, "Input.Block", "Tangkis (tahan) + parry (tekan tepat waktu): RMB / R2 / RT");
	UE_DEFINE_GAMEPLAY_TAG_COMMENT(Input_Jump, "Input.Jump", "Lompat: Space / Cross / A");
	UE_DEFINE_GAMEPLAY_TAG_COMMENT(Input_Transform, "Input.Transform", "Transformasi: T / L1+R1 / LB+RB");
	UE_DEFINE_GAMEPLAY_TAG_COMMENT(Input_LockOn, "Input.LockOn", "Lock-on boss: Q, klik tengah / R3 / RS");

	UE_DEFINE_GAMEPLAY_TAG(Ability_Attack_Light, "Ability.Attack.Light");
	UE_DEFINE_GAMEPLAY_TAG(Ability_Attack_Heavy, "Ability.Attack.Heavy");
	UE_DEFINE_GAMEPLAY_TAG(Ability_Dodge, "Ability.Dodge");
	UE_DEFINE_GAMEPLAY_TAG(Ability_Block, "Ability.Block");
	UE_DEFINE_GAMEPLAY_TAG(Ability_HitReact, "Ability.HitReact");
	UE_DEFINE_GAMEPLAY_TAG(Ability_Finisher, "Ability.Finisher");

	UE_DEFINE_GAMEPLAY_TAG_COMMENT(State_Transform_Ready, "State.Transform.Ready", "Energi transformasi penuh, boleh berubah");
	UE_DEFINE_GAMEPLAY_TAG(State_Attacking, "State.Attacking");
	UE_DEFINE_GAMEPLAY_TAG_COMMENT(State_Combat_ComboWindow, "State.Combat.ComboWindow", "Dipasang notify ComboWindow; input ringan melanjutkan combo");
	UE_DEFINE_GAMEPLAY_TAG(State_Dodging, "State.Dodging");
	UE_DEFINE_GAMEPLAY_TAG(State_Invulnerable, "State.Invulnerable");
	UE_DEFINE_GAMEPLAY_TAG(State_Blocking, "State.Blocking");
	UE_DEFINE_GAMEPLAY_TAG(State_ParryWindow, "State.ParryWindow");
	UE_DEFINE_GAMEPLAY_TAG(State_Stagger, "State.Stagger");
	UE_DEFINE_GAMEPLAY_TAG(State_Knockdown, "State.Knockdown");
	UE_DEFINE_GAMEPLAY_TAG(State_Dead, "State.Dead");
	UE_DEFINE_GAMEPLAY_TAG_COMMENT(State_Downed, "State.Downed", "Minion roboh, bisa bangkit lagi kecuali di-finisher");

	UE_DEFINE_GAMEPLAY_TAG(Event_Hit, "Event.Hit");
	UE_DEFINE_GAMEPLAY_TAG(Event_Hit_Blocked, "Event.Hit.Blocked");
	UE_DEFINE_GAMEPLAY_TAG(Event_Hit_Parried, "Event.Hit.Parried");
	UE_DEFINE_GAMEPLAY_TAG(Event_Combo_Continue, "Event.Combo.Continue");
	UE_DEFINE_GAMEPLAY_TAG(Event_Poise_Broken, "Event.Poise.Broken");
	UE_DEFINE_GAMEPLAY_TAG_COMMENT(Event_HitReact, "Event.HitReact", "Pemicu UJDGA_HitReact; jenis reaksi = tag anak, durasi = EventMagnitude (0 = dari profil)");
	UE_DEFINE_GAMEPLAY_TAG(Event_HitReact_Light, "Event.HitReact.Light");
	UE_DEFINE_GAMEPLAY_TAG(Event_HitReact_Stagger, "Event.HitReact.Stagger");
	UE_DEFINE_GAMEPLAY_TAG(Event_HitReact_Knockdown, "Event.HitReact.Knockdown");
	UE_DEFINE_GAMEPLAY_TAG(Event_BodyPart_Detached, "Event.BodyPart.Detached");
	UE_DEFINE_GAMEPLAY_TAG(Event_BodyPart_Reattached, "Event.BodyPart.Reattached");

	UE_DEFINE_GAMEPLAY_TAG(Data_Damage, "Data.Damage");
	UE_DEFINE_GAMEPLAY_TAG(Data_PoiseDamage, "Data.PoiseDamage");
	UE_DEFINE_GAMEPLAY_TAG(Data_SyncPenalty, "Data.SyncPenalty");
	UE_DEFINE_GAMEPLAY_TAG_COMMENT(Data_StaminaRegen, "Data.StaminaRegen", "Stamina per tick UJDGE_StaminaRegen");
	UE_DEFINE_GAMEPLAY_TAG_COMMENT(Data_PoiseRegen, "Data.PoiseRegen", "Poise per tick UJDGE_PoiseRegen");
	UE_DEFINE_GAMEPLAY_TAG(Data_Init_MaxHealth, "Data.Init.MaxHealth");
	UE_DEFINE_GAMEPLAY_TAG(Data_Init_MaxStamina, "Data.Init.MaxStamina");
	UE_DEFINE_GAMEPLAY_TAG(Data_Init_MaxPoise, "Data.Init.MaxPoise");
	UE_DEFINE_GAMEPLAY_TAG(Data_Init_MaxSync, "Data.Init.MaxSync");
	UE_DEFINE_GAMEPLAY_TAG(Data_Init_MaxTransformEnergy, "Data.Init.MaxTransformEnergy");

	UE_DEFINE_GAMEPLAY_TAG(GameplayCue_Hit_Light, "GameplayCue.Hit.Light");
	UE_DEFINE_GAMEPLAY_TAG(GameplayCue_Hit_Heavy, "GameplayCue.Hit.Heavy");
	UE_DEFINE_GAMEPLAY_TAG(GameplayCue_Hit_Blocked, "GameplayCue.Hit.Blocked");
	UE_DEFINE_GAMEPLAY_TAG(GameplayCue_Parry, "GameplayCue.Parry");
	UE_DEFINE_GAMEPLAY_TAG(GameplayCue_Dodge, "GameplayCue.Dodge");
	UE_DEFINE_GAMEPLAY_TAG(GameplayCue_Bone_Break, "GameplayCue.Bone.Break");
	UE_DEFINE_GAMEPLAY_TAG(GameplayCue_Giant_Footstep, "GameplayCue.Giant.Footstep");
	UE_DEFINE_GAMEPLAY_TAG(GameplayCue_Building_Collapse, "GameplayCue.Building.Collapse");

	UE_DEFINE_GAMEPLAY_TAG(Boss_Phase_1, "Boss.Phase.1");
	UE_DEFINE_GAMEPLAY_TAG(Boss_Phase_2, "Boss.Phase.2");
	UE_DEFINE_GAMEPLAY_TAG(Boss_WeakPoint_Exposed, "Boss.WeakPoint.Exposed");

	UE_DEFINE_GAMEPLAY_TAG_COMMENT(Cheat_God, "Cheat.God", "JD.God: damage tidak mengurangi Health");
}
