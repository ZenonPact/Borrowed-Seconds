// Copyright Epic Games, Inc. All Rights Reserved.

#include "BorrowedSecondsCharacter.h"
#include "Animation/AnimInstance.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "EnhancedInputComponent.h"
#include "InputActionValue.h"
#include "GrabberComponent.h"
#include "PhysicsEngine/PhysicsHandleComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "CountdownComponent.h"
#include "Kismet/GameplayStatics.h"
#include "BorrowedSeconds.h"

ABorrowedSecondsCharacter::ABorrowedSecondsCharacter()
{
	// Set size for collision capsule
	GetCapsuleComponent()->InitCapsuleSize(55.f, 96.0f);
	
	// Create the first person mesh that will be viewed only by this character's owner
	FirstPersonMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("First Person Mesh"));

	FirstPersonMesh->SetupAttachment(GetMesh());
	FirstPersonMesh->SetOnlyOwnerSee(true);
	FirstPersonMesh->FirstPersonPrimitiveType = EFirstPersonPrimitiveType::FirstPerson;
	FirstPersonMesh->SetCollisionProfileName(FName("NoCollision"));

	// Create the Camera Component	
	FirstPersonCameraComponent = CreateDefaultSubobject<UCameraComponent>(TEXT("First Person Camera"));
	FirstPersonCameraComponent->SetupAttachment(FirstPersonMesh, FName("head"));
	FirstPersonCameraComponent->SetRelativeLocationAndRotation(FVector(-2.8f, 5.89f, 0.0f), FRotator(0.0f, 90.0f, -90.0f));
	FirstPersonCameraComponent->bUsePawnControlRotation = true;
	FirstPersonCameraComponent->bEnableFirstPersonFieldOfView = true;
	FirstPersonCameraComponent->bEnableFirstPersonScale = true;
	FirstPersonCameraComponent->FirstPersonFieldOfView = 70.0f;
	FirstPersonCameraComponent->FirstPersonScale = 0.6f;

	// Create the Grabber Component	
	Grabber = CreateDefaultSubobject<UGrabberComponent>(TEXT("GrabberComponent"));
	Grabber->SetupAttachment(FirstPersonCameraComponent);

	// Create the PhysicsHandle Component	
	PhysicsHandle = CreateDefaultSubobject<UPhysicsHandleComponent>(TEXT("PhysicsHandle"));

	// configure the character comps
	GetMesh()->SetOwnerNoSee(true);
	GetMesh()->FirstPersonPrimitiveType = EFirstPersonPrimitiveType::WorldSpaceRepresentation;

	GetCapsuleComponent()->SetCapsuleSize(34.0f, 96.0f);

	// Configure character movement
	GetCharacterMovement()->BrakingDecelerationFalling = 1500.0f;
	GetCharacterMovement()->AirControl = 0.5f;
}

void ABorrowedSecondsCharacter::BeginPlay()
{
	Super::BeginPlay();

	UCharacterMovementComponent* Movement = GetCharacterMovement();
	Movement->MaxAcceleration = GroundAcceleration;
	Movement->BrakingDecelerationWalking = GroundBrakingDeceleration;
	Movement->GroundFriction = GroundFriction;
	Movement->AirControl = AirControl;
	Movement->BrakingDecelerationFalling = FallingBrakingDeceleration;
	Movement->GravityScale = GravityScale;
}

void ABorrowedSecondsCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{	
	// Set up action bindings
	if (UEnhancedInputComponent* EnhancedInputComponent = Cast<UEnhancedInputComponent>(PlayerInputComponent))
	{
		// Jumping
		EnhancedInputComponent->BindAction(JumpAction, ETriggerEvent::Started, this, &ABorrowedSecondsCharacter::DoJumpStart);
		EnhancedInputComponent->BindAction(JumpAction, ETriggerEvent::Completed, this, &ABorrowedSecondsCharacter::DoJumpEnd);

		// Moving
		EnhancedInputComponent->BindAction(MoveAction, ETriggerEvent::Triggered, this, &ABorrowedSecondsCharacter::MoveInput);

		// Looking/Aiming
		EnhancedInputComponent->BindAction(LookAction, ETriggerEvent::Triggered, this, &ABorrowedSecondsCharacter::LookInput);
		EnhancedInputComponent->BindAction(MouseLookAction, ETriggerEvent::Triggered, this, &ABorrowedSecondsCharacter::MouseLookInput);

		// Grab
		EnhancedInputComponent->BindAction(GrabAction, ETriggerEvent::Triggered, Grabber, &UGrabberComponent::Grab);

		// Release
		EnhancedInputComponent->BindAction(ReleaseAction, ETriggerEvent::Triggered, Grabber, &UGrabberComponent::Release);

		// Reset
		EnhancedInputComponent->BindAction(ResetAction, ETriggerEvent::Triggered, this, &ABorrowedSecondsCharacter::ResetAllCells);
	}
	else
	{
		UE_LOG(LogBorrowedSeconds, Error, TEXT("'%s' Failed to find an Enhanced Input Component! This template is built to use the Enhanced Input system. If you intend to use the legacy system, then you will need to update this C++ file."), *GetNameSafe(this));
	}
}

void ABorrowedSecondsCharacter::ResetAllCells()
{
	if (Grabber)
	{
		Grabber->Release();
	}

	TArray<AActor*> AllCells;
	UGameplayStatics::GetAllActorsWithTag(GetWorld(), FName("Grabbable"), AllCells);

	for (AActor* Actor : AllCells)
	{
		if (Actor)
		{
			//Actor->AttachToActor(nullptr, FAttachmentTransformRules::KeepWorldTransform);
			//Actor->SetActorEnableCollision(true);

			//if (UPrimitiveComponent* Prim = Cast<UPrimitiveComponent>(Actor->GetComponentByClass(UPrimitiveComponent::StaticClass())))
			//{
				//Prim->SetSimulatePhysics(true);
			//}

			UCountdownComponent* Countdown = Actor->FindComponentByClass<UCountdownComponent>();
			if (Countdown)
			{
				Countdown->ForceExpire();
			}
		}
	}
}

void ABorrowedSecondsCharacter::MoveInput(const FInputActionValue& Value)
{
	// get the Vector2D move axis
	FVector2D MovementVector = Value.Get<FVector2D>();

	// pass the axis values to the move input
	DoMove(MovementVector.X, MovementVector.Y);

}

void ABorrowedSecondsCharacter::LookInput(const FInputActionValue& Value)
{
	// get the Vector2D look axis
	FVector2D LookAxisVector = Value.Get<FVector2D>();

	// pass the axis values to the aim input
	DoAim(LookAxisVector.X, LookAxisVector.Y);

}

void ABorrowedSecondsCharacter::MouseLookInput(const FInputActionValue& Value)
{
	const FVector2D LookAxisVector = Value.Get<FVector2D>() * MouseSensitivity;
	DoAim(LookAxisVector.X, LookAxisVector.Y);
}

void ABorrowedSecondsCharacter::DoAim(float Yaw, float Pitch)
{
	if (GetController())
	{
		// pass the rotation inputs
		AddControllerYawInput(Yaw);
		AddControllerPitchInput(Pitch);
	}
}

void ABorrowedSecondsCharacter::DoMove(float Right, float Forward)
{
	if (GetController())
	{
		// pass the move inputs
		AddMovementInput(GetActorRightVector(), Right);
		AddMovementInput(GetActorForwardVector(), Forward);
	}
}

void ABorrowedSecondsCharacter::DoJumpStart()
{
	// pass Jump to the character
	Jump();
}

void ABorrowedSecondsCharacter::DoJumpEnd()
{
	// pass StopJumping to the character
	StopJumping();
}
