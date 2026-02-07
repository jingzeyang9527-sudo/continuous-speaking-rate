from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

import numpy as np


@dataclass
class PauseAnalyzer:
    """
    Analyze pauses in speech based on an amplitude envelope and classify them
    as physiological breaths vs. pathological blocks.

    This implements Step 2 of the DSAL spec:
    1. Adaptive threshold using the quietest 10% of envelope samples.
    2. Segmentation of regions where envelope < threshold.
    3. For each segment, compute
       - Zero Crossing Rate (ZCR) on the corresponding audio samples.
       - Local energy.
    4. Classification rule:
       - IF ZCR > zcr_threshold AND Energy > noise_floor * 1.1 -> \"breath\"
       - ELSE -> \"pathological\"
    """

    zcr_threshold: float = 0.05
    min_pause_duration: float = 0.15  # seconds; ignore very short gaps

    def _adaptive_threshold(
        self, envelope: np.ndarray, y: np.ndarray
    ) -> Tuple[float, float]:
        """
        Estimate background noise level from the quietest 10% of the envelope.

        Returns
        -------
        envelope_floor:
            Mean envelope value among the quietest samples.
        energy_floor:
            Mean squared amplitude (energy) of audio samples at those indices.
        """
        if envelope.ndim != 1:
            raise ValueError("Envelope must be a 1D array.")
        if y.ndim != 1:
            raise ValueError("Audio signal `y` must be a 1D array.")
        if len(envelope) != len(y):
            raise ValueError("Envelope and audio `y` must have the same length.")

        n = len(envelope)
        if n == 0:
            raise ValueError("Empty envelope provided.")

        quiet_count = max(1, int(0.1 * n))
        # Indices of the quietest 10% envelope values
        quiet_indices = np.argpartition(envelope, quiet_count - 1)[:quiet_count]

        envelope_floor = float(np.mean(envelope[quiet_indices]))
        energy_floor = float(np.mean(y[quiet_indices] ** 2))
        return envelope_floor, energy_floor

    def _find_silent_segments(
        self, silent_mask: np.ndarray, sr: int
    ) -> List[Tuple[int, int]]:
        """
        Convert a boolean mask of silent samples into contiguous [start, end) indices.
        """
        if silent_mask.ndim != 1:
            raise ValueError("silent_mask must be a 1D boolean array.")

        segments: List[Tuple[int, int]] = []
        n = len(silent_mask)
        in_segment = False
        start = 0

        for i, is_silent in enumerate(silent_mask):
            if is_silent and not in_segment:
                in_segment = True
                start = i
            elif not is_silent and in_segment:
                in_segment = False
                end = i
                segments.append((start, end))

        # If we ended in a silent region, close it at the end of the signal
        if in_segment:
            segments.append((start, n))

        # Filter by minimum duration
        min_samples = int(self.min_pause_duration * sr)
        segments = [(s, e) for (s, e) in segments if (e - s) >= min_samples]
        return segments

    @staticmethod
    def _zero_crossing_rate(segment: np.ndarray) -> float:
        """
        Compute zero crossing rate of a 1D audio segment.
        """
        if len(segment) < 2:
            return 0.0

        signs = np.signbit(segment)
        crossings = np.logical_xor(signs[1:], signs[:-1])
        return float(np.mean(crossings))

    @staticmethod
    def _local_energy(segment: np.ndarray) -> float:
        """
        Compute mean squared amplitude (energy) of a segment.
        """
        if segment.size == 0:
            return 0.0
        return float(np.mean(segment ** 2))

    def analyze(
        self, y: np.ndarray, sr: int, envelope: np.ndarray
    ) -> List[Dict[str, Any]]:
        """
        Run pause detection and classification.

        Parameters
        ----------
        y:
            Mono audio signal.
        sr:
            Sample rate in Hz.
        envelope:
            Smoothed amplitude envelope of `y`, same length.

        Returns
        -------
        segments:
            List of dictionaries, e.g.:
            [
              {
                'start': 1.2,
                'end': 1.8,
                'type': 'breath',
                'zcr': 0.07,
                'energy': 1.2e-4
              },
              ...
            ]
        """
        if sr <= 0:
            raise ValueError("Sample rate `sr` must be positive.")

        envelope_floor, energy_floor = self._adaptive_threshold(envelope, y)

        # Use a slightly conservative threshold relative to the estimated floor
        threshold = envelope_floor
        silent_mask = envelope < threshold

        raw_segments = self._find_silent_segments(silent_mask, sr)

        results: List[Dict[str, Any]] = []
        for start_idx, end_idx in raw_segments:
            segment_y = y[start_idx:end_idx]
            if segment_y.size == 0:
                continue

            zcr = self._zero_crossing_rate(segment_y)
            energy = self._local_energy(segment_y)

            if zcr > self.zcr_threshold and energy > energy_floor * 1.1:
                label = "breath"
            else:
                label = "pathological"

            start_time = start_idx / sr
            end_time = end_idx / sr

            results.append(
                {
                    "start": start_time,
                    "end": end_time,
                    "type": label,
                    "zcr": zcr,
                    "energy": energy,
                }
            )

        return results

