// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MoverComponent.generated.h"

class USoundBase;
class USoundAttenuation;

UCLASS( ClassGroup=(Custom), meta=(BlueprintSpawnableComponent) )
class BORROWEDSECONDS_API UMoverComponent : public UActorComponent
{
	GENERATED_BODY()

public:	
	// Sets default values for this component's properties
	UMoverComponent();

protected:
	// Called when the game starts
	virtual void BeginPlay() override;

public:	
	// Called every frame
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
	void SetShouldMove(bool Mover);
	bool GetShouldMove() const;

	UPROPERTY(EditAnywhere)
	FVector MoveOffset;

	UPROPERTY(EditAnywhere)
	float MoveTime;

	FVector StartingPosition;
	FVector TargetPosition;
	float MoveSpeed;

	UPROPERTY(EditAnywhere, Category = "Audio")
	USoundBase* OpenSound = nullptr;	

	UPROPERTY(EditAnywhere, Category = "Audio")
	USoundBase* CloseSound = nullptr;

	UPROPERTY(EditAnywhere, Category = "Audio")
	USoundAttenuation* DoorAttenuation = nullptr;

private:
	bool ShouldMove = false;
};
