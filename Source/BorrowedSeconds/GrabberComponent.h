// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/SceneComponent.h"
#include "GrabberComponent.generated.h"

class UPhysicsHandleComponent;

UCLASS( ClassGroup=(Custom), meta=(BlueprintSpawnableComponent) )
class BORROWEDSECONDS_API UGrabberComponent : public USceneComponent
{
	GENERATED_BODY()

public:	
	// Sets default values for this component's properties
	UGrabberComponent();

protected:
	// Called when the game starts
	virtual void BeginPlay() override;

public:	
	// Called every frame
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
	UFUNCTION(BlueprintCallable)
	void Grab();

	UFUNCTION(BlueprintCallable)
	void Release();

	UPROPERTY(EditAnywhere)
	float MaxDistance;

	UPROPERTY(EditAnywhere)
	float GrabRadius;

	UPROPERTY(EditAnywhere)
	float GrabDistance;

	/** Collision channel used by the grab sweep. Visibility preserves existing content. */
	UPROPERTY(EditAnywhere, Category = "Interaction")
	TEnumAsByte<ECollisionChannel> GrabTraceChannel = ECC_GameTraceChannel2;

	UPROPERTY(VisibleAnywhere)
	UPhysicsHandleComponent* PhysicsHandle;
	
};
