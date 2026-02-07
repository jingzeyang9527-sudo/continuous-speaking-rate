"""
Feature extraction module for DSAL toolkit.

This module provides functions to extract speaking rate, articulation rate,
and prosody features (F0, jitter, shimmer, intensity) from audio signals.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import librosa
from scipy import signal


def calculate_speaking_rate(
    y: np.ndarray,
    sr: int,
    envelope: np.ndarray,
    threshold_factor: float = 0.1,
) -> Dict[str, float]:
    """
    Calculate speaking rate metrics.

    Speaking rate is typically defined as:
    - Speech duration / Total duration (proportion of time spent speaking)
    - Or: syllables per minute (if syllable count is available)

    Parameters
    ----------
    y:
        Mono audio signal (1D array).
    sr:
        Sample rate in Hz.
    envelope:
        Smoothed amplitude envelope, same length as `y`.
    threshold_factor:
        Factor to determine speech vs silence threshold (relative to envelope mean).

    Returns
    -------
    metrics:
        Dictionary with:
        - 'speaking_rate': proportion of time with speech (0-1)
        - 'speech_duration': total duration of speech segments in seconds
        - 'total_duration': total audio duration in seconds
    """
    if y.ndim != 1:
        raise ValueError("Audio signal `y` must be a 1D array.")
    if envelope.ndim != 1:
        raise ValueError("Envelope must be a 1D array.")
    if len(y) != len(envelope):
        raise ValueError("Audio `y` and envelope must have the same length.")

    total_duration = len(y) / sr

    # Estimate speech threshold from envelope
    # Use a threshold based on envelope statistics
    envelope_mean = np.mean(envelope)
    envelope_std = np.std(envelope)
    threshold = envelope_mean * threshold_factor + envelope_std * 0.1

    # Identify speech regions (where envelope > threshold)
    speech_mask = envelope > threshold
    speech_samples = np.sum(speech_mask)
    speech_duration = speech_samples / sr

    speaking_rate = speech_duration / total_duration if total_duration > 0 else 0.0

    return {
        "speaking_rate": speaking_rate,
        "speech_duration": speech_duration,
        "total_duration": total_duration,
    }


def calculate_articulation_rate(
    y: np.ndarray,
    sr: int,
    segments: List[Dict[str, Any]],
    total_duration: float,
) -> Dict[str, float]:
    """
    Calculate articulation rate metrics.

    Articulation rate is typically defined as:
    - Speech duration / (Total duration - Pause duration)
    - Or: syllables per minute of actual speech time (excluding pauses)

    Parameters
    ----------
    y:
        Mono audio signal (1D array).
    sr:
        Sample rate in Hz.
    segments:
        List of pause segment dictionaries with 'start', 'end' keys.
    total_duration:
        Total audio duration in seconds.

    Returns
    -------
    metrics:
        Dictionary with:
        - 'articulation_rate': speech duration / (total - pause duration)
        - 'speech_duration': total duration minus all pause durations
        - 'pause_duration': total duration of all pauses
        - 'net_speech_duration': total - pause duration
    """
    if total_duration <= 0:
        return {
            "articulation_rate": 0.0,
            "speech_duration": 0.0,
            "pause_duration": 0.0,
            "net_speech_duration": 0.0,
        }

    # Calculate total pause duration
    pause_duration = sum(seg["end"] - seg["start"] for seg in segments)
    net_speech_duration = total_duration - pause_duration

    # Articulation rate: how much of the non-pause time is actual speech
    # For simplicity, we use: net_speech_duration / total_duration
    # (This assumes pauses are correctly identified)
    articulation_rate = (
        net_speech_duration / total_duration if total_duration > 0 else 0.0
    )

    return {
        "articulation_rate": articulation_rate,
        "speech_duration": net_speech_duration,
        "pause_duration": pause_duration,
        "net_speech_duration": net_speech_duration,
    }


def extract_f0(
    y: np.ndarray,
    sr: int,
    fmin: float = 75.0,
    fmax: float = 600.0,
    frame_length: int = 2048,
    hop_length: int = 512,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extract fundamental frequency (F0) contour using librosa's pyin algorithm.

    Parameters
    ----------
    y:
        Mono audio signal (1D array).
    sr:
        Sample rate in Hz.
    fmin:
        Minimum frequency for F0 estimation (Hz). Default: 75 Hz.
    fmax:
        Maximum frequency for F0 estimation (Hz). Default: 600 Hz.
    frame_length:
        Frame length for F0 estimation. Default: 2048.
    hop_length:
        Hop length for F0 estimation. Default: 512.

    Returns
    -------
    f0:
        F0 contour (Hz), same length as number of frames.
    voiced_mask:
        Boolean mask indicating which frames are voiced (non-zero F0).
    """
    if y.ndim != 1:
        raise ValueError("Audio signal `y` must be a 1D array.")

    # Use librosa's pyin for robust F0 estimation
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y,
        fmin=fmin,
        fmax=fmax,
        frame_length=frame_length,
        hop_length=hop_length,
        sr=sr,
    )

    # Convert NaN to 0 for unvoiced frames
    f0 = np.nan_to_num(f0, nan=0.0)
    voiced_mask = voiced_flag.astype(bool)

    return f0, voiced_mask


def calculate_f0_statistics(f0: np.ndarray, voiced_mask: np.ndarray) -> Dict[str, float]:
    """
    Calculate F0 statistics (mean, std, range, variability).

    Parameters
    ----------
    f0:
        F0 contour (Hz).
    voiced_mask:
        Boolean mask indicating voiced frames.

    Returns
    -------
    stats:
        Dictionary with F0 statistics:
        - 'f0_mean': mean F0 (Hz)
        - 'f0_std': standard deviation of F0 (Hz)
        - 'f0_min': minimum F0 (Hz)
        - 'f0_max': maximum F0 (Hz)
        - 'f0_range': F0 range (max - min, Hz)
        - 'f0_cv': coefficient of variation (std/mean)
        - 'voiced_ratio': proportion of voiced frames
    """
    voiced_f0 = f0[voiced_mask]

    if len(voiced_f0) == 0:
        return {
            "f0_mean": 0.0,
            "f0_std": 0.0,
            "f0_min": 0.0,
            "f0_max": 0.0,
            "f0_range": 0.0,
            "f0_cv": 0.0,
            "voiced_ratio": 0.0,
        }

    f0_mean = float(np.mean(voiced_f0))
    f0_std = float(np.std(voiced_f0))
    f0_min = float(np.min(voiced_f0))
    f0_max = float(np.max(voiced_f0))
    f0_range = f0_max - f0_min
    f0_cv = f0_std / f0_mean if f0_mean > 0 else 0.0
    voiced_ratio = float(np.mean(voiced_mask))

    return {
        "f0_mean": f0_mean,
        "f0_std": f0_std,
        "f0_min": f0_min,
        "f0_max": f0_max,
        "f0_range": f0_range,
        "f0_cv": f0_cv,
        "voiced_ratio": voiced_ratio,
    }


def calculate_jitter(
    f0: np.ndarray, voiced_mask: np.ndarray, period_unit: str = "period"
) -> Dict[str, float]:
    """
    Calculate jitter (F0 period-to-period variability).

    Jitter measures the cycle-to-cycle variation in fundamental frequency.
    Common measures:
    - Local Jitter: mean absolute difference between consecutive periods
    - Relative Average Perturbation (RAP)
    - Pitch Period Perturbation Quotient (PPQ)

    Parameters
    ----------
    f0:
        F0 contour (Hz).
    voiced_mask:
        Boolean mask indicating voiced frames.
    period_unit:
        Unit for jitter calculation ('period' or 'frequency').

    Returns
    -------
    jitter_metrics:
        Dictionary with:
        - 'jitter_local': local jitter (absolute difference between consecutive periods)
        - 'jitter_rap': Relative Average Perturbation
        - 'jitter_ppq5': Pitch Period Perturbation Quotient (5-point)
    """
    voiced_f0 = f0[voiced_mask]

    if len(voiced_f0) < 2:
        return {
            "jitter_local": 0.0,
            "jitter_rap": 0.0,
            "jitter_ppq5": 0.0,
        }

    # Convert F0 to periods (in samples, approximate)
    # For simplicity, we work with F0 values directly
    periods = 1.0 / (voiced_f0 + 1e-9)  # Avoid division by zero

    # Local jitter: mean absolute difference between consecutive periods
    period_diffs = np.abs(np.diff(periods))
    jitter_local = float(np.mean(period_diffs)) if len(period_diffs) > 0 else 0.0

    # RAP: average of absolute differences between a period and the average of it and its neighbors
    if len(periods) >= 3:
        rap_values = []
        for i in range(1, len(periods) - 1):
            local_avg = (periods[i - 1] + periods[i] + periods[i + 1]) / 3.0
            rap_values.append(abs(periods[i] - local_avg))
        jitter_rap = float(np.mean(rap_values)) if rap_values else 0.0
    else:
        jitter_rap = 0.0

    # PPQ5: average of absolute differences between a period and the average of it and 4 neighbors
    if len(periods) >= 5:
        ppq5_values = []
        for i in range(2, len(periods) - 2):
            local_avg = np.mean(periods[i - 2 : i + 3])
            ppq5_values.append(abs(periods[i] - local_avg))
        jitter_ppq5 = float(np.mean(ppq5_values)) if ppq5_values else 0.0
    else:
        jitter_ppq5 = 0.0

    return {
        "jitter_local": jitter_local,
        "jitter_rap": jitter_rap,
        "jitter_ppq5": jitter_ppq5,
    }


def calculate_shimmer(
    y: np.ndarray,
    sr: int,
    f0: np.ndarray,
    voiced_mask: np.ndarray,
    frame_length: int = 2048,
    hop_length: int = 512,
) -> Dict[str, float]:
    """
    Calculate shimmer (amplitude period-to-period variability).

    Shimmer measures the cycle-to-cycle variation in amplitude.
    Common measures:
    - Local Shimmer: mean absolute difference between consecutive amplitudes
    - Shimmer (dB)
    - Amplitude Perturbation Quotient (APQ)

    Parameters
    ----------
    y:
        Mono audio signal (1D array).
    sr:
        Sample rate in Hz.
    f0:
        F0 contour (Hz).
    voiced_mask:
        Boolean mask indicating voiced frames.
    frame_length:
        Frame length for amplitude extraction. Default: 2048.
    hop_length:
        Hop length for amplitude extraction. Default: 512.

    Returns
    -------
    shimmer_metrics:
        Dictionary with:
        - 'shimmer_local': local shimmer (absolute difference between consecutive amplitudes)
        - 'shimmer_db': shimmer in dB
        - 'shimmer_apq5': Amplitude Perturbation Quotient (5-point)
    """
    if y.ndim != 1:
        raise ValueError("Audio signal `y` must be a 1D array.")

    # Extract amplitude envelope per frame
    frames = librosa.util.frame(y, frame_length=frame_length, hop_length=hop_length)
    amplitudes = np.mean(np.abs(frames), axis=0)

    # Only use voiced frames
    voiced_amplitudes = amplitudes[voiced_mask[: len(amplitudes)]]

    if len(voiced_amplitudes) < 2:
        return {
            "shimmer_local": 0.0,
            "shimmer_db": 0.0,
            "shimmer_apq5": 0.0,
        }

    # Local shimmer: mean absolute difference between consecutive amplitudes
    amp_diffs = np.abs(np.diff(voiced_amplitudes))
    shimmer_local = float(np.mean(amp_diffs)) if len(amp_diffs) > 0 else 0.0

    # Shimmer in dB
    amp_db = 20 * np.log10(voiced_amplitudes + 1e-9)
    amp_db_diffs = np.abs(np.diff(amp_db))
    shimmer_db = float(np.mean(amp_db_diffs)) if len(amp_db_diffs) > 0 else 0.0

    # APQ5: average of absolute differences between an amplitude and the average of it and 4 neighbors
    if len(voiced_amplitudes) >= 5:
        apq5_values = []
        for i in range(2, len(voiced_amplitudes) - 2):
            local_avg = np.mean(voiced_amplitudes[i - 2 : i + 3])
            apq5_values.append(abs(voiced_amplitudes[i] - local_avg))
        shimmer_apq5 = float(np.mean(apq5_values)) if apq5_values else 0.0
    else:
        shimmer_apq5 = 0.0

    return {
        "shimmer_local": shimmer_local,
        "shimmer_db": shimmer_db,
        "shimmer_apq5": shimmer_apq5,
    }


def extract_intensity(
    y: np.ndarray,
    sr: int,
    frame_length: int = 2048,
    hop_length: int = 512,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extract intensity (RMS energy) contour.

    Parameters
    ----------
    y:
        Mono audio signal (1D array).
    sr:
        Sample rate in Hz.
    frame_length:
        Frame length for intensity extraction. Default: 2048.
    hop_length:
        Hop length for intensity extraction. Default: 512.

    Returns
    -------
    intensity:
        Intensity contour (RMS energy per frame).
    times:
        Time points for each frame (seconds).
    """
    if y.ndim != 1:
        raise ValueError("Audio signal `y` must be a 1D array.")

    # Extract RMS energy per frame
    frames = librosa.util.frame(y, frame_length=frame_length, hop_length=hop_length)
    intensity = np.sqrt(np.mean(frames ** 2, axis=0))

    # Time points
    times = librosa.frames_to_time(
        np.arange(len(intensity)), sr=sr, hop_length=hop_length
    )

    return intensity, times


def calculate_intensity_statistics(intensity: np.ndarray) -> Dict[str, float]:
    """
    Calculate intensity statistics.

    Parameters
    ----------
    intensity:
        Intensity contour (RMS energy per frame).

    Returns
    -------
    stats:
        Dictionary with intensity statistics:
        - 'intensity_mean': mean intensity
        - 'intensity_std': standard deviation
        - 'intensity_min': minimum intensity
        - 'intensity_max': maximum intensity
        - 'intensity_range': intensity range (max - min)
    """
    if len(intensity) == 0:
        return {
            "intensity_mean": 0.0,
            "intensity_std": 0.0,
            "intensity_min": 0.0,
            "intensity_max": 0.0,
            "intensity_range": 0.0,
        }

    return {
        "intensity_mean": float(np.mean(intensity)),
        "intensity_std": float(np.std(intensity)),
        "intensity_min": float(np.min(intensity)),
        "intensity_max": float(np.max(intensity)),
        "intensity_range": float(np.max(intensity) - np.min(intensity)),
    }


def extract_all_prosody_features(
    y: np.ndarray,
    sr: int,
    fmin: float = 75.0,
    fmax: float = 600.0,
) -> Dict[str, Any]:
    """
    Extract all prosody features (F0, jitter, shimmer, intensity) in one call.

    Parameters
    ----------
    y:
        Mono audio signal (1D array).
    sr:
        Sample rate in Hz.
    fmin:
        Minimum frequency for F0 estimation (Hz). Default: 75 Hz.
    fmax:
        Maximum frequency for F0 estimation (Hz). Default: 600 Hz.

    Returns
    -------
    features:
        Dictionary containing all prosody features:
        - F0 statistics (f0_mean, f0_std, f0_min, f0_max, f0_range, f0_cv, voiced_ratio)
        - Jitter metrics (jitter_local, jitter_rap, jitter_ppq5)
        - Shimmer metrics (shimmer_local, shimmer_db, shimmer_apq5)
        - Intensity statistics (intensity_mean, intensity_std, intensity_min, intensity_max, intensity_range)
    """
    # Extract F0
    f0, voiced_mask = extract_f0(y, sr, fmin=fmin, fmax=fmax)
    f0_stats = calculate_f0_statistics(f0, voiced_mask)

    # Calculate jitter
    jitter_metrics = calculate_jitter(f0, voiced_mask)

    # Calculate shimmer
    shimmer_metrics = calculate_shimmer(y, sr, f0, voiced_mask)

    # Extract intensity
    intensity, _ = extract_intensity(y, sr)
    intensity_stats = calculate_intensity_statistics(intensity)

    # Combine all features
    all_features = {
        **f0_stats,
        **jitter_metrics,
        **shimmer_metrics,
        **intensity_stats,
    }

    return all_features
