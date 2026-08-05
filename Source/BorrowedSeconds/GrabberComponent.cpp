// Fill out your copyright notice in the Description page of Project Settings.


#include "GrabberComponent.h"
#include "CountdownComponent.h"
#include "Sound/SoundBase.h"
#include <Kismet/GameplayStatics.h>
#include "PhysicsEngine/PhysicsHandleComponent.h"

// Sets default values for this component's properties
UGrabberComponent::UGrabberComponent()
{
	// Set this component to be initialized when the game starts, and to be ticked every frame.  You can turn these features
	// off to improve performance if you don't need them.
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = false;

	// ...
}


// Called when the game starts
void UGrabberComponent::BeginPlay()
{
	Super::BeginPlay();

	if (GetOwner())
	{
		PhysicsHandle = GetOwner()->FindComponentByClass<UPhysicsHandleComponent>();
		if (!PhysicsHandle)
		{
			UE_LOG(LogTemp, Display, TEXT("Sorry we didn't find any physic component"));
		}
	}
}


// Called every frame
void UGrabberComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	if (!PhysicsHandle)
	{
		return;
	}
	if (PhysicsHandle->GetGrabbedComponent())
	{
		PhysicsHandle->SetTargetLocation(GetComponentLocation() + GetForwardVector() * GrabDistance);
	}
}

void UGrabberComponent::Grab()
{
	if (!PhysicsHandle || PhysicsHandle->GetGrabbedComponent())
	{
		return;
	}

	FHitResult OutHit;
	FVector StartLocation = GetComponentLocation();
	FVector EndLocation = StartLocation + GetForwardVector() * MaxDistance;
	//FVector GrabbedObjectLocation = StartLocation + GetForwardVector() * GrabDistance; Just to remember what i wanted to do once
	FCollisionQueryParams QueryParameter;
	QueryParameter.AddIgnoredActor(GetOwner());
	bool HasHit = GetWorld()->SweepSingleByChannel(OutHit, StartLocation, EndLocation, FQuat::Identity, GrabTraceChannel, FCollisionShape::MakeSphere(GrabRadius), QueryParameter);

	if (HasHit)
	{
		if (PhysicsHandle and OutHit.GetActor()->ActorHasTag("Grabbable"))
		{
			UCountdownComponent* Countdown = OutHit.GetActor()->FindComponentByClass<UCountdownComponent>();
			if (Countdown)
			{
				Countdown->StartCountdown();
			}
			OutHit.GetComponent()->SetSimulatePhysics(true);
			PhysicsHandle->GrabComponentAtLocationWithRotation(OutHit.GetComponent(), NAME_None, OutHit.ImpactPoint, OutHit.GetComponent()->GetComponentRotation());
			if (PhysicsHandle->GetGrabbedComponent() == OutHit.GetComponent())
			{
				OnActorGrabbed.Broadcast(OutHit.GetActor());
			}
			if (GrabSound)
			{
				UGameplayStatics::PlaySoundAtLocation(this, GrabSound, OutHit.GetComponent()->GetComponentLocation());
			}
			SetComponentTickEnabled(true);
		}
	}
}

void UGrabberComponent::Release()
{
	if (PhysicsHandle->GetGrabbedComponent())
	{
		UPrimitiveComponent* GrabbedComponent =
			PhysicsHandle->GetGrabbedComponent();

		AActor* ReleasedActor = GrabbedComponent->GetOwner();

		const FVector ReleaseLocation = GrabbedComponent->GetComponentLocation();

		if (ReleaseSound)
		{
			UGameplayStatics::PlaySoundAtLocation(this, ReleaseSound, ReleaseLocation);
		}

		PhysicsHandle->ReleaseComponent();

		if (ReleasedActor)
		{
			OnActorReleased.Broadcast(ReleasedActor);
		}

		SetComponentTickEnabled(false);
	}
}

