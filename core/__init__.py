"""
Core signal processing modules for the Disordered Speech Analysis Library (DSAL).

Currently exposes:
- AudioPreprocessor: loading audio and computing smoothed amplitude envelopes.
- PauseAnalyzer: pause segmentation and classification.
- plot_analysis: visualization of waveform, envelope, and pause segments.
- Feature extraction functions: speaking rate, articulation rate, prosody (F0, jitter, shimmer, intensity).
"""

from .preprocessor import AudioPreprocessor
from .dynamics import PauseAnalyzer
from .visualizer import plot_analysis
from .features import (
    calculate_speaking_rate,
    calculate_articulation_rate,
    extract_f0,
    calculate_f0_statistics,
    calculate_jitter,
    calculate_shimmer,
    extract_intensity,
    calculate_intensity_statistics,
    extract_all_prosody_features,
)

