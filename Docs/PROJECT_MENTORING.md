# Project mentoring notes

## Mouse sensitivity

`ABorrowedSecondsCharacter::MouseSensitivity` scales mouse input only. Change it on the `BP_FirstPersonCharacter` class defaults under **Input**. `1.0` preserves the Input Mapping Context value; lower values slow the mouse and higher values speed it up. Keep controller sensitivity separate because stick input is frame-rate based and usually needs response curves/deadzones.

For a settings menu later, store the player's value in a `USaveGame`, set it on the controlled character, and save immediately after the slider changes.

## Less floaty movement

The character exposes movement feel values under **Movement Feel**:

- `GroundAcceleration`: how quickly movement reaches top speed.
- `GroundBrakingDeceleration`: how quickly the character stops when input is released.
- `GroundFriction`: how strongly direction changes grip the ground.
- `AirControl`: how much steering is possible in the air.
- `FallingBrakingDeceleration`: how much falling lateral motion brakes.
- `GravityScale`: how quickly the character falls.

Tune one value at a time in the character Blueprint. Start with braking and acceleration, then gravity, and only then air control. Test at a stable frame rate and package a Development build before judging the result.

## Custom trace channel

The project defines the `Interactable` trace channel in `Config/DefaultEngine.ini`. To adopt it safely:

1. Open **Project Settings > Collision** and confirm `Interactable` exists.
2. On every grabbable mesh, set its collision response to **Block** for `Interactable`.
3. On `BP_FirstPersonCharacter`, select `GrabberComponent` and change `Grab Trace Channel` from `Visibility` to `Interactable`.
4. Use **Show > Collision** in the viewport and test grabbing walls versus tagged physics objects.

The default remains `Visibility` until step 3, so existing levels keep working. A dedicated channel prevents UI/weapon visibility traces and interaction traces from accidentally sharing rules.

## Performance workflow

Measure before changing visuals. In a Development build, use:

- `stat unit` to decide whether Game, Draw, or GPU is limiting frame time.
- `stat game` for costly game-thread systems.
- `stat gpu` and `profilegpu` for lighting, shadows, post processing, and translucency.
- Unreal Insights for hitches and per-frame CPU work.
- `memreport -full` for memory investigations.

Current project-specific watch points:

- Hardware ray tracing, Lumen, mesh distance fields, and Substrate are all enabled. That is an expensive baseline for a jam game; profile on the target machine before keeping all four.
- Several 4K-class character textures and large Control Rig assets dominate source asset size. Set sensible maximum texture sizes and remove unused template content only through the Unreal Content Browser after checking references.
- `ResetAllCells` performs a tagged world search, but only on player input, so it is not a frame-time problem unless the level contains an extreme actor count.
- The grabber now disables its component tick while idle; pickups, projectiles, and weapons no longer request unused actor ticks.
- Never judge performance solely in the Editor. Compare a packaged Development build at the intended resolution and scalability preset.

