from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Optional

import librosa
import numpy as np
from scipy.signal import butter, filtfilt, hilbert


@dataclass
class AudioPreprocessor:
    """
    AudioPreprocessor handles low-level audio loading and extraction of
    a smoothed amplitude envelope using the Hilbert transform.

    This implements the functionality described in Step 1 of the DSAL spec:
    - Load audio, resample to 16 kHz and convert to mono
    - Compute the Hilbert envelope
    - Apply a 4th-order low-pass Butterworth filter (cutoff = 50 Hz)
      to smooth the envelope
    """

    target_sr: int = 16000

    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        Load an audio file, resampled to `target_sr` and converted to mono.

        Parameters
        ----------
        file_path:
            Path to an audio file (e.g. .wav).

        Returns
        -------
        y:
            1D numpy array containing the mono audio samples.
        sr:
            Sample rate (should be `target_sr`).
        """
        y, sr = librosa.load(file_path, sr=self.target_sr, mono=True)

        # Ensure float64 for numerical stability in subsequent processing
        y = np.asarray(y, dtype=np.float64)
        return y, sr

    def get_envelope(self, y: np.ndarray, sr: Optional[int] = None) -> np.ndarray:
        """
        Compute a smoothed amplitude envelope for the given audio signal.

        Steps:
        1. Apply Hilbert transform to get the analytic signal.
        2. Take magnitude to obtain the raw amplitude envelope.
        3. Apply a low-pass Butterworth filter (order=4, cutoff=50 Hz)
           to smooth the envelope.

        Parameters
        ----------
        y:
            1D audio signal (mono).
        sr:
            Sample rate of the signal. If None, falls back to `target_sr`.

        Returns
        -------
        envelope_smooth:
            Smoothed amplitude envelope, same shape as `y`.
        """
        if y.ndim != 1:
            raise ValueError("Input audio `y` must be a 1D (mono) signal.")

        if sr is None:
            sr = self.target_sr

        # Hilbert transform -> analytic signal
        analytic = hilbert(y)
        amplitude_envelope = np.abs(analytic)

        # Design low-pass Butterworth filter
        cutoff_hz = 50.0
        nyquist = 0.5 * sr
        if cutoff_hz >= nyquist:
            raise ValueError(
                f"Cutoff frequency ({cutoff_hz} Hz) must be below Nyquist ({nyquist} Hz)."
            )

        normal_cutoff = cutoff_hz / nyquist
        b, a = butter(N=4, Wn=normal_cutoff, btype="low", analog=False)

        # Zero-phase filtering to avoid phase distortion
        envelope_smooth = filtfilt(b, a, amplitude_envelope)

        return envelope_smooth

    def process(self, file_path: str) -> Tuple[np.ndarray, int, np.ndarray]:
        """
        Convenience method: load an audio file and compute its smoothed envelope.

        This matches the spec's Step 1 output:
        Returns raw audio `y`, sample rate `sr`, and smoothed `envelope`.

        Parameters
        ----------
        file_path:
            Path to an audio file.

        Returns
        -------
        y:
            Mono audio signal.
        sr:
            Sample rate of the returned signal.
        envelope:
            Smoothed amplitude envelope.
        """
        y, sr = self.load_audio(file_path)
        envelope = self.get_envelope(y, sr=sr)
        return y, sr, envelope

