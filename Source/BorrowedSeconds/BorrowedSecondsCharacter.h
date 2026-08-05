// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Logging/LogMacros.h"
#include "BorrowedSecondsCharacter.generated.h"

class UInputComponent;
class USkeletalMeshComponent;
class UCameraComponent;
class UInputAction;
class UGrabberComponent;
class UPhysicsHandleComponent;
class USoundBase;
struct FInputActionValue;

DECLARE_LOG_CATEGORY_EXTERN(LogTemplateCharacter, Log, All);

/**
 *  A basic first person character
 */
UCLASS(abstract)
class ABorrowedSecondsCharacter : public ACharacter
{
	GENERATED_BODY()

	/** Pawn mesh: first person view (arms; seen only by self) */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Components", meta = (AllowPrivateAccess = "true"))
	USkeletalMeshComponent* FirstPersonMesh;

	/** First person camera */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Components", meta = (AllowPrivateAccess = "true"))
	UCameraComponent* FirstPersonCameraComponent;

protected:
	virtual void BeginPlay() override;

	/** Jump Input Action */
	UPROPERTY(EditAnywhere, Category ="Input")
	UInputAction* JumpAction;

	/** Move Input Action */
	UPROPERTY(EditAnywhere, Category ="Input")
	UInputAction* MoveAction;

	/** Look Input Action */
	UPROPERTY(EditAnywhere, Category ="Input")
	class UInputAction* LookAction;

	/** Mouse Look Input Action */
	UPROPERTY(EditAnywhere, Category ="Input")
	class UInputAction* MouseLookAction;

	/** Grab Input Action */
	UPROPERTY(EditAnywhere, Category = "Input")
	class UInputAction* GrabAction;

	/** Release Input Action */
	UPROPERTY(EditAnywhere, Category = "Input")
	class UInputAction* ReleaseAction;

	UPROPERTY(EditAnywhere, Category = "Input")
	class UInputAction* ResetAction;
	
public:
	ABorrowedSecondsCharacter();

	virtual void Tick(float DeltaTime) override;

protected:

	/** Called from Input Actions for movement input */
	void MoveInput(const FInputActionValue& Value);

	/** Called from Input Actions for looking input */
	void LookInput(const FInputActionValue& Value);

	/** Mouse look is separate so controller response is not affected by mouse settings. */
	void MouseLookInput(const FInputActionValue& Value);

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Input", meta = (ClampMin = "0.01", ClampMax = "10.0"))
	float MouseSensitivityX = 1.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Input", meta = (ClampMin = "0.01", ClampMax = "10.0"))
	float MouseSensitivityY = 1.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Movement Feel", meta = (ClampMin = "0.0"))
	float GroundAcceleration = 2048.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Movement Feel", meta = (ClampMin = "0.0"))
	float GroundBrakingDeceleration = 2048.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Movement Feel", meta = (ClampMin = "0.0"))
	float GroundFriction = 8.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Movement Feel", meta = (ClampMin = "0.0", ClampMax = "1.0"))
	float AirControl = 0.5f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Movement Feel", meta = (ClampMin = "0.0"))
	float FallingBrakingDeceleration = 1500.0f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadWrite, Category = "Movement Feel", meta = (ClampMin = "0.1"))
	float GravityScale = 1.0f;

	/** Handles aim inputs from either controls or UI interfaces */
	UFUNCTION(BlueprintCallable, Category="Input")
	virtual void DoAim(float Yaw, float Pitch);

	/** Handles move inputs from either controls or UI interfaces */
	UFUNCTION(BlueprintCallable, Category="Input")
	virtual void DoMove(float Right, float Forward);

	/** Handles jump start inputs from either controls or UI interfaces */
	UFUNCTION(BlueprintCallable, Category="Input")
	virtual void DoJumpStart();

	/** Handles jump end inputs from either controls or UI interfaces */
	UFUNCTION(BlueprintCallable, Category="Input")
	virtual void DoJumpEnd();


protected:

	/** Set up input action bindings */
	virtual void SetupPlayerInputComponent(UInputComponent* InputComponent) override;

public:

	UFUNCTION()
	void ResetAllCells();

	UPROPERTY(VisibleAnywhere)
	UGrabberComponent* Grabber;

	UPROPERTY(VisibleAnywhere)
	UPhysicsHandleComponent* PhysicsHandle;

	/** Returns the first person mesh **/
	USkeletalMeshComponent* GetFirstPersonMesh() const { return FirstPersonMesh; }

	/** Returns first person camera component **/
	UCameraComponent* GetFirstPersonCameraComponent() const { return FirstPersonCameraComponent; }

	UPROPERTY(EditAnywhere, Category = "Audio|Footsteps")
	TArray<TObjectPtr<USoundBase>> FootstepSounds;

	UPROPERTY(EditAnywhere, Category = "Audio|Footsteps", meta = (ClampMin = "1.0"))
	float FootstepDistance = 180.0f;

	float AccumulatedFootstepDistance = 0.0f;
	int32 LastFootstepSoundIndex = INDEX_NONE;

};

