"""
Visualization module for DSAL toolkit.

This module provides plotting functions to visualize audio waveforms,
amplitude envelopes, and pause segment classifications.
"""

from typing import List, Dict, Any

import matplotlib.pyplot as plt
import numpy as np


def plot_analysis(
    y: np.ndarray,
    sr: int,
    envelope: np.ndarray,
    segments: List[Dict[str, Any]],
    figsize: tuple = (12, 6),
    show_waveform: bool = True,
    show_envelope: bool = True,
    alpha: float = 0.3,
) -> plt.Figure:
    """
    Plot waveform, envelope, and colored pause segments.

    Parameters
    ----------
    y:
        Mono audio signal (1D array).
    sr:
        Sample rate in Hz.
    envelope:
        Smoothed amplitude envelope, same length as `y`.
    segments:
        List of pause segment dictionaries, each with keys:
        - 'start': start time in seconds
        - 'end': end time in seconds
        - 'type': 'breath' or 'pathological'
    figsize:
        Figure size tuple (width, height) in inches. Default: (12, 6).
    show_waveform:
        Whether to display the waveform. Default: True.
    show_envelope:
        Whether to display the envelope. Default: True.
    alpha:
        Transparency of the colored pause regions (0-1). Default: 0.3.

    Returns
    -------
    fig:
        matplotlib.figure.Figure object (suitable for Streamlit integration).
    """
    if y.ndim != 1:
        raise ValueError("Audio signal `y` must be a 1D array.")
    if envelope.ndim != 1:
        raise ValueError("Envelope must be a 1D array.")
    if len(y) != len(envelope):
        raise ValueError("Audio `y` and envelope must have the same length.")
    if sr <= 0:
        raise ValueError("Sample rate `sr` must be positive.")

    # Create time axis in seconds
    duration = len(y) / sr
    t = np.arange(len(y)) / sr

    # Normalize for display (optional, but helps visualization)
    y_norm = y / (np.abs(y).max() + 1e-9)
    envelope_norm = envelope / (envelope.max() + 1e-9)

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Plot waveform in light gray (if enabled)
    if show_waveform:
        ax.plot(t, y_norm, color="lightgray", alpha=0.6, linewidth=0.5, label="Waveform")

    # Overlay envelope in black (if enabled)
    if show_envelope:
        ax.plot(t, envelope_norm, color="black", linewidth=1.0, label="Envelope")

    # Highlight pause segments with colored regions
    breath_labeled = False
    pathological_labeled = False
    
    for seg in segments:
        start = seg["start"]
        end = seg["end"]
        seg_type = seg.get("type", "unknown")

        if seg_type == "breath":
            # Green area for breath pauses
            label = "Breath" if not breath_labeled else ""
            ax.axvspan(start, end, alpha=alpha, color="green", label=label)
            breath_labeled = True
        elif seg_type == "pathological":
            # Red area for pathological blocks
            label = "Pathological Block" if not pathological_labeled else ""
            ax.axvspan(start, end, alpha=alpha, color="red", label=label)
            pathological_labeled = True

    ax.legend(loc="upper right")

    ax.set_xlabel("Time (seconds)", fontsize=11)
    ax.set_ylabel("Amplitude (normalized)", fontsize=11)
    ax.set_title("Speech Analysis: Waveform, Envelope, and Pause Classification", fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, duration)

    plt.tight_layout()
    return fig
