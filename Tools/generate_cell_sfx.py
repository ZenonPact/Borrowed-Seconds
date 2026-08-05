"""Generate original mono WAV pickup/release concepts for Borrowed Seconds."""

from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path


SAMPLE_RATE = 48_000
OUTPUT = Path(__file__).resolve().parents[1] / "AudioSource" / "Original" / "CellInteraction"


def envelope(t: float, attack: float, decay: float) -> float:
    if t < attack:
        return t / attack
    return math.exp(-(t - attack) / decay)


def click(t: float, frequency: float, decay: float, amount: float) -> float:
    return amount * math.sin(2 * math.pi * frequency * t) * math.exp(-t / decay)


def noise_burst(rng: random.Random, t: float, decay: float, amount: float) -> float:
    return amount * rng.uniform(-1.0, 1.0) * math.exp(-t / decay)


def render(kind: str, variant: str) -> list[float]:
    duration = 0.34 if kind == "pickup" else 0.42
    rng = random.Random(f"borrowed-seconds-{kind}-{variant}")
    samples: list[float] = []

    for index in range(int(duration * SAMPLE_RATE)):
        t = index / SAMPLE_RATE

        if variant == "A":
            if kind == "pickup":
                pitch = 185 + 330 * min(t / 0.16, 1.0)
                value = 0.34 * math.sin(2 * math.pi * pitch * t) * envelope(t, 0.004, 0.105)
                value += click(t, 1250, 0.018, 0.27)
                value += noise_burst(rng, t, 0.025, 0.08)
            else:
                pitch = 155 - 55 * min(t / 0.18, 1.0)
                value = 0.43 * math.sin(2 * math.pi * pitch * t) * envelope(t, 0.002, 0.13)
                value += click(t, 760, 0.026, 0.34)
                value += noise_burst(rng, t, 0.045, 0.11)
        elif variant == "B":
            if kind == "pickup":
                value = click(t, 980, 0.035, 0.34)
                value += click(t, 1540, 0.018, 0.18)
                value += 0.18 * math.sin(2 * math.pi * 310 * t) * envelope(t, 0.003, 0.09)
            else:
                value = click(t, 620, 0.048, 0.4)
                value += click(max(t - 0.035, 0), 410, 0.055, 0.22) if t >= 0.035 else 0
                value += noise_burst(rng, t, 0.03, 0.07)
        else:
            if kind == "pickup":
                sweep = 260 + 720 * min(t / 0.12, 1.0)
                value = 0.28 * math.sin(2 * math.pi * sweep * t) * envelope(t, 0.003, 0.11)
                value += 0.12 * math.sin(2 * math.pi * sweep * 2.01 * t) * envelope(t, 0.003, 0.07)
                value += click(t, 1800, 0.012, 0.18)
            else:
                sweep = 520 - 360 * min(t / 0.22, 1.0)
                value = 0.34 * math.sin(2 * math.pi * sweep * t) * envelope(t, 0.002, 0.14)
                value += click(t, 540, 0.04, 0.3)
                value += noise_burst(rng, t, 0.05, 0.06)

        # Gentle saturation avoids brittle peaks and gives the effects some body.
        samples.append(math.tanh(value * 1.45) * 0.82)

    fade_samples = int(0.025 * SAMPLE_RATE)
    for offset in range(fade_samples):
        samples[-fade_samples + offset] *= 1.0 - offset / fade_samples
    return samples


def render_subtle_pickup(variant: str) -> list[float]:
    duration = 0.24
    rng = random.Random(f"borrowed-seconds-subtle-pickup-{variant}")
    samples: list[float] = []

    for index in range(int(duration * SAMPLE_RATE)):
        t = index / SAMPLE_RATE

        if variant == "D":
            # Muted magnetic engagement: a small rise with almost no sparkle.
            pitch = 175 + 105 * min(t / 0.11, 1.0)
            value = 0.17 * math.sin(2 * math.pi * pitch * t) * envelope(t, 0.004, 0.075)
            value += click(t, 680, 0.018, 0.11)
            value += noise_burst(rng, t, 0.016, 0.025)
        elif variant == "E":
            # A tactile lift: mostly a soft body and restrained mechanical click.
            value = click(t, 390, 0.036, 0.19)
            value += click(t, 840, 0.017, 0.08)
            value += 0.10 * math.sin(2 * math.pi * 135 * t) * envelope(t, 0.002, 0.065)
        else:
            # Low-energy activation: tonal enough to read, but not overtly electric.
            pitch = 205 + 70 * min(t / 0.13, 1.0)
            value = 0.14 * math.sin(2 * math.pi * pitch * t) * envelope(t, 0.006, 0.09)
            value += 0.055 * math.sin(2 * math.pi * pitch * 1.49 * t) * envelope(t, 0.006, 0.055)
            value += click(t, 510, 0.022, 0.09)

        samples.append(math.tanh(value * 1.2) * 0.58)

    fade_samples = int(0.02 * SAMPLE_RATE)
    for offset in range(fade_samples):
        samples[-fade_samples + offset] *= 1.0 - offset / fade_samples
    return samples


def write_wav(path: Path, samples: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    peak = max(abs(sample) for sample in samples) or 1.0
    gain = min(0.92 / peak, 1.0)
    pcm = b"".join(
        struct.pack("<h", int(max(-1.0, min(1.0, sample * gain)) * 32767))
        for sample in samples
    )
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(pcm)


def main() -> None:
    silence = [0.0] * int(0.55 * SAMPLE_RATE)
    short_gap = [0.0] * int(0.22 * SAMPLE_RATE)
    preview: list[float] = []

    for variant in ("A", "B", "C"):
        pickup = render("pickup", variant)
        release = render("release", variant)
        write_wav(OUTPUT / f"SFX_Cell_Pickup_{variant}.wav", pickup)
        write_wav(OUTPUT / f"SFX_Cell_Release_{variant}.wav", release)
        preview.extend(pickup + short_gap + release + silence)

    write_wav(OUTPUT / "PREVIEW_CellInteraction_ABC.wav", preview)

    subtle_preview: list[float] = []
    for variant in ("D", "E", "F"):
        pickup = render_subtle_pickup(variant)
        write_wav(OUTPUT / f"SFX_Cell_Pickup_{variant}.wav", pickup)
        subtle_preview.extend(pickup + silence)

    write_wav(OUTPUT / "PREVIEW_CellPickup_Subtle_DEF.wav", subtle_preview)


if __name__ == "__main__":
    main()
