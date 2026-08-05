// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "CountdownComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam( FOnCountdownExpired, bool, bPlayExpirationSound);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnCountdownPulse, float, RemainingTime);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnCountdownDisplayChanged, float, RemainingTime);

UCLASS( ClassGroup=(Custom), meta=(BlueprintSpawnableComponent) )
class BORROWEDSECONDS_API UCountdownComponent : public UActorComponent
{
	GENERATED_BODY()

public:	
	// Sets default values for this component's properties
	UCountdownComponent();

protected:
	// Called when the game starts
	virtual void BeginPlay() override;

public:	
	// Called every frame
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
	void StartCountdown();
	void PauseCountdown();


	UPROPERTY(EditAnywhere)
	float StartingTime;

	UPROPERTY(VisibleAnywhere)
	float TimeRemaining;

	UPROPERTY(BlueprintAssignable)
	FOnCountdownPulse OnCountdownPulse;

	UPROPERTY()
	bool bIsRunning = false;

	UPROPERTY()
	bool bHasExpired = false;

	UPROPERTY(BlueprintAssignable)
	FOnCountdownExpired OnCountdownExpired;

	UFUNCTION(BlueprintCallable)
	void ResetCountdown();

	UFUNCTION(BlueprintCallable)
	float GetTimeRemaining() const;
	
	void ForceExpire();

	UPROPERTY(BlueprintAssignable, Category = "Countdown|Events")
	FOnCountdownDisplayChanged OnCountdownDisplayChanged;

private:
	UPROPERTY()
	float TimeUntilNextPulse = .2f;

	int32 LastDisplayedSecond = INDEX_NONE;
};
