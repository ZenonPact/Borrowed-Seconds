// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/BoxComponent.h"
#include "TriggerZone.generated.h"

/**
 * 
 */
class UPhysicsHandleComponent;
class UMoverComponent;
UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class BORROWEDSECONDS_API UTriggerZone : public UBoxComponent
{
	GENERATED_BODY()
public:
	UTriggerZone();

protected:
	// Called when the game starts
	virtual void BeginPlay() override;
	
public:
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	AActor* GetAcceptableActor();
	void CheckAcceptableActor(AActor* AcceptedActor);

	UPROPERTY(EditAnywhere)
	AActor* DoorActor;

	UPROPERTY()
	UMoverComponent* Mover;

	UPROPERTY(EditAnywhere)
	FName AcceptableTag;

	UPROPERTY()
	UPhysicsHandleComponent* PlayerPhysicsHandle;

	UPROPERTY()
	AActor* LockedActor = nullptr;


};
