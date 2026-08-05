"""Create smoother Unreal-ready door WAVs from the licensed gate recording."""

from __future__ import annotations

import struct
import wave
from pathlib import Path

import numpy as np
import soundfile as sf


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "AudioSource" / "External" / "CC0" / "Pixabay_103288_GateHeavyOpenClose.mp3"
OUT = ROOT / "AudioSource" / "Original" / "Door" / "RecordedGate"
TARGET_RATE = 48_000


def extract(source: np.ndarray, source_rate: int, start: float, end: float) -> np.ndarray:
    segment = source[int(start * source_rate):int(end * source_rate)].copy()

    # A broad, gentle high-frequency reduction removes the abrasive drill-like edge
    # while retaining the gate's chain, creak, and impact character.
    spectrum = np.fft.rfft(segment)
    frequencies = np.fft.rfftfreq(len(segment), 1.0 / source_rate)
    shelf = np.ones_like(frequencies)
    transition = np.clip((frequencies - 3_500.0) / 5_500.0, 0.0, 1.0)
    shelf *= 1.0 - 0.62 * transition
    segment = np.fft.irfft(spectrum * shelf, n=len(segment))

    # Keep dynamics but bring the source down to a comfortable SFX level.
    rms = float(np.sqrt(np.mean(segment * segment))) or 1.0
    segment *= min((10.0 ** (-18.0 / 20.0)) / rms, 1.0)
    peak = float(np.max(np.abs(segment))) or 1.0
    if peak > 0.68:
        segment *= 0.68 / peak

    # Gentle start/end fades prevent edit clicks and make the movement smoother.
    fade_in = min(int(0.045 * source_rate), len(segment))
    fade_out = min(int(0.12 * source_rate), len(segment))
    segment[:fade_in] *= np.linspace(0.0, 1.0, fade_in)
    segment[-fade_out:] *= np.linspace(1.0, 0.0, fade_out)

    # The Pixabay file is 24 kHz; export at the project's standard 48 kHz.
    target_length = round(len(segment) * TARGET_RATE / source_rate)
    old_positions = np.arange(len(segment), dtype=np.float64)
    new_positions = np.linspace(0.0, len(segment) - 1.0, target_length)
    return np.interp(new_positions, old_positions, segment).astype(np.float32)


def write_wav(path: Path, samples: np.ndarray) -> None:
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

    opening = extract(mono, source_rate, 0.15, 2.65)
    closing = extract(mono, source_rate, 3.45, 5.95)

    write_wav(OUT / "SFX_Door_Open_Recorded_Smooth.wav", opening)
    write_wav(OUT / "SFX_Door_Close_Recorded_Smooth.wav", closing)

    gap = np.zeros(int(0.7 * TARGET_RATE), dtype=np.float32)
    write_wav(OUT / "PREVIEW_DoorRecordedSmooth.wav", np.concatenate((opening, gap, closing)))


if __name__ == "__main__":
    main()
