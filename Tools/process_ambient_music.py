"""Create a quieter, loop-friendly ambient music file for Borrowed Seconds."""

from pathlib import Path

import numpy as np
import soundfile as sf


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "AudioSource/External/CC0/Pixabay_454726_DarkAmbientCinematicDrone.mp3"
OUTPUT = ROOT / "AudioSource/Final/MUS_DarkAmbientLoop.wav"

CROSSFADE_SECONDS = 8.0
TARGET_PEAK_DB = -8.0


def main() -> None:
    audio, sample_rate = sf.read(SOURCE, always_2d=True, dtype="float32")
    overlap = int(CROSSFADE_SECONDS * sample_rate)

    if len(audio) <= overlap * 2:
        raise ValueError("Source is too short for the requested loop crossfade")

    # Rotate the loop seam into the file: tail -> head, followed by the middle.
    # This makes both the start and end of the exported file join continuously.
    phase = np.linspace(0.0, np.pi / 2.0, overlap, dtype=np.float32)[:, None]
    fade_out = np.cos(phase)
    fade_in = np.sin(phase)
    seam = audio[-overlap:] * fade_out + audio[:overlap] * fade_in
    loop = np.concatenate((seam, audio[overlap:-overlap]), axis=0)

    target_peak = 10.0 ** (TARGET_PEAK_DB / 20.0)
    current_peak = float(np.max(np.abs(loop)))
    if current_peak > 0.0:
        loop *= target_peak / current_peak

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    sf.write(OUTPUT, loop, sample_rate, subtype="PCM_16")

    print(f"Created: {OUTPUT}")
    print(f"Channels: {loop.shape[1]}")
    print(f"Sample rate: {sample_rate} Hz")
    print(f"Duration: {len(loop) / sample_rate:.2f} seconds")


if __name__ == "__main__":
    main()
