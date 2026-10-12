#include "UI/JDHUDWidget.h"

#include "Abilities/JDAttributeSet.h"
#include "AbilitySystemComponent.h"
#include "AbilitySystemGlobals.h"
#include "Blueprint/WidgetTree.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/ProgressBar.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "GameFramework/PlayerController.h"

TSharedRef<SWidget> UJDHUDWidget::RebuildWidget()
{
	// Kelas C++ murni tidak punya layout; WBP turunan sudah punya root dari designer.
	if (WidgetTree && !WidgetTree->RootWidget)
	{
		BuildDefaultLayout();
	}
	return Super::RebuildWidget();
}

void UJDHUDWidget::BuildDefaultLayout()
{
	UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("Root"));
	WidgetTree->RootWidget = Root;

	UVerticalBox* Box = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("Bars"));
	UCanvasPanelSlot* BoxSlot = Root->AddChildToCanvas(Box);
	// Kiri bawah: kiri atas dipakai pesan debug layar (JD.Debug.Input, AddOnScreenDebugMessage).
	BoxSlot->SetAnchors(FAnchors(0.0f, 1.0f));
	BoxSlot->SetAlignment(FVector2D(0.0f, 1.0f));
	BoxSlot->SetPosition(FVector2D(32.0f, -32.0f));
	BoxSlot->SetAutoSize(true);

	AddDefaultRow(Box, NSLOCTEXT("JDHUD", "Health", "Health"), FLinearColor(0.80f, 0.12f, 0.10f), HealthBar, HealthText);
	AddDefaultRow(Box, NSLOCTEXT("JDHUD", "Stamina", "Stamina"), FLinearColor(0.20f, 0.70f, 0.25f), StaminaBar, StaminaText);
	AddDefaultRow(Box, NSLOCTEXT("JDHUD", "Sync", "Sync"), FLinearColor(0.95f, 0.70f, 0.15f), SyncBar, SyncText);
	AddDefaultRow(Box, NSLOCTEXT("JDHUD", "Energy", "Energi"), FLinearColor(0.25f, 0.55f, 0.95f), TransformEnergyBar, TransformEnergyText);
}

void UJDHUDWidget::AddDefaultRow(UVerticalBox* Box, const FText& Label, const FLinearColor& Color, TObjectPtr<UProgressBar>& OutBar, TObjectPtr<UTextBlock>& OutText)
{
	UHorizontalBox* Row = WidgetTree->ConstructWidget<UHorizontalBox>();
	UVerticalBoxSlot* RowSlot = Box->AddChildToVerticalBox(Row);
	RowSlot->SetPadding(FMargin(0.0f, 0.0f, 0.0f, 6.0f));

	USizeBox* Size = WidgetTree->ConstructWidget<USizeBox>();
	Size->SetWidthOverride(260.0f);
	Size->SetHeightOverride(16.0f);
	UHorizontalBoxSlot* SizeSlot = Row->AddChildToHorizontalBox(Size);
	SizeSlot->SetVerticalAlignment(VAlign_Center);

	OutBar = WidgetTree->ConstructWidget<UProgressBar>();
	OutBar->SetFillColorAndOpacity(Color);
	OutBar->SetPercent(1.0f);
	Size->AddChild(OutBar);

	OutText = WidgetTree->ConstructWidget<UTextBlock>();
	OutText->SetText(Label);
	FSlateFontInfo Font = OutText->GetFont();
	Font.Size = 12;
	OutText->SetFont(Font);
	OutText->SetShadowOffset(FVector2D(1.0f, 1.0f));
	OutText->SetShadowColorAndOpacity(FLinearColor(0.0f, 0.0f, 0.0f, 0.8f));
	UHorizontalBoxSlot* TextSlot = Row->AddChildToHorizontalBox(OutText);
	TextSlot->SetPadding(FMargin(8.0f, 0.0f, 0.0f, 0.0f));
	TextSlot->SetVerticalAlignment(VAlign_Center);
}

UAbilitySystemComponent* UJDHUDWidget::GetPawnASC() const
{
	const APlayerController* PC = GetOwningPlayer();
	return UAbilitySystemGlobals::GetAbilitySystemComponentFromActor(PC ? PC->GetPawn() : nullptr);
}

float UJDHUDWidget::GetPercent(const FGameplayAttribute& Value, const FGameplayAttribute& Max) const
{
	const UAbilitySystemComponent* ASC = GetPawnASC();
	if (!ASC || !ASC->HasAttributeSetForAttribute(Max))
	{
		return 0.0f;
	}
	const float MaxValue = ASC->GetNumericAttribute(Max);
	return MaxValue > 0.0f ? FMath::Clamp(ASC->GetNumericAttribute(Value) / MaxValue, 0.0f, 1.0f) : 0.0f;
}

float UJDHUDWidget::GetHealthPercent() const
{
	return GetPercent(UJDAttributeSet::GetHealthAttribute(), UJDAttributeSet::GetMaxHealthAttribute());
}

float UJDHUDWidget::GetStaminaPercent() const
{
	return GetPercent(UJDAttributeSet::GetStaminaAttribute(), UJDAttributeSet::GetMaxStaminaAttribute());
}

float UJDHUDWidget::GetSyncPercent() const
{
	return GetPercent(UJDAttributeSet::GetSyncAttribute(), UJDAttributeSet::GetMaxSyncAttribute());
}

float UJDHUDWidget::GetTransformEnergyPercent() const
{
	return GetPercent(UJDAttributeSet::GetTransformEnergyAttribute(), UJDAttributeSet::GetMaxTransformEnergyAttribute());
}

void UJDHUDWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);

	UpdateRow(HealthBar, HealthText, UJDAttributeSet::GetHealthAttribute(), UJDAttributeSet::GetMaxHealthAttribute());
	UpdateRow(StaminaBar, StaminaText, UJDAttributeSet::GetStaminaAttribute(), UJDAttributeSet::GetMaxStaminaAttribute());
	UpdateRow(SyncBar, SyncText, UJDAttributeSet::GetSyncAttribute(), UJDAttributeSet::GetMaxSyncAttribute());
	UpdateRow(TransformEnergyBar, TransformEnergyText, UJDAttributeSet::GetTransformEnergyAttribute(), UJDAttributeSet::GetMaxTransformEnergyAttribute());
}

void UJDHUDWidget::UpdateRow(UProgressBar* Bar, UTextBlock* Text, const FGameplayAttribute& Value, const FGameplayAttribute& Max) const
{
	const UAbilitySystemComponent* ASC = GetPawnASC();
	const float MaxValue = (ASC && ASC->HasAttributeSetForAttribute(Max)) ? ASC->GetNumericAttribute(Max) : 0.0f;
	const ESlateVisibility RowVisibility = MaxValue > 0.0f ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed;
	if (MaxValue <= 0.0f)
	{
		if (Bar) { Bar->SetVisibility(RowVisibility); }
		if (Text) { Text->SetVisibility(RowVisibility); }
		return;
	}

	const float Current = ASC->GetNumericAttribute(Value);
	if (Bar)
	{
		Bar->SetVisibility(RowVisibility);
		Bar->SetPercent(FMath::Clamp(Current / MaxValue, 0.0f, 1.0f));
	}
	if (Text)
	{
		Text->SetVisibility(RowVisibility);
		Text->SetText(FText::FromString(FString::Printf(TEXT("%s %.0f / %.0f"), *Value.GetName(), Current, MaxValue)));
	}
}
