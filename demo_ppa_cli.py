"""
CLI demo: run DSAL pipeline on a WAV file from the PPA dataset and export outputs.

Outputs:
- segments CSV
- analysis PNG

Usage examples:
  python demo_ppa_cli.py --wav "/data/jingzeyang/ppa/controls_jiachen2_copy/.../segment/segment7.wav"
  python demo_ppa_cli.py --root "/data/jingzeyang/ppa" --random
"""

from __future__ import annotations

import argparse
from pathlib import Path
import random

import pandas as pd

from core.preprocessor import AudioPreprocessor
from core.dynamics import PauseAnalyzer
from core.visualizer import plot_analysis
from utils.helpers import calculate_metrics


def find_wavs(root: Path) -> list[Path]:
    wavs = list(root.rglob("*.wav")) + list(root.rglob("*.WAV"))
    return sorted({p.resolve() for p in wavs})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wav", type=str, default=None, help="Path to a WAV file")
    parser.add_argument("--root", type=str, default="/data/jingzeyang/ppa", help="Dataset root to search")
    parser.add_argument("--random", action="store_true", help="Pick a random wav under --root")
    parser.add_argument("--zcr-threshold", type=float, default=0.05)
    parser.add_argument("--min-pause-duration", type=float, default=0.15)
    parser.add_argument("--outdir", type=str, default="demo_outputs", help="Output directory")
    args = parser.parse_args()

    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    if args.wav:
        wav_path = Path(args.wav).expanduser().resolve()
    else:
        root = Path(args.root).expanduser().resolve()
        wavs = find_wavs(root)
        if not wavs:
            raise SystemExit(f"No wav files found under {root}")
        wav_path = random.choice(wavs) if args.random else wavs[0]

    if not wav_path.exists():
        raise SystemExit(f"WAV not found: {wav_path}")

    pre = AudioPreprocessor(target_sr=16000)
    y, sr, envelope = pre.process(str(wav_path))

    analyzer = PauseAnalyzer(
        zcr_threshold=float(args.zcr_threshold),
        min_pause_duration=float(args.min_pause_duration),
    )
    segments = analyzer.analyze(y, sr, envelope)

    total_duration = len(y) / sr
    metrics = calculate_metrics(segments, total_duration)

    stem = wav_path.stem
    csv_path = outdir / f"{stem}_segments.csv"
    png_path = outdir / f"{stem}_analysis.png"

    pd.DataFrame(segments).to_csv(csv_path, index=False)

    fig = plot_analysis(y, sr, envelope, segments, figsize=(14, 6))
    fig.savefig(png_path, dpi=150, bbox_inches="tight")

    print(f"WAV: {wav_path}")
    print(f"Segments: {len(segments)}")
    print(f"Pathological Pause Rate: {metrics['pathological_pause_rate']:.1%}")
    print(f"Breath Frequency: {metrics['breath_frequency']:.2f} /s")
    print(f"CSV: {csv_path}")
    print(f"PNG: {png_path}")


if __name__ == "__main__":
    main()

