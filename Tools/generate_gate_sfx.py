"""Generate castle-gate / futuristic-portcullis door concepts."""

from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path


SR = 48_000
OUT = Path(__file__).resolve().parents[1] / "AudioSource" / "Original" / "Door"


def window(t: float, start: float, end: float, edge: float) -> float:
    if t < start or t > end:
        return 0.0
    return min(1.0, (t - start) / edge, (end - t) / edge)


def impact(t: float, start: float, base: float, decay: float, level: float) -> float:
    x = t - start
    if x < 0:
        return 0.0
    tone = math.sin(2 * math.pi * base * x)
    tone += 0.48 * math.sin(2 * math.pi * base * 2.73 * x)
    tone += 0.22 * math.sin(2 * math.pi * base * 4.19 * x)
    return level * tone * math.exp(-x / decay)


def render(variant: str, closing: bool) -> list[float]:
    duration = {"D": 1.95, "E": 1.75, "F": 1.9}[variant]
    rng = random.Random(f"borrowed-seconds-gate-{variant}-{closing}")
    clank_times: list[tuple[float, float, float]] = []
    cursor = 0.13
    while cursor < duration - 0.16:
        cursor += rng.uniform(0.075, 0.135)
        clank_times.append((cursor, rng.uniform(430, 920), rng.uniform(0.028, 0.065)))

    samples: list[float] = []
    low_noise = 0.0
    mid_noise = 0.0

    for i in range(int(duration * SR)):
        t = i / SR
        p = t / duration
        noise = rng.uniform(-1.0, 1.0)
        low_noise += 0.018 * (noise - low_noise)
        mid_noise += 0.12 * (noise - mid_noise)
        motion = window(t, 0.09, duration - 0.1, 0.13)

        # Heavy iron dragging through old guides.
        grind = (0.19 * mid_noise + 0.12 * low_noise) * motion
        rumble = 0.17 * math.sin(2 * math.pi * (39 + 4 * math.sin(2 * math.pi * 0.8 * t)) * t) * motion
        value = grind + rumble

        if variant in ("D", "F"):
            # Irregular chain links and ratchet impacts.
            chain_level = 0.12 if variant == "F" else 0.17
            for start, frequency, decay in clank_times:
                x = t - start
                if 0 <= x < 0.16:
                    value += chain_level * math.sin(2 * math.pi * frequency * x) * math.exp(-x / decay)

        if variant == "E":
            # Slow stressed-metal groan, like a massive hinged iron gate.
            creak_freq = 74 + 24 * math.sin(2 * math.pi * (0.7 + 0.2 * p) * t)
            value += 0.20 * math.sin(2 * math.pi * creak_freq * t + 2.5 * math.sin(2 * math.pi * 3.1 * t)) * motion
            value += 0.07 * math.sin(2 * math.pi * 212 * t) * motion

        if variant == "F":
            # Restrained futuristic drive beneath the physical mechanism.
            servo_freq = (82 + 20 * p) if not closing else (104 - 18 * p)
            value += 0.09 * math.sin(2 * math.pi * servo_freq * t) * motion
            value += 0.035 * math.sin(2 * math.pi * servo_freq * 3.02 * t) * motion

        value += impact(t, 0.0, 71 if closing else 86, 0.11, 0.34)
        final_level = 0.82 if closing else 0.53
        value += impact(t, duration - 0.15, 49 if closing else 64, 0.20, final_level)

        # A closing gate gathers threatening weight before its final stop.
        if closing and p > 0.68:
            value *= 1.0 + 0.28 * ((p - 0.68) / 0.32)

        samples.append(math.tanh(value * 1.38) * 0.70)

    fade = int(0.025 * SR)
    for n in range(fade):
        samples[-fade + n] *= 1.0 - n / fade
    return samples


def write(path: Path, samples: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = b"".join(
        struct.pack("<h", int(max(-1.0, min(1.0, sample)) * 32767))
        for sample in samples
    )
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SR)
        wav.writeframes(pcm)


def main() -> None:
    gap = [0.0] * int(0.48 * SR)
    pair_gap = [0.0] * int(0.85 * SR)
    preview: list[float] = []
    for variant in ("D", "E", "F"):
        opening = render(variant, False)
        closing = render(variant, True)
        write(OUT / f"SFX_Door_Open_{variant}.wav", opening)
        write(OUT / f"SFX_Door_Close_{variant}.wav", closing)
        preview.extend(opening + gap + closing + pair_gap)
    write(OUT / "PREVIEW_DoorCastleFuture_DEF.wav", preview)


if __name__ == "__main__":
    main()
