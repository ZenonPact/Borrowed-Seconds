"""Create concrete/metal footstep variations from a licensed field recording."""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

import numpy as np
import soundfile as sf


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "AudioSource" / "External" / "CC0" / "Pixabay_6265_ConcreteFootsteps.mp3"
OUT = ROOT / "AudioSource" / "Original" / "Footsteps"
TARGET_RATE = 48_000

# Selected contact times from the source recording. They vary in weight and texture.
CONTACTS = (0.34, 1.62, 2.63, 3.13, 4.13, 6.05)


def resample(samples: np.ndarray, source_rate: int) -> np.ndarray:
    size = round(len(samples) * TARGET_RATE / source_rate)
    old_positions = np.arange(len(samples), dtype=np.float64)
    new_positions = np.linspace(0.0, len(samples) - 1.0, size)
    return np.interp(new_positions, old_positions, samples).astype(np.float32)


def make_step(source: np.ndarray, source_rate: int, contact: float, index: int) -> np.ndarray:
    start = max(0, int((contact - 0.075) * source_rate))
    end = min(len(source), int((contact + 0.46) * source_rate))
    step = source[start:end].copy()

    # Remove the recording's extremely quiet background floor.
    step[np.abs(step) < 0.0012] *= 0.25

    # Match perceived weight without crushing the natural impact dynamics.
    rms = float(np.sqrt(np.mean(step * step))) or 1.0
    step *= min((10.0 ** (-20.0 / 20.0)) / rms, 2.0)
    peak = float(np.max(np.abs(step))) or 1.0
    if peak > 0.58:
        step *= 0.58 / peak

    # A very quiet short metal resonance blends the concrete with the setting.
    t = np.arange(len(step), dtype=np.float64) / source_rate
    ring_start = 0.075
    local = np.maximum(t - ring_start, 0.0)
    active = t >= ring_start
    base = 510.0 + index * 31.0
    ring = np.zeros_like(step)
    ring[active] = (
        0.011 * np.sin(2 * math.pi * base * local[active])
        + 0.005 * np.sin(2 * math.pi * base * 1.83 * local[active])
    ) * np.exp(-local[active] / 0.065)
    step += ring

    fade_in = min(int(0.012 * source_rate), len(step))
    fade_out = min(int(0.11 * source_rate), len(step))
    step[:fade_in] *= np.linspace(0.0, 1.0, fade_in)
    step[-fade_out:] *= np.linspace(1.0, 0.0, fade_out)
    return resample(step, source_rate)


def write(path: Path, samples: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = b"".join(
        struct.pack("<h", int(max(-1.0, min(1.0, float(sample))) * 32767))
        for sample in samples
    )
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(TARGET_RATE)
        wav.writeframes(pcm)


def main() -> None:
    audio, source_rate = sf.read(SOURCE, always_2d=True)
    mono = audio.mean(axis=1)
    preview: list[np.ndarray] = []
    gap = np.zeros(int(0.34 * TARGET_RATE), dtype=np.float32)

    for index, contact in enumerate(CONTACTS, start=1):
        step = make_step(mono, source_rate, contact, index)
        write(OUT / f"SFX_Footstep_ConcreteMetal_{index:02d}.wav", step)
        preview.extend((step, gap))

    write(OUT / "PREVIEW_Footsteps_ConcreteMetal.wav", np.concatenate(preview))


if __name__ == "__main__":
    main()
