"""
Utility functions for DSAL toolkit.

This module provides helper functions for metrics calculation, data export,
and other common operations.
"""

from typing import List, Dict, Any
import numpy as np
from core.features import (
    calculate_speaking_rate,
    calculate_articulation_rate,
    extract_all_prosody_features,
)


def calculate_metrics(segments: List[Dict[str, Any]], total_duration: float) -> Dict[str, float]:
    """
    Calculate Pathological Pause Rate and Breath Frequency from segments.

    Parameters
    ----------
    segments:
        List of segment dictionaries with 'start', 'end', 'type' keys.
    total_duration:
        Total audio duration in seconds.

    Returns
    -------
    metrics:
        Dictionary with:
        - 'pathological_pause_rate': proportion of audio duration (0-1)
        - 'breath_frequency': breaths per second
        - 'pathological_duration': total pathological pause duration in seconds
        - 'breath_count': number of breath pauses
        - 'total_pause_duration': total duration of all pauses
        - 'pause_rate': proportion of audio that is any type of pause
    """
    if total_duration <= 0:
        return {
            "pathological_pause_rate": 0.0,
            "breath_frequency": 0.0,
            "pathological_duration": 0.0,
            "breath_count": 0,
            "total_pause_duration": 0.0,
            "pause_rate": 0.0,
        }

    pathological_duration = 0.0
    breath_count = 0
    total_pause_duration = 0.0

    for seg in segments:
        duration = seg["end"] - seg["start"]
        total_pause_duration += duration
        seg_type = seg.get("type", "")

        if seg_type == "pathological":
            pathological_duration += duration
        elif seg_type == "breath":
            breath_count += 1

    pathological_pause_rate = pathological_duration / total_duration
    breath_frequency = breath_count / total_duration  # breaths per second
    pause_rate = total_pause_duration / total_duration

    return {
        "pathological_pause_rate": pathological_pause_rate,
        "breath_frequency": breath_frequency,
        "pathological_duration": pathological_duration,
        "breath_count": breath_count,
        "total_pause_duration": total_pause_duration,
        "pause_rate": pause_rate,
    }


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to a human-readable string.

    Parameters
    ----------
    seconds:
        Duration in seconds.

    Returns
    -------
    formatted:
        Formatted string (e.g., "1m 23.45s" or "45.67s").
    """
    if seconds < 60:
        return f"{seconds:.2f}s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.2f}s"


def calculate_all_metrics(
    y: np.ndarray,
    sr: int,
    envelope: np.ndarray,
    segments: List[Dict[str, Any]],
    total_duration: float,
) -> Dict[str, Any]:
    """
    Calculate all metrics: pause metrics, speaking rate, articulation rate, and prosody features.

    Parameters
    ----------
    y:
        Mono audio signal (1D array).
    sr:
        Sample rate in Hz.
    envelope:
        Smoothed amplitude envelope, same length as `y`.
    segments:
        List of pause segment dictionaries with 'start', 'end', 'type' keys.
    total_duration:
        Total audio duration in seconds.

    Returns
    -------
    all_metrics:
        Dictionary containing:
        - Pause metrics (from calculate_metrics)
        - Speaking rate metrics (from calculate_speaking_rate)
        - Articulation rate metrics (from calculate_articulation_rate)
        - Prosody features (from extract_all_prosody_features)
    """
    # Pause metrics
    pause_metrics = calculate_metrics(segments, total_duration)

    # Speaking rate
    speaking_rate_metrics = calculate_speaking_rate(y, sr, envelope)

    # Articulation rate
    articulation_rate_metrics = calculate_articulation_rate(
        y, sr, segments, total_duration
    )

    # Prosody features
    prosody_features = extract_all_prosody_features(y, sr)

    # Combine all
    all_metrics = {
        **pause_metrics,
        **speaking_rate_metrics,
        **articulation_rate_metrics,
        **prosody_features,
    }

    return all_metrics
