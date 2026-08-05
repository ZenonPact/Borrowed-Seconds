"""Generate original heavy-metal door sound concepts for Borrowed Seconds."""

from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path


SR = 48_000
OUT = Path(__file__).resolve().parents[1] / "AudioSource" / "Original" / "Door"


def clamp(value: float) -> float:
    return max(-1.0, min(1.0, value))


def hit(t: float, start: float, frequency: float, decay: float, amount: float) -> float:
    local = t - start
    if local < 0:
        return 0.0
    body = math.sin(2 * math.pi * frequency * local)
    overtone = 0.38 * math.sin(2 * math.pi * frequency * 2.37 * local)
    return amount * (body + overtone) * math.exp(-local / decay)


def smooth_window(t: float, start: float, end: float, edge: float = 0.08) -> float:
    if t < start or t > end:
        return 0.0
    fade_in = min((t - start) / edge, 1.0)
    fade_out = min((end - t) / edge, 1.0)
    return max(0.0, min(fade_in, fade_out))


def render(variant: str, closing: bool) -> list[float]:
    duration = {"A": 1.45, "B": 1.65, "C": 0.92}[variant]
    rng = random.Random(f"borrowed-seconds-door-{variant}-{closing}")
    samples: list[float] = []
    filtered_noise = 0.0

    for i in range(int(duration * SR)):
        t = i / SR
        progress = t / duration
        raw_noise = rng.uniform(-1.0, 1.0)
        filtered_noise += 0.055 * (raw_noise - filtered_noise)

        if variant == "A":
            motion = smooth_window(t, 0.07, duration - 0.10)
            rumble_freq = 48 + 7 * math.sin(2 * math.pi * 1.7 * t)
            value = 0.22 * math.sin(2 * math.pi * rumble_freq * t) * motion
            value += 0.20 * filtered_noise * motion
            value += 0.055 * math.sin(2 * math.pi * 185 * t) * motion
            value += hit(t, 0.0, 92 if closing else 108, 0.08, 0.34)
            value += hit(t, duration - 0.12, 72 if closing else 86, 0.13, 0.68 if closing else 0.48)
        elif variant == "B":
            motion = smooth_window(t, 0.10, duration - 0.13, 0.13)
            motor = 0.17 * math.sin(2 * math.pi * (61 + 5 * progress) * t)
            motor += 0.08 * math.sin(2 * math.pi * 122 * t)
            value = motor * motion
            value += 0.14 * filtered_noise * motion
            value += hit(t, 0.0, 78, 0.11, 0.42)
            value += hit(t, duration - 0.15, 58, 0.17, 0.75 if closing else 0.52)
        else:
            motion = smooth_window(t, 0.045, duration - 0.075, 0.055)
            value = 0.19 * math.sin(2 * math.pi * 67 * t) * motion
            value += 0.23 * filtered_noise * motion
            value += hit(t, 0.0, 118, 0.055, 0.38)
            value += hit(t, duration - 0.09, 76, 0.105, 0.78 if closing else 0.55)

        # Closing gets a slightly stronger final third, suggesting momentum.
        if closing and progress > 0.66:
            value *= 1.0 + 0.22 * ((progress - 0.66) / 0.34)

        samples.append(math.tanh(value * 1.45) * 0.72)

    fade = int(0.025 * SR)
    for offset in range(fade):
        samples[-fade + offset] *= 1.0 - offset / fade
    return samples


def write(path: Path, samples: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = b"".join(struct.pack("<h", int(clamp(sample) * 32767)) for sample in samples)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SR)
        wav.writeframes(pcm)


def main() -> None:
    gap = [0.0] * int(0.45 * SR)
    pair_gap = [0.0] * int(0.8 * SR)
    preview: list[float] = []

    for variant in ("A", "B", "C"):
        opening = render(variant, closing=False)
        closing = render(variant, closing=True)
        write(OUT / f"SFX_Door_Open_{variant}.wav", opening)
        write(OUT / f"SFX_Door_Close_{variant}.wav", closing)
        preview.extend(opening + gap + closing + pair_gap)

    write(OUT / "PREVIEW_DoorHeavyMetal_ABC.wav", preview)


if __name__ == "__main__":
    main()
