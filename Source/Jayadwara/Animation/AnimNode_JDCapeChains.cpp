#include "Animation/AnimNode_JDCapeChains.h"

#include "Animation/AnimInstanceProxy.h"

namespace
{
	FVector ClosestOnSegment(const FVector& P, const FVector& A, const FVector& B)
	{
		const FVector AB = B - A;
		const double Len2 = AB.SizeSquared();
		const double T = Len2 > UE_SMALL_NUMBER ? FMath::Clamp(FVector::DotProduct(P - A, AB) / Len2, 0.0, 1.0) : 0.0;
		return A + AB * T;
	}
}

void FAnimNode_JDCapeChains::InitializeBoneReferences(const FBoneContainer& RequiredBones)
{
	ChainStates.Reset();
	for (FJDCapeChain& Chain : Chains)
	{
		Chain.StartBone.Initialize(RequiredBones);
		Chain.EndBone.Initialize(RequiredBones);
		FChainState State;
		if (Chain.StartBone.IsValidToEvaluate(RequiredBones) && Chain.EndBone.IsValidToEvaluate(RequiredBones))
		{
			const FCompactPoseBoneIndex Start = Chain.StartBone.GetCompactPoseIndex(RequiredBones);
			FCompactPoseBoneIndex Bone = Chain.EndBone.GetCompactPoseIndex(RequiredBones);
			while (Bone != INDEX_NONE)
			{
				State.Bones.Insert(Bone, 0);
				if (Bone == Start)
				{
					break;
				}
				Bone = RequiredBones.GetParentBoneIndex(Bone);
			}
			if (State.Bones.Num() < 2 || State.Bones[0] != Start)
			{
				State.Bones.Reset();          // akhir bukan keturunan awal
			}
		}
		ChainStates.Add(MoveTemp(State));
	}
	for (FJDCapeCollider& Collider : Colliders)
	{
		Collider.BoneA.Initialize(RequiredBones);
		Collider.BoneB.Initialize(RequiredBones);
	}
	bReset = true;
}

bool FAnimNode_JDCapeChains::IsValidToEvaluate(const USkeleton* Skeleton, const FBoneContainer& RequiredBones)
{
	for (const FChainState& State : ChainStates)
	{
		if (State.Bones.Num() >= 2)
		{
			return true;
		}
	}
	return false;
}

void FAnimNode_JDCapeChains::ResetDynamics(ETeleportType InTeleportType)
{
	bReset = true;
}

void FAnimNode_JDCapeChains::UpdateInternal(const FAnimationUpdateContext& Context)
{
	FAnimNode_SkeletalControlBase::UpdateInternal(Context);
	PendingDeltaTime += Context.GetDeltaTime();
}

void FAnimNode_JDCapeChains::EvaluateSkeletalControl_AnyThread(FComponentSpacePoseContext& Output, TArray<FBoneTransform>& OutBoneTransforms)
{
	const FTransform ToWorld = Output.AnimInstanceProxy->GetComponentTransform();
	const double CompScale = ToWorld.GetScale3D().GetAbsMax();
	const float Dt = FMath::Min(PendingDeltaTime, 0.1f);
	const bool bTooLong = PendingDeltaTime > 0.25f;          // jeda panjang (hitch, editor) = reset
	PendingDeltaTime = 0.0f;
	FCSPose<FCompactPose>& Pose = Output.Pose;
	const FBoneContainer& Required = Pose.GetPose().GetBoneContainer();

	// kapsul penolak di ruang dunia
	struct FCapsule { FVector A, B; double R; };
	TArray<FCapsule, TInlineAllocator<8>> Caps;
	for (const FJDCapeCollider& C : Colliders)
	{
		if (C.BoneA.IsValidToEvaluate(Required) && C.BoneB.IsValidToEvaluate(Required))
		{
			Caps.Add({ ToWorld.TransformPosition(Pose.GetComponentSpaceTransform(C.BoneA.GetCompactPoseIndex(Required)).GetLocation()),
				ToWorld.TransformPosition(Pose.GetComponentSpaceTransform(C.BoneB.GetCompactPoseIndex(Required)).GetLocation()),
				(C.Radius + CollisionMargin) * CompScale });
		}
	}

	const int32 Steps = FMath::Clamp(FMath::CeilToInt(Dt * 60.0f), 1, 6);
	const double H = Dt / Steps;
	const FVector GravityAcc(0.0, 0.0, -Gravity);
	const double CosMax = FMath::Cos(FMath::DegreesToRadians(MaxAngleDeg));

	for (FChainState& S : ChainStates)
	{
		const int32 NB = S.Bones.Num();
		if (NB < 2)
		{
			continue;
		}
		// target dunia: kepala tiap tulang (pose animasi) + ujung = ekstrapolasi ruas terakhir
		TArray<FTransform, TInlineAllocator<8>> CS;
		TArray<FVector, TInlineAllocator<8>> Target;
		for (const FCompactPoseBoneIndex Bone : S.Bones)
		{
			CS.Add(Pose.GetComponentSpaceTransform(Bone));
			Target.Add(ToWorld.TransformPosition(CS.Last().GetLocation()));
		}
		Target.Add(Target[NB - 1] + (Target[NB - 1] - Target[NB - 2]));
		const int32 NP = Target.Num();

		const bool bTeleport = S.Pos.Num() != NP || bReset || bTooLong
			|| FVector::DistSquared(S.Pos[0], Target[0]) > FMath::Square(TeleportDistance * CompScale);
		if (bTeleport)
		{
			S.Pos = TArray<FVector>(Target.GetData(), NP);
			S.Prev = S.Pos;
			S.PrevTarget = S.Pos;
		}

		for (int32 Step = 1; Step <= Steps && Dt > 0.0f; ++Step)
		{
			const double StepAlpha = double(Step) / Steps;
			const double Damp = FMath::Exp(-AirDrag * H);
			TArray<FVector, TInlineAllocator<8>> T;
			for (int32 i = 0; i < NP; ++i)
			{
				T.Add(FMath::Lerp(S.PrevTarget[i], Target[i], StepAlpha));
			}
			S.Pos[0] = S.Prev[0] = T[0];                               // akar menempel ke badan
			for (int32 i = 1; i < NP; ++i)
			{
				const FVector Vel = (S.Pos[i] - S.Prev[i]) * Damp;       // hambatan udara di ruang dunia
				const FVector Acc = GravityAcc + (T[i] - S.Pos[i]) * Stiffness;
				S.Prev[i] = S.Pos[i];
				S.Pos[i] += Vel + Acc * (H * H);
			}
			for (int32 It = 0; It < Iterations; ++It)
			{
				for (int32 i = 1; i < NP; ++i)
				{
					for (const FCapsule& Cap : Caps)                    // keluar dari kapsul kaki/pinggul
					{
						const FVector Q = ClosestOnSegment(S.Pos[i], Cap.A, Cap.B);
						const FVector D = S.Pos[i] - Q;
						const double Dist = D.Size();
						if (Dist < Cap.R)
						{
							S.Pos[i] = Q + (Dist > UE_KINDA_SMALL_NUMBER ? D / Dist : (T[i] - Q).GetSafeNormal()) * Cap.R;
						}
					}
					// batas sudut terhadap arah animasi, lalu panjang ruas tetap (follow-the-leader dari akar)
					const FVector AnimDir = (T[i] - T[i - 1]).GetSafeNormal();
					const double Len = (T[i] - T[i - 1]).Size();
					FVector Dir = (S.Pos[i] - S.Pos[i - 1]).GetSafeNormal();
					if (Dir.IsNearlyZero())
					{
						Dir = AnimDir;
					}
					if (FVector::DotProduct(Dir, AnimDir) < CosMax)
					{
						const FVector Axis = FVector::CrossProduct(AnimDir, Dir).GetSafeNormal();
						Dir = Axis.IsNearlyZero() ? AnimDir : FQuat(Axis, FMath::DegreesToRadians(MaxAngleDeg)).RotateVector(AnimDir);
					}
					S.Pos[i] = S.Pos[i - 1] + Dir * Len;
				}
			}
		}
		S.PrevTarget = TArray<FVector>(Target.GetData(), NP);

		// tulang: putar dari arah animasi ke arah simulasi (ruang komponen), posisi kepala = partikel
		for (int32 b = 0; b < NB; ++b)
		{
			const FVector AnimDir = ToWorld.InverseTransformVector(Target[b + 1] - Target[b]).GetSafeNormal();
			const FVector SimDir = ToWorld.InverseTransformVector(S.Pos[b + 1] - S.Pos[b]).GetSafeNormal();
			FTransform Out = CS[b];
			Out.SetRotation((FQuat::FindBetweenNormals(AnimDir, SimDir) * Out.GetRotation()).GetNormalized());
			if (b > 0)
			{
				Out.SetLocation(ToWorld.InverseTransformPosition(S.Pos[b]));
			}
			OutBoneTransforms.Add(FBoneTransform(S.Bones[b], Out));
		}
	}
	bReset = false;
	OutBoneTransforms.Sort(FCompareBoneTransformIndex());
}
