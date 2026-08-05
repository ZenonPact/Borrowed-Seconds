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
		TimeRemaining = FMath::Max(TimeRemaining - DeltaTime, 0.f);
		TimeUntilNextPulse -= DeltaTime;
		const int32 DisplayedSecond = FMath::CeilToInt(TimeRemaining);

		if (LastDisplayedSecond != DisplayedSecond)
		{
			LastDisplayedSecond = DisplayedSecond;
			OnCountdownDisplayChanged.Broadcast(TimeRemaining);
		}
		if (TimeRemaining <= 0)
		{
			bIsRunning = false;
			bHasExpired = true;
			OnCountdownExpired.Broadcast(true);
		}
		else if (TimeUntilNextPulse <= 0.0f)
		{
			OnCountdownPulse.Broadcast(TimeRemaining);

			const float RemainingRatio = FMath::Clamp(TimeRemaining / StartingTime, 0.f, 1.f);

			TimeUntilNextPulse = FMath::Lerp(0.15f, 1.f, RemainingRatio);
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
	TimeUntilNextPulse = .2f;
	LastDisplayedSecond = INDEX_NONE;
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
	OnCountdownExpired.Broadcast(false);
}
