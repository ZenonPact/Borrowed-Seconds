// Fill out your copyright notice in the Description page of Project Settings.


#include "TriggerZone.h"
#include "Kismet/GameplayStatics.h"
#include "PhysicsEngine/PhysicsHandleComponent.h"
#include "CountdownComponent.h"
#include "GameFramework/Character.h"
#include "MoverComponent.h"

UTriggerZone::UTriggerZone()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void UTriggerZone::BeginPlay()
{
	Super::BeginPlay();

	if (DoorActor)
	{
		Mover = DoorActor->FindComponentByClass<UMoverComponent>();
	}
	ACharacter* Player = UGameplayStatics::GetPlayerCharacter(GetWorld(), 0);
	if (Player)
	{
		PlayerPhysicsHandle = Player->FindComponentByClass<UPhysicsHandleComponent>();
	}
}

void UTriggerZone::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	if (!LockedActor)
	{
		AActor* AcceptedActor = GetAcceptableActor();
		if (AcceptedActor)
		{
			LockedActor = AcceptedActor;
			CheckAcceptableActor(AcceptedActor);
		}
	}
	if (LockedActor)
	{
		TArray<AActor*> OverlappingActors;
		GetOverlappingActors(OverlappingActors);

		if (OverlappingActors.Contains(LockedActor))
		{
			if (Mover && LockedActor->ActorHasTag(AcceptableTag))
			{
				Mover->SetShouldMove(true);
			}
		}
		else
		{
			if (Mover)
			{
				Mover->SetShouldMove(false);
			}
			LockedActor = nullptr;
		}
	}
}

AActor* UTriggerZone::GetAcceptableActor()
{
	TArray<AActor*> OverlappingActors;

	GetOverlappingActors(OverlappingActors);
	for (AActor* SomeActor : OverlappingActors)
	{
		if (PlayerPhysicsHandle && PlayerPhysicsHandle->GetGrabbedComponent() && PlayerPhysicsHandle->GetGrabbedComponent()->GetOwner() == SomeActor)
		{
			continue;
		}
		if (SomeActor->ActorHasTag("Grabbable"))
		{
			return SomeActor;
		}
	}
	return nullptr;
}

void UTriggerZone::CheckAcceptableActor(AActor* AcceptedActor)
{
	AcceptedActor->DisableComponentsSimulatePhysics();
	AcceptedActor->AttachToActor(GetOwner(), FAttachmentTransformRules::SnapToTargetNotIncludingScale);
	UCountdownComponent* Countdown = AcceptedActor->FindComponentByClass<UCountdownComponent>();
	if (Countdown)
	{
		Countdown->PauseCountdown();
	}
}
