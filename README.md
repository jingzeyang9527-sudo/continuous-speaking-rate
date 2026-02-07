## Disordered Speech Analysis Library (DSAL)

Python research toolkit for analyzing speech from patients with Primary Progressive Aphasia (PPA), with a focus on distinguishing **physiological pauses (breathing)** from **pathological pauses (cognitive/motor blocks)**, and extracting comprehensive speech features including **speaking rate**, **articulation rate**, and **prosody features** (F0, jitter, shimmer, intensity).

This README documents the complete implementation:
- **Pause Analysis**: Segmentation and classification of pauses (breath vs pathological)
- **Speaking Rate & Articulation Rate**: Speech duration metrics
- **Prosody Features**: F0 (pitch), jitter, shimmer, intensity
- **Visualization**: Waveform, envelope, and pause regions
- **Streamlit Web UI**: Interactive interface with dataset integration

---

### 1. Project Structure

```text
dsal_toolkit/
├── core/
│   ├── __init__.py
│   ├── preprocessor.py      # AudioPreprocessor: loading + Hilbert envelope
│   ├── dynamics.py          # PauseAnalyzer: pause segmentation & classification
│   ├── features.py          # Speaking rate, articulation rate, prosody (F0, jitter, shimmer, intensity)
│   └── visualizer.py        # plot_analysis: waveform + colored pause regions
├── app/
│   └── main.py              # Streamlit Web UI (complete implementation)
├── utils/
│   └── helpers.py           # Metrics calculation and utilities
├── requirements.txt
└── README.md
```

---

### 2. Installation

From the `dsal_toolkit` directory:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 3. Step 1: AudioPreprocessor

The class `AudioPreprocessor` (in `core/preprocessor.py`) implements:

- **`load_audio(file_path)`**
  - Loads an audio file (e.g. `.wav`)
  - Resamples to 16 kHz
  - Converts to mono
  - Returns `y, sr`
- **`get_envelope(y, sr=None)`**
  - Computes analytic signal via **Hilbert transform**
  - Takes magnitude to get the amplitude envelope
  - Applies a **4th-order low-pass Butterworth** filter (cutoff = 50 Hz) to smooth the envelope
- **`process(file_path)`**
  - Convenience wrapper returning: raw `y`, sample rate `sr`, and smoothed `envelope`

---

### 4. How to Test Step 1 Locally

1. Prepare a `.wav` file (mono or stereo, any sample rate), for example:

   ```text
   /path/to/example.wav
   ```

2. From the `dsal_toolkit` directory, run Python and try:

   ```python
   from core.preprocessor import AudioPreprocessor

   audio_path = "/path/to/example.wav"  # 修改为你自己的文件路径

   pre = AudioPreprocessor(target_sr=16000)
   y, sr, envelope = pre.process(audio_path)

   print("Audio shape:", y.shape)
   print("Sample rate:", sr)
   print("Envelope shape:", envelope.shape)
   print("First 10 envelope values:", envelope[:10])
   ```

3. (Optional) Quickly visualize the envelope:

   ```python
   import matplotlib.pyplot as plt
   import numpy as np

   t = np.arange(len(y)) / sr
   plt.figure(figsize=(10, 4))
   plt.plot(t, y / (abs(y).max() + 1e-9), alpha=0.4, label="Waveform (normalized)")
   plt.plot(t, envelope / (envelope.max() + 1e-9), label="Smoothed envelope")
   plt.xlabel("Time (s)")
   plt.legend()
   plt.tight_layout()
   plt.show()
   ```

If this runs without errors and the envelope looks smooth and reasonable, **Step 1 is working**.

---

### 4. Step 2: PauseAnalyzer (Pause Segmentation & Classification)

`PauseAnalyzer` (in `core/dynamics.py`) takes the raw audio, sample rate and the smoothed envelope, and:

- Estimates background noise level from the quietest 10% envelope samples.
- Detects **silent segments** where `envelope < threshold`, ignoring very short gaps (`min_pause_duration`, default 0.15 s).
- For each segment, computes:
  - **ZCR (Zero Crossing Rate)** on the corresponding audio samples.
  - **Local energy** (mean squared amplitude).
- Applies the rule:
  - IF `ZCR > zcr_threshold` (default 0.05) **AND** `Energy > noise_floor * 1.1` → label as **`"breath"`**
  - ELSE → label as **`"pathological"`**

Usage example:

```python
from core.preprocessor import AudioPreprocessor
from core.dynamics import PauseAnalyzer

audio_path = "/path/to/example.wav"

pre = AudioPreprocessor(target_sr=16000)
y, sr, envelope = pre.process(audio_path)

analyzer = PauseAnalyzer(zcr_threshold=0.05, min_pause_duration=0.15)
segments = analyzer.analyze(y, sr, envelope)

for seg in segments:
    print(seg)
    # e.g. {'start': 1.2, 'end': 1.8, 'type': 'breath', 'zcr': 0.07, 'energy': 1.2e-4}
```

The `segments` list matches the spec format:

```python
[{'start': 1.2, 'end': 1.8, 'type': 'breath'},
 {'start': 4.5, 'end': 6.0, 'type': 'pathological'}, ...]
```

You can ignore the extra diagnostic keys (`zcr`, `energy`) if not needed.

---

### 5. Step 3: Visualization (`core/visualizer.py`)

The `plot_analysis` function creates a matplotlib figure showing:

- **Waveform** (light gray, normalized)
- **Envelope** (black line)
- **Colored regions**:
  - **Green**: segments classified as `"breath"`
  - **Red**: segments classified as `"pathological"`

The function returns a `matplotlib.figure.Figure` object, which can be:
- Displayed in Jupyter notebooks
- Saved to file with `fig.savefig("output.png")`
- Integrated into Streamlit with `st.pyplot(fig)`

Usage example:

```python
from core.preprocessor import AudioPreprocessor
from core.dynamics import PauseAnalyzer
from core.visualizer import plot_analysis
import matplotlib.pyplot as plt

audio_path = "/path/to/example.wav"

# Step 1: Preprocess
pre = AudioPreprocessor(target_sr=16000)
y, sr, envelope = pre.process(audio_path)

# Step 2: Analyze pauses
analyzer = PauseAnalyzer(zcr_threshold=0.05, min_pause_duration=0.15)
segments = analyzer.analyze(y, sr, envelope)

# Step 3: Visualize
fig = plot_analysis(y, sr, envelope, segments, figsize=(12, 6))
plt.show()  # or fig.savefig("analysis.png")
```

---

### 6. Step 4: Streamlit Web UI (`app/main.py`)

The Streamlit application provides a user-friendly web interface for the complete analysis pipeline.

**Features:**
- 📁 **File Uploader**: Upload `.wav` files (mono or stereo, any sample rate)
- 🎵 **Audio Player**: Listen to uploaded files directly in the browser
- ⚙️ **Adjustable Parameters**: 
  - ZCR Threshold (slider: 0.01 - 0.20)
  - Minimum Pause Duration (slider: 0.05 - 1.0 seconds)
  - Advanced options (audio player toggle, result caching)
- 📊 **Metrics Display**:
  - **Pathological Pause Rate**: (Total duration of red blocks / Total audio duration)
  - **Breath Frequency**: (Count of green blocks / Total duration)
  - Additional diagnostic metrics (pathological duration, breath count, total pause rate)
- 📈 **Interactive Visualization**: Waveform, envelope, and colored pause regions
- 📋 **Detailed Segment List**: Expandable table with all detected segments and statistics
- 💾 **Export Functionality**: Download segment data as CSV
- ⚡ **Performance Optimizations**:
  - Result caching to avoid reprocessing
  - Progress bars for real-time feedback
  - Improved error handling with helpful tips

**How to Run:**

1. Make sure you're in the `dsal_toolkit` directory and dependencies are installed:
   ```bash
   cd /data/jingzeyang/dsal_toolkit
   source .venv/bin/activate  # if using venv
   pip install -r requirements.txt
   ```

2. Launch the Streamlit app:
   ```bash
   streamlit run app/main.py
   ```

3. The app will open in your default web browser (usually at `http://localhost:8501`)

4. Upload a `.wav` file, adjust parameters if needed, and click "🔍 Analyze"

**Usage Tips:**
- The app automatically resamples audio to 16 kHz and converts to mono
- Larger files may take a few seconds to process
- You can adjust the ZCR threshold and minimum pause duration in the sidebar to fine-tune classification
- The detailed segment list shows start/end times, duration, type, ZCR, and energy for each detected pause
- **Audio Player**: Enable in Advanced Options to listen to your uploaded file
- **Caching**: Enable result caching to avoid reprocessing when adjusting visualization settings
- **Export**: Download segment data as CSV for further analysis
- **Progress Tracking**: Real-time progress bars show analysis status

---

### 7. Speaking Rate, Articulation Rate, and Prosody Features

The toolkit now includes comprehensive feature extraction for speech analysis:

#### 7.1 Speaking Rate

**Speaking Rate** measures the proportion of time spent speaking:
- `speaking_rate`: Speech duration / Total duration (0-1)
- `speech_duration`: Total duration of speech segments (seconds)

```python
from core.features import calculate_speaking_rate
from core.preprocessor import AudioPreprocessor

pre = AudioPreprocessor(target_sr=16000)
y, sr, envelope = pre.process("audio.wav")

sr_metrics = calculate_speaking_rate(y, sr, envelope)
print(f"Speaking Rate: {sr_metrics['speaking_rate']:.1%}")
```

#### 7.2 Articulation Rate

**Articulation Rate** measures speech rate excluding pauses:
- `articulation_rate`: Net speech duration / Total duration
- `net_speech_duration`: Total duration minus all pause durations

```python
from core.features import calculate_articulation_rate
from core.dynamics import PauseAnalyzer

analyzer = PauseAnalyzer()
segments = analyzer.analyze(y, sr, envelope)
total_duration = len(y) / sr

ar_metrics = calculate_articulation_rate(y, sr, segments, total_duration)
print(f"Articulation Rate: {ar_metrics['articulation_rate']:.1%}")
```

#### 7.3 Prosody Features

**Prosody features** include:

- **F0 (Fundamental Frequency / Pitch)**:
  - `f0_mean`, `f0_std`, `f0_min`, `f0_max`, `f0_range`
  - `f0_cv`: Coefficient of variation (std/mean)
  - `voiced_ratio`: Proportion of voiced frames

- **Jitter** (F0 period-to-period variability):
  - `jitter_local`: Local jitter
  - `jitter_rap`: Relative Average Perturbation
  - `jitter_ppq5`: Pitch Period Perturbation Quotient (5-point)

- **Shimmer** (Amplitude period-to-period variability):
  - `shimmer_local`: Local shimmer
  - `shimmer_db`: Shimmer in dB
  - `shimmer_apq5`: Amplitude Perturbation Quotient (5-point)

- **Intensity** (RMS energy):
  - `intensity_mean`, `intensity_std`, `intensity_min`, `intensity_max`, `intensity_range`

```python
from core.features import extract_all_prosody_features

prosody = extract_all_prosody_features(y, sr)
print(f"F0 Mean: {prosody['f0_mean']:.1f} Hz")
print(f"Jitter (Local): {prosody['jitter_local']:.6f}")
print(f"Shimmer (dB): {prosody['shimmer_db']:.3f} dB")
```

#### 7.4 All Features at Once

Use `calculate_all_metrics` to extract everything in one call:

```python
from utils.helpers import calculate_all_metrics

all_metrics = calculate_all_metrics(y, sr, envelope, segments, total_duration)
# Contains: pause metrics, speaking rate, articulation rate, and all prosody features
```

---

### 8. Complete Pipeline Example (Command Line)

For programmatic use or batch processing, you can use the core modules directly:

```python
from core.preprocessor import AudioPreprocessor
from core.dynamics import PauseAnalyzer
from core.visualizer import plot_analysis
from utils.helpers import calculate_all_metrics
import matplotlib.pyplot as plt

# Process a single file
audio_path = "/path/to/ppa_recording.wav"

pre = AudioPreprocessor(target_sr=16000)
y, sr, envelope = pre.process(audio_path)

analyzer = PauseAnalyzer(zcr_threshold=0.05, min_pause_duration=0.15)
segments = analyzer.analyze(y, sr, envelope)

# Calculate all metrics (pause, speaking rate, articulation rate, prosody)
total_duration = len(y) / sr
all_metrics = calculate_all_metrics(y, sr, envelope, segments, total_duration)

# Display key metrics
print(f"Pathological Pause Rate: {all_metrics['pathological_pause_rate']:.1%}")
print(f"Breath Frequency: {all_metrics['breath_frequency']:.2f} /s")
print(f"Speaking Rate: {all_metrics['speaking_rate']:.1%}")
print(f"Articulation Rate: {all_metrics['articulation_rate']:.1%}")
print(f"F0 Mean: {all_metrics['f0_mean']:.1f} Hz")
print(f"Jitter (Local): {all_metrics['jitter_local']:.6f}")
print(f"Shimmer (dB): {all_metrics['shimmer_db']:.3f} dB")

# Visualize
fig = plot_analysis(y, sr, envelope, segments)
plt.savefig("analysis_output.png", dpi=150, bbox_inches="tight")
plt.close()
```

