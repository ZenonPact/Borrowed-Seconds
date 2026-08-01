import math
import random
import struct
import wave
from pathlib import Path


SAMPLE_RATE = 48_000
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "AudioSource" / "Original"
CC0_DIR = Path(__file__).resolve().parents[1] / "AudioSource" / "External" / "CC0"


def envelope(t, attack, decay):
    if t < attack:
        return t / attack
    return math.exp(-(t - attack) / decay)


def write_wav(name, samples):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    peak = max(1.0, max(abs(sample) for sample in samples))
    pcm = bytearray()
    for sample in samples:
        value = int(max(-1.0, min(1.0, sample / peak)) * 32767)
        pcm.extend(struct.pack("<h", value))
    with wave.open(str(OUTPUT_DIR / name), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        output.writeframes(pcm)


def mechanical_tick(duration=0.22, pitch=880.0):
    rng = random.Random(17)
    result = []
    for index in range(int(duration * SAMPLE_RATE)):
        t = index / SAMPLE_RATE
        metal = (
            math.sin(2 * math.pi * pitch * t)
            + 0.55 * math.sin(2 * math.pi * pitch * 1.47 * t)
            + 0.28 * math.sin(2 * math.pi * pitch * 2.31 * t)
        )
        click = rng.uniform(-1.0, 1.0) * math.exp(-t / 0.012)
        body = math.sin(2 * math.pi * 92 * t) * math.exp(-t / 0.07)
        sample = 0.38 * metal * envelope(t, 0.0015, 0.055)
        sample += 0.26 * click + 0.18 * body
        result.append(sample)
    return result


def final_warning(duration=0.85):
    rng = random.Random(31)
    result = []
    for index in range(int(duration * SAMPLE_RATE)):
        t = index / SAMPLE_RATE
        downward_pitch = 310 - 105 * min(t / duration, 1.0)
        phase = 2 * math.pi * downward_pitch * t
        alarm = math.sin(phase) + 0.38 * math.sin(2.01 * phase)
        pulse = 0.65 + 0.35 * math.sin(2 * math.pi * 7.5 * t)
        impact = math.sin(2 * math.pi * 58 * t) * math.exp(-t / 0.24)
        grit = rng.uniform(-1.0, 1.0) * math.exp(-t / 0.09)
        fade = min(1.0, t / 0.008) * min(1.0, (duration - t) / 0.12)
        result.append((0.42 * alarm * pulse + 0.32 * impact + 0.08 * grit) * fade)
    return result


def mix_at(destination, source, start_seconds, gain=1.0):
    start = int(start_seconds * SAMPLE_RATE)
    for index, sample in enumerate(source):
        if start + index < len(destination):
            destination[start + index] += sample * gain


def read_recorded_wav(path):
    with wave.open(str(path), "rb") as source:
        if source.getnchannels() != 1 or source.getsampwidth() != 2:
            raise ValueError(f"Expected mono 16-bit WAV: {path}")
        rate = source.getframerate()
        frames = source.readframes(source.getnframes())
    source_samples = [value[0] / 32768.0 for value in struct.iter_unpack("<h", frames)]
    peak = max(abs(value) for value in source_samples)
    threshold = peak * 0.035
    active = [i for i, value in enumerate(source_samples) if abs(value) >= threshold]
    if active:
        padding = int(rate * 0.008)
        source_samples = source_samples[max(0, active[0] - padding):min(len(source_samples), active[-1] + padding)]
    output_length = max(1, round(len(source_samples) * SAMPLE_RATE / rate))
    resampled = []
    for output_index in range(output_length):
        position = output_index * rate / SAMPLE_RATE
        left = min(int(position), len(source_samples) - 1)
        right = min(left + 1, len(source_samples) - 1)
        fraction = position - left
        resampled.append(source_samples[left] * (1.0 - fraction) + source_samples[right] * fraction)
    normalize = 0.88 / max(0.001, max(abs(value) for value in resampled))
    return [value * normalize for value in resampled]


tick = mechanical_tick()
warning = final_warning()
write_wav("SFX_Countdown_Tick.wav", tick)
write_wav("SFX_Countdown_Final.wav", warning)

preview = [0.0] * int(5.8 * SAMPLE_RATE)
for moment, gain, pitch in [
    (0.35, 0.70, 760),
    (1.35, 0.76, 820),
    (2.25, 0.82, 880),
    (3.05, 0.90, 960),
    (3.72, 1.00, 1060),
]:
    mix_at(preview, mechanical_tick(pitch=pitch), moment, gain)
mix_at(preview, warning, 4.55, 0.95)
write_wav("PREVIEW_Countdown_Sequence.wav", preview)


def clock_strike(kind="tick", duration=0.16):
    rng = random.Random(101 if kind == "tick" else 202)
    base = 1780.0 if kind == "tick" else 1180.0
    body_frequency = 145.0 if kind == "tick" else 112.0
    result = []
    for index in range(int(duration * SAMPLE_RATE)):
        t = index / SAMPLE_RATE
        transient = rng.uniform(-1.0, 1.0) * math.exp(-t / 0.0045)
        escapement = math.sin(2 * math.pi * base * t) * math.exp(-t / 0.024)
        metal = math.sin(2 * math.pi * base * 1.63 * t) * math.exp(-t / 0.039)
        body = math.sin(2 * math.pi * body_frequency * t) * math.exp(-t / 0.052)
        result.append(0.34 * transient + 0.48 * escapement + 0.21 * metal + 0.16 * body)
    return result


def dying_battery(duration=1.65):
    rng = random.Random(404)
    result = []
    phase = 0.0
    for index in range(int(duration * SAMPLE_RATE)):
        t = index / SAMPLE_RATE
        progress = t / duration
        wobble = 1.0 + 0.055 * math.sin(2 * math.pi * (4.0 + 10.0 * progress) * t)
        frequency = (510.0 - 420.0 * progress ** 0.72) * wobble
        phase += 2 * math.pi * frequency / SAMPLE_RATE
        power = (1.0 - progress) ** 1.15
        dropout_wave = math.sin(2 * math.pi * (7.0 + 18.0 * progress) * t)
        dropout = 1.0 if dropout_wave > (-0.92 + 0.74 * progress) else 0.08
        tone = math.sin(phase) + 0.31 * math.sin(2.03 * phase)
        buzz = math.sin(2 * math.pi * 61.0 * t) * (1.0 - progress)
        static = rng.uniform(-1.0, 1.0) * (0.025 + 0.07 * progress)
        result.append((0.43 * tone * dropout + 0.16 * buzz + static) * power)
    return result


tick_clock = clock_strike("tick")
tock_clock = clock_strike("tock")
battery_end = dying_battery()
write_wav("SFX_Countdown_ClockTick_V2.wav", tick_clock)
write_wav("SFX_Countdown_ClockTock_V2.wav", tock_clock)
write_wav("SFX_Countdown_BatteryDie_V2.wav", battery_end)

clock_preview = [0.0] * int(6.1 * SAMPLE_RATE)
clock_events = [
    (0.30, "tick"),
    (1.00, "tock"),
    (1.64, "tick"),
    (2.22, "tock"),
    (2.73, "tick"),
    (3.17, "tock"),
    (3.54, "tick"),
    (3.85, "tock"),
    (4.11, "tick"),
    (4.32, "tock"),
]
for moment, kind in clock_events:
    gain = 0.72 + 0.25 * (moment / 4.32)
    mix_at(clock_preview, tick_clock if kind == "tick" else tock_clock, moment, gain)
mix_at(clock_preview, battery_end, 4.50, 0.95)
write_wav("PREVIEW_Countdown_ClockBattery_V2.wav", clock_preview)


def dry_clock_tick(kind="tick", duration=0.115):
    rng = random.Random(707 if kind == "tick" else 808)
    main_frequency = 720.0 if kind == "tick" else 510.0
    result = []
    for index in range(int(duration * SAMPLE_RATE)):
        t = index / SAMPLE_RATE
        sharp_click = rng.uniform(-1.0, 1.0) * math.exp(-t / 0.0024)
        wood = math.sin(2 * math.pi * main_frequency * t) * math.exp(-t / 0.017)
        case = math.sin(2 * math.pi * (205 if kind == "tick" else 168) * t) * math.exp(-t / 0.026)
        soft_tail = rng.uniform(-1.0, 1.0) * math.exp(-t / 0.014)
        result.append(0.24 * sharp_click + 0.42 * wood + 0.23 * case + 0.045 * soft_tail)
    return result


dry_tick = dry_clock_tick("tick")
dry_tock = dry_clock_tick("tock")
write_wav("SFX_Countdown_DryTick_V3.wav", dry_tick)
write_wav("SFX_Countdown_DryTock_V3.wav", dry_tock)

dry_preview = [0.0] * int(6.1 * SAMPLE_RATE)
for moment, kind in clock_events:
    gain = 0.76 + 0.20 * (moment / 4.32)
    mix_at(dry_preview, dry_tick if kind == "tick" else dry_tock, moment, gain)
mix_at(dry_preview, battery_end, 4.50, 0.95)
write_wav("PREVIEW_Countdown_DryClockBattery_V3.wav", dry_preview)


recorded_tick = read_recorded_wav(CC0_DIR / "OGA_Tick.wav")
recorded_tock = read_recorded_wav(CC0_DIR / "OGA_Tock.wav")
cc0_preview = [0.0] * int(6.1 * SAMPLE_RATE)
for moment, kind in clock_events:
    gain = 0.72 + 0.20 * (moment / 4.32)
    mix_at(cc0_preview, recorded_tick if kind == "tick" else recorded_tock, moment, gain)
mix_at(cc0_preview, battery_end, 4.50, 0.95)
write_wav("PREVIEW_Countdown_CC0ClockBattery_V4.wav", cc0_preview)
