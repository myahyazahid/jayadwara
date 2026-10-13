#include "JDEditorToolsLibrary.h"

#include "AnimGraphNode_AnimDynamics.h"
#include "AnimGraphNode_ComponentToLocalSpace.h"
#include "AnimGraphNode_LocalToComponentSpace.h"
#include "AnimGraphNode_Root.h"
#include "Animation/AnimBlueprint.h"
#include "Animation/AnimNodeBase.h"
#include "Animation/Skeleton.h"
#include "EdGraph/EdGraph.h"
#include "EdGraphSchema_K2.h"
#include "Engine/SkeletalMesh.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "Kismet2/KismetEditorUtilities.h"
#include "MeshUtilitiesCommon.h"
#include "MeshUtilitiesEngine.h"
#include "PhysicsAssetUtils.h"
#include "RetargetEditor/IKRetargetBatchOperation.h"
#include "Retargeter/IKRetargeter.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/PhysicsConstraintTemplate.h"
#include "PhysicsEngine/SkeletalBodySetup.h"

DEFINE_LOG_CATEGORY_STATIC(LogJayadwaraEditor, Log, All);

namespace
{
	const TCHAR* GeneratedNodeTag = TEXT("JD_AnimDynamics");

	bool IsPosePin(const UEdGraphPin* Pin, EEdGraphPinDirection Direction)
	{
		return Pin && Pin->Direction == Direction && Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_Struct
			&& (Pin->PinType.PinSubCategoryObject == FPoseLink::StaticStruct()
				|| Pin->PinType.PinSubCategoryObject == FComponentSpacePoseLink::StaticStruct());
	}

	UEdGraphPin* FindPosePin(UEdGraphNode* Node, EEdGraphPinDirection Direction)
	{
		for (UEdGraphPin* Pin : Node->Pins)
		{
			if (IsPosePin(Pin, Direction))
			{
				return Pin;
			}
		}
		return nullptr;
	}

	bool IsGenerated(const UEdGraphNode* Node)
	{
		return Node && Node->NodeComment == GeneratedNodeTag;
	}

	/** Sumbu lokal (0=X,1=Y,2=Z) tempat anak pertama tulang berada = arah panjang tulang. */
	int32 AlongBoneAxis(const FReferenceSkeleton& Ref, int32 BoneIndex)
	{
		for (int32 i = BoneIndex + 1; i < Ref.GetRawBoneNum(); ++i)
		{
			if (Ref.GetParentIndex(i) == BoneIndex)
			{
				const FVector T = Ref.GetRefBonePose()[i].GetTranslation().GetAbs();
				return T.X >= T.Y && T.X >= T.Z ? 0 : (T.Y >= T.Z ? 1 : 2);
			}
		}
		return 0;
	}

	template <typename TNode>
	TNode* CreateGraphNode(UEdGraph& Graph, int32 PosX, int32 PosY)
	{
		FGraphNodeCreator<TNode> Creator(Graph);
		TNode* Node = Creator.CreateNode();
		Node->NodePosX = PosX;
		Node->NodePosY = PosY;
		Creator.Finalize();
		Node->NodeComment = GeneratedNodeTag;
		return Node;
	}
}

int32 UJDEditorToolsLibrary::RebuildPhysicsAsset(UPhysicsAsset* PhysicsAsset, USkeletalMesh* Mesh, const TArray<FName>& BodyBones,
	const TArray<FString>& ExcludePrefixes, float AngularLimitDeg)
{
	if (!PhysicsAsset || !Mesh)
	{
		return 0;
	}

	const FReferenceSkeleton& Ref = Mesh->GetRefSkeleton();
	auto IsExcluded = [&ExcludePrefixes](FName Name)
	{
		const FString S = Name.ToString();
		return ExcludePrefixes.ContainsByPredicate([&S](const FString& P) { return S.StartsWith(P); });
	};

	TSet<int32> BodySet;
	for (const FName Bone : BodyBones)
	{
		const int32 Index = Ref.FindBoneIndex(Bone);
		if (Index == INDEX_NONE)
		{
			UE_LOG(LogJayadwaraEditor, Warning, TEXT("RebuildPhysicsAsset: tulang %s tidak ada"), *Bone.ToString());
			continue;
		}
		BodySet.Add(Index);
	}

	// Vertex tiap body = vertex tulangnya + turunan tanpa body (jari, twist); cabang yang dikecualikan tidak ikut.
	TArray<FBoneVertInfo> Infos;
	FMeshUtilitiesEngine::CalcBoneVertInfos(Mesh, Infos, true);
	TMap<int32, FBoneVertInfo> Merged;
	for (const int32 Index : BodySet)
	{
		Merged.Add(Index, Infos[Index]);
	}
	for (int32 i = 0; i < Ref.GetRawBoneNum(); ++i)
	{
		if (BodySet.Contains(i))
		{
			continue;
		}
		int32 Owner = i;
		bool bSkip = false;
		while (Owner != INDEX_NONE && !BodySet.Contains(Owner))
		{
			if (IsExcluded(Ref.GetBoneName(Owner)))
			{
				bSkip = true;
				break;
			}
			Owner = Ref.GetParentIndex(Owner);
		}
		if (!bSkip && Owner != INDEX_NONE)
		{
			Merged[Owner].Positions.Append(Infos[i].Positions);
			Merged[Owner].Normals.Append(Infos[i].Normals);
		}
	}

	PhysicsAsset->Modify();
	while (PhysicsAsset->ConstraintSetup.Num() > 0)
	{
		FPhysicsAssetUtils::DestroyConstraint(PhysicsAsset, PhysicsAsset->ConstraintSetup.Num() - 1);
	}
	while (PhysicsAsset->SkeletalBodySetups.Num() > 0)
	{
		FPhysicsAssetUtils::DestroyBody(PhysicsAsset, PhysicsAsset->SkeletalBodySetups.Num() - 1);
	}

	FPhysAssetCreateParams Params;
	Params.GeomType = EFG_Sphyl;
	Params.VertWeight = EVW_DominantWeight;
	Params.MinBoneSize = 0.0f;
	Params.bAutoOrientToBone = true;
	Params.bDisableCollisionsByDefault = true;

	TArray<int32> Sorted = BodySet.Array();
	Sorted.Sort();                                          // induk selalu sebelum anak di ref skeleton
	for (const int32 BoneIndex : Sorted)
	{
		const FName BoneName = Ref.GetBoneName(BoneIndex);
		const int32 BodyIndex = FPhysicsAssetUtils::CreateNewBody(PhysicsAsset, BoneName, Params);
		USkeletalBodySetup* Body = PhysicsAsset->SkeletalBodySetups[BodyIndex];
		if (!FPhysicsAssetUtils::CreateCollisionFromBone(Body, Mesh, BoneIndex, Params, Merged[BoneIndex]))
		{
			UE_LOG(LogJayadwaraEditor, Warning, TEXT("RebuildPhysicsAsset: kapsul %s gagal dibuat"), *BoneName.ToString());
			FPhysicsAssetUtils::DestroyBody(PhysicsAsset, BodyIndex);
			continue;
		}

		int32 ParentIndex = Ref.GetParentIndex(BoneIndex);
		int32 ParentBody = INDEX_NONE;
		while (ParentIndex != INDEX_NONE && ParentBody == INDEX_NONE)
		{
			ParentBody = PhysicsAsset->FindBodyIndex(Ref.GetBoneName(ParentIndex));
			if (ParentBody == INDEX_NONE)
			{
				ParentIndex = Ref.GetParentIndex(ParentIndex);
			}
		}
		if (ParentBody == INDEX_NONE)
		{
			continue;
		}

		// Sendi di pangkal tulang anak (sama seperti generator bawaan), sudut dibatasi.
		const int32 ConstraintIndex = FPhysicsAssetUtils::CreateNewConstraint(PhysicsAsset, BoneName);
		UPhysicsConstraintTemplate* Constraint = PhysicsAsset->ConstraintSetup[ConstraintIndex];
		FConstraintInstance& Instance = Constraint->DefaultInstance;
		Instance.ConstraintBone1 = BoneName;
		Instance.ConstraintBone2 = Ref.GetBoneName(ParentIndex);
		Instance.SnapTransformsToDefault(EConstraintTransformComponentFlags::All, PhysicsAsset);
		Instance.SetAngularSwing1Limit(EAngularConstraintMotion::ACM_Limited, AngularLimitDeg);
		Instance.SetAngularSwing2Limit(EAngularConstraintMotion::ACM_Limited, AngularLimitDeg);
		Instance.SetAngularTwistLimit(EAngularConstraintMotion::ACM_Limited, AngularLimitDeg * 0.5f);
		Constraint->SetDefaultProfile(Instance);
		PhysicsAsset->DisableCollision(BodyIndex, ParentBody);
	}

	PhysicsAsset->UpdateBodySetupIndexMap();
	PhysicsAsset->UpdateBoundsBodiesArray();
	PhysicsAsset->RefreshPhysicsAssetChange();
	PhysicsAsset->PostEditChange();
	PhysicsAsset->MarkPackageDirty();

	UE_LOG(LogJayadwaraEditor, Log, TEXT("RebuildPhysicsAsset: %d body, %d constraint"),
		PhysicsAsset->SkeletalBodySetups.Num(), PhysicsAsset->ConstraintSetup.Num());
	return PhysicsAsset->SkeletalBodySetups.Num();
}

int32 UJDEditorToolsLibrary::AddAnimDynamicsChains(UAnimBlueprint* AnimBlueprint, const TArray<FJDAnimDynamicsChain>& Chains,
	const TArray<FName>& SphereLimitBones, float SphereLimitRadius, int32 SimulationSpace, float ComponentLinearAccScale, float GravityScale)
{
	if (!AnimBlueprint || !AnimBlueprint->TargetSkeleton)
	{
		return -1;
	}

	UEdGraph* Graph = nullptr;
	for (UEdGraph* Candidate : AnimBlueprint->FunctionGraphs)
	{
		if (Candidate && Candidate->GetFName() == UEdGraphSchema_K2::GN_AnimGraph)
		{
			Graph = Candidate;
			break;
		}
	}
	UAnimGraphNode_Root* Root = nullptr;
	if (Graph)
	{
		for (UEdGraphNode* Node : Graph->Nodes)
		{
			Root = Root ? Root : Cast<UAnimGraphNode_Root>(Node);
		}
	}
	UEdGraphPin* RootIn = Root ? FindPosePin(Root, EGPD_Input) : nullptr;
	if (!RootIn)
	{
		UE_LOG(LogJayadwaraEditor, Error, TEXT("AddAnimDynamicsChains: AnimGraph/Output Pose tidak ditemukan di %s"), *AnimBlueprint->GetName());
		return -1;
	}

	// Sumber pose = keluaran node terakhir yang BUKAN buatan fungsi ini (node lama dilewati lalu dihapus).
	UEdGraphPin* Source = RootIn->LinkedTo.Num() > 0 ? RootIn->LinkedTo[0] : nullptr;
	while (Source && IsGenerated(Source->GetOwningNode()))
	{
		UEdGraphPin* In = FindPosePin(Source->GetOwningNode(), EGPD_Input);
		Source = In && In->LinkedTo.Num() > 0 ? In->LinkedTo[0] : nullptr;
	}
	if (!Source)
	{
		UE_LOG(LogJayadwaraEditor, Error, TEXT("AddAnimDynamicsChains: Output Pose belum tersambung ke pose apa pun"));
		return -1;
	}

	AnimBlueprint->Modify();
	Graph->Modify();
	TArray<UEdGraphNode*> Old;
	for (UEdGraphNode* Node : Graph->Nodes)
	{
		if (IsGenerated(Node))
		{
			Old.Add(Node);
		}
	}
	for (UEdGraphNode* Node : Old)
	{
		FBlueprintEditorUtils::RemoveNode(AnimBlueprint, Node, true);
	}
	RootIn->BreakAllPinLinks();

	const FReferenceSkeleton& Ref = AnimBlueprint->TargetSkeleton->GetReferenceSkeleton();
	const int32 BaseX = Root->NodePosX;
	const int32 BaseY = Root->NodePosY + 300;

	UAnimGraphNode_LocalToComponentSpace* ToComponent = CreateGraphNode<UAnimGraphNode_LocalToComponentSpace>(*Graph, BaseX - 300 * (Chains.Num() + 2), BaseY);
	UEdGraphPin* Prev = FindPosePin(ToComponent, EGPD_Output);
	Source->MakeLinkTo(FindPosePin(ToComponent, EGPD_Input));

	int32 Added = 0;
	for (int32 c = 0; c < Chains.Num(); ++c)
	{
		const FJDAnimDynamicsChain& Chain = Chains[c];
		const int32 StartIndex = Ref.FindBoneIndex(Chain.StartBone);
		if (StartIndex == INDEX_NONE || Ref.FindBoneIndex(Chain.EndBone) == INDEX_NONE)
		{
			UE_LOG(LogJayadwaraEditor, Warning, TEXT("AddAnimDynamicsChains: rantai %s..%s tidak ada"), *Chain.StartBone.ToString(), *Chain.EndBone.ToString());
			continue;
		}

		UAnimGraphNode_AnimDynamics* Dyn = CreateGraphNode<UAnimGraphNode_AnimDynamics>(*Graph, BaseX - 300 * (Chains.Num() + 1 - c), BaseY);
		FAnimNode_AnimDynamics& N = Dyn->Node;
		N.bChain = true;
		N.BoundBone.BoneName = Chain.StartBone;
		N.ChainEnd.BoneName = Chain.EndBone;
		N.SimulationSpace = static_cast<AnimPhysSimSpaceType>(FMath::Clamp(SimulationSpace, 0, 4));   // 0 Component, 1 Actor, 2 World, 3 RootRelative
		N.ComponentLinearAccScale = FVector(ComponentLinearAccScale);   // seberapa besar percepatan karakter mengayunkan kain
		N.GravityScale = GravityScale;
		N.UpdateChainPhysicsBodyDefinitions(Ref);

		// Sumbu panjang tulang = twist; dua sumbu lain = ayun. Linear terkunci (min = max = 0).
		const int32 Along = AlongBoneAxis(Ref, StartIndex);
		FVector Limit(Chain.SwingLimit);
		Limit[Along] = Chain.TwistLimit;
		for (FAnimPhysBodyDefinition& Body : N.PhysicsBodyDefinitions)
		{
			Body.BoxExtents = Chain.BoxExtents;
			Body.CollisionType = AnimPhysCollisionType::CustomSphere;
			Body.SphereCollisionRadius = Chain.CollisionRadius;
			Body.ConstraintSetup.AngularConstraintType = AnimPhysAngularConstraintType::Angular;
			Body.ConstraintSetup.TwistAxis = static_cast<AnimPhysTwistAxis>(Along);
			Body.ConstraintSetup.AngularLimitsMin = -Limit;
			Body.ConstraintSetup.AngularLimitsMax = Limit;
		}

		// Bola penolak di tengah tulang (mis. paha) supaya kain tidak menembus kaki.
		N.bUseSphericalLimits = SphereLimitBones.Num() > 0;
		N.SphericalLimits.Reset();
		for (const FName LimitBone : SphereLimitBones)
		{
			const int32 LimitIndex = Ref.FindBoneIndex(LimitBone);
			if (LimitIndex == INDEX_NONE)
			{
				continue;
			}
			FAnimPhysSphericalLimit Sphere;
			Sphere.DrivingBone.BoneName = LimitBone;
			for (int32 i = LimitIndex + 1; i < Ref.GetRawBoneNum(); ++i)
			{
				if (Ref.GetParentIndex(i) == LimitIndex)
				{
					Sphere.SphereLocalOffset = Ref.GetRefBonePose()[i].GetTranslation() * 0.5f;
					break;
				}
			}
			Sphere.LimitRadius = SphereLimitRadius;
			Sphere.LimitType = ESphericalLimitType::Outer;
			N.SphericalLimits.Add(Sphere);
		}

		Prev->MakeLinkTo(FindPosePin(Dyn, EGPD_Input));
		Prev = FindPosePin(Dyn, EGPD_Output);
		++Added;
	}

	UAnimGraphNode_ComponentToLocalSpace* ToLocal = CreateGraphNode<UAnimGraphNode_ComponentToLocalSpace>(*Graph, BaseX - 300, BaseY);
	Prev->MakeLinkTo(FindPosePin(ToLocal, EGPD_Input));
	FindPosePin(ToLocal, EGPD_Output)->MakeLinkTo(RootIn);

	FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(AnimBlueprint);
	FKismetEditorUtilities::CompileBlueprint(AnimBlueprint);
	AnimBlueprint->MarkPackageDirty();
	UE_LOG(LogJayadwaraEditor, Log, TEXT("AddAnimDynamicsChains: %d rantai di %s"), Added, *AnimBlueprint->GetName());
	return Added;
}

int32 UJDEditorToolsLibrary::BypassAnimGraphNodes(UAnimBlueprint* AnimBlueprint, const FString& ClassNameContains)
{
	if (!AnimBlueprint || ClassNameContains.IsEmpty())
	{
		return 0;
	}

	int32 Removed = 0;
	for (UEdGraph* Graph : AnimBlueprint->FunctionGraphs)
	{
		if (!Graph)
		{
			continue;
		}
		TArray<UEdGraphNode*> Targets;
		for (UEdGraphNode* Node : Graph->Nodes)
		{
			if (Node && Node->GetClass()->GetName().Contains(ClassNameContains))
			{
				Targets.Add(Node);
			}
		}
		for (UEdGraphNode* Node : Targets)
		{
			UEdGraphPin* In = FindPosePin(Node, EGPD_Input);
			UEdGraphPin* Out = FindPosePin(Node, EGPD_Output);
			UEdGraphPin* Source = In && In->LinkedTo.Num() > 0 ? In->LinkedTo[0] : nullptr;
			TArray<UEdGraphPin*> Destinations = Out ? Out->LinkedTo : TArray<UEdGraphPin*>();
			Graph->Modify();
			FBlueprintEditorUtils::RemoveNode(AnimBlueprint, Node, true);
			if (Source)
			{
				for (UEdGraphPin* Destination : Destinations)
				{
					Source->MakeLinkTo(Destination);
				}
			}
			++Removed;
		}
	}

	if (Removed > 0)
	{
		FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(AnimBlueprint);
		FKismetEditorUtilities::CompileBlueprint(AnimBlueprint);
		AnimBlueprint->MarkPackageDirty();
	}
	UE_LOG(LogJayadwaraEditor, Log, TEXT("BypassAnimGraphNodes: %d node '%s' dilepas dari %s"), Removed, *ClassNameContains, *AnimBlueprint->GetName());
	return Removed;
}

void UJDEditorToolsLibrary::RetargetAssetsToFolder(const TArray<UObject*>& Assets, USkeletalMesh* SourceMesh, USkeletalMesh* TargetMesh,
	UIKRetargeter* Retargeter, const FString& FolderPath, const FString& Suffix, bool bIncludeReferencedAssets)
{
	FIKRetargetBatchOperationContext Context;
	for (UObject* Asset : Assets)
	{
		if (Asset)
		{
			Context.AssetsToRetarget.Add(Asset);
		}
	}
	Context.SourceMesh = SourceMesh;
	Context.TargetMesh = TargetMesh;
	Context.IKRetargetAsset = Retargeter;
	Context.NameRule.Suffix = Suffix;
	Context.NameRule.FolderPath = FolderPath / TEXT("");
	Context.bOverwriteExistingFiles = true;
	Context.bIncludeReferencedAssets = bIncludeReferencedAssets;
	if (!Context.IsValid())
	{
		UE_LOG(LogJayadwaraEditor, Error, TEXT("RetargetAssetsToFolder: mesh sumber/target/retargeter tidak valid"));
		return;
	}

	UIKRetargetBatchOperation* Operation = NewObject<UIKRetargetBatchOperation>();
	Operation->AddToRoot();
	Operation->RunRetarget(Context);
	Operation->RemoveFromRoot();
	UE_LOG(LogJayadwaraEditor, Log, TEXT("RetargetAssetsToFolder: %d aset -> %s"), Assets.Num(), *FolderPath);
}

FGameplayTag UJDEditorToolsLibrary::MakeGameplayTag(FName TagName)
{
	return FGameplayTag::RequestGameplayTag(TagName, /*ErrorIfNotFound*/ true);
}
