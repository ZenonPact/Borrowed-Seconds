// Fill out your copyright notice in the Description page of Project Settings.


#include "CountdownComponent.h"

// Sets default values for this component's properties
UCountdownComponent::UCountdownComponent()
{
	// Set this component to be initialized when the game starts, and to be ticked every frame.  You can turn these features
	// off to improve performance if you don't need them.
	PrimaryComponentTick.bCanEverTick = true;

	// ...
}


// Called when the game starts
void UCountdownComponent::BeginPlay()
{
	Super::BeginPlay();

	TimeRemaining = StartingTime;
	
}


// Called every frame
void UCountdownComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	
	if (bIsRunning)
	{
		TimeRemaining -= DeltaTime;
		if (TimeRemaining <= 0)
		{
			bIsRunning = false;
			bHasExpired = true;
			OnCountdownExpired.Broadcast();
		}
	}
}

void UCountdownComponent::StartCountdown()
{
	bIsRunning = true;
}

void UCountdownComponent::PauseCountdown()
{
	bIsRunning = false;
}

void UCountdownComponent::ResetCountdown()
{
	TimeRemaining = StartingTime;
	bHasExpired = false;
}

float UCountdownComponent::GetTimeRemaining() const
{
	return TimeRemaining;
}

void UCountdownComponent::ForceExpire()
{
	TimeRemaining = 0.f;
	bIsRunning = false;
	bHasExpired = true;
	OnCountdownExpired.Broadcast();
}
