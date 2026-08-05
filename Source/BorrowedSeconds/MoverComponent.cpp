// Fill out your copyright notice in the Description page of Project Settings.


#include "MoverComponent.h"
#include <Kismet/GameplayStatics.h>

// Sets default values for this component's properties
UMoverComponent::UMoverComponent()
{
	// Set this component to be initialized when the game starts, and to be ticked every frame.  You can turn these features
	// off to improve performance if you don't need them.
	PrimaryComponentTick.bCanEverTick = true;

	// ...
}


// Called when the game starts
void UMoverComponent::BeginPlay()
{
	Super::BeginPlay();

	StartingPosition = GetOwner()->GetActorLocation();
	TargetPosition = StartingPosition + MoveOffset;

	MoveSpeed = MoveOffset.Size() / MoveTime;
}


// Called every frame
void UMoverComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	FVector CurrentPosition = GetOwner()->GetActorLocation();

	if (ShouldMove)
	{
		FVector NewLocation = FMath::VInterpConstantTo(CurrentPosition, TargetPosition, DeltaTime, MoveSpeed);
		GetOwner()->SetActorLocation(NewLocation);
	}
	else
	{
		FVector NewLocation = FMath::VInterpConstantTo(CurrentPosition, StartingPosition, DeltaTime, MoveSpeed);
		GetOwner()->SetActorLocation(NewLocation);
	}
}

void UMoverComponent::SetShouldMove(bool Mover)
{
	if (ShouldMove == Mover)
	{
		return;
	}
	UE_LOG(
		LogTemp,
		Warning,
		TEXT("SetShouldMove called on %s: Current=%s, Requested=%s"),
		*GetNameSafe(GetOwner()),
		ShouldMove ? TEXT("true") : TEXT("false"),
		Mover ? TEXT("true") : TEXT("false")
	);
	ShouldMove = Mover;
	if (ShouldMove)
	{
		if (OpenSound)
		{
			UGameplayStatics::PlaySoundAtLocation(this, OpenSound, GetOwner()->GetActorLocation(), 1.0f, 1.0f, 0.0f, DoorAttenuation);
		}	
	}
	else
	{
		if (CloseSound)
		{
			UGameplayStatics::PlaySoundAtLocation(this, CloseSound, GetOwner()->GetActorLocation(), 1.0f, 1.0f, 0.0f, DoorAttenuation);
		}
	}
}

bool UMoverComponent::GetShouldMove() const
{
	return ShouldMove;
}

