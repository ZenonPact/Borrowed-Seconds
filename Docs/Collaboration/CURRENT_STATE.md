# Borrowed Seconds — current state

Last updated: 3 August 2026

## Current milestone

Polish the game-jam build into a stable, presentable portfolio project. Audio
integration is the current focus.

## Completed and working

- Git repository and Git LFS are configured and pushing to GitHub.
- Pause menu opens and closes with Escape, including correct cursor, viewport
  focus, input mode, pause state, Resume, Restart, and Quit behavior.
- Horizontal and vertical mouse sensitivities have separate sliders. The UI
  displays 1–100 and maps to runtime values of 0.01–1.0.
- Master-volume slider drives an Audio Modulation Control Bus Mix.
- Sound Classes exist for Master, SFX, and Music.
- Countdown Tick, Tock, and battery-death Sound Waves are imported as SFX.
- `UCountdownComponent` broadcasts `OnCountdownPulse(RemainingTime)` and varies
  the interval from roughly 1.0 seconds to 0.15 seconds as time expires.
- `BP_Cell` alternates Tick and Tock sounds on countdown pulses.
- Countdown pauses while the cell is on a pedestal and resumes when removed.

## Work in progress

- Connect the battery-death sound to the existing cell-expiry flow and test it.
- The first Tick/Tock pulse should wait approximately one second after a fresh
  countdown/reset rather than playing immediately.

## Known cleanup and polish

- The cell countdown uses a Text Render component updated on Event Tick. Replace
  it with a better presentation that stays above the cell and faces the player;
  avoid unnecessary per-frame UI work where possible.
- Consider disabling or changing held-cell collision so it cannot snag on walls.
- Add an `ESC: Menu` HUD hint.
- Add an instructions widget toggled with `I`.
- Add remaining door, pickup, placement, footstep, ambience, and music audio.
- Finish a packaged-build test and portfolio-facing README before release.

## Next action

Add `SFX_Countdown_BatteryDie` to `BP_Cell` when `OnCountdownExpired` is handled,
then test the complete countdown sequence and the master-volume slider together.

