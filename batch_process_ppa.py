"""
Batch processing script for PPA dataset.

This script processes all audio files in the PPA dataset directory structure,
extracts all features (pause analysis, speaking rate, articulation rate, prosody),
and saves results to a CSV file for later analysis and visualization.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from tqdm import tqdm

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.preprocessor import AudioPreprocessor
from core.dynamics import PauseAnalyzer
from utils.helpers import calculate_all_metrics


def find_audio_files(root_dir: Path, pattern: str = "*.wav") -> List[Path]:
    """
    Recursively find all audio files matching the pattern.

    Parameters
    ----------
    root_dir:
        Root directory to search.
    pattern:
        File pattern to match (default: "*.wav").

    Returns
    -------
    files:
        List of Path objects to audio files.
    """
    files = list(root_dir.rglob(pattern))
    return sorted(files)


def extract_subtype_from_path(file_path: Path, root_dir: Path) -> str:
    """
    Extract PPA subtype from file path.

    Parameters
    ----------
    file_path:
        Path to audio file.
    root_dir:
        Root directory of PPA dataset.

    Returns
    -------
    subtype:
        Subtype string (e.g., "nfvppa", "lvppa", "svppa", "controls").
    """
    relative_path = file_path.relative_to(root_dir)
    parts = relative_path.parts
    
    # First directory level should be the subtype
    if len(parts) > 0:
        subtype = parts[0]
        # Normalize subtype name
        subtype = subtype.lower().replace("_", "").replace("-", "")
        if "nfv" in subtype:
            return "nfvppa"
        elif "lv" in subtype and "sv" not in subtype:
            return "lvppa"
        elif "sv" in subtype:
            return "svppa"
        elif "control" in subtype:
            return "controls"
    
    return "unknown"


def process_single_file(
    file_path: Path,
    preprocessor: AudioPreprocessor,
    analyzer: PauseAnalyzer,
    zcr_threshold: float = 0.05,
    min_pause_duration: float = 0.02,
) -> Dict[str, Any]:
    """
    Process a single audio file and extract all features.

    Parameters
    ----------
    file_path:
        Path to audio file.
    preprocessor:
        AudioPreprocessor instance.
    analyzer:
        PauseAnalyzer instance.
    zcr_threshold:
        ZCR threshold for pause classification.
    min_pause_duration:
        Minimum pause duration in seconds.

    Returns
    -------
    result:
        Dictionary containing file metadata and all extracted features.
    """
    try:
        # Load and preprocess
        y, sr, envelope = preprocessor.process(str(file_path))
        total_duration = len(y) / sr

        # Analyze pauses
        analyzer.zcr_threshold = zcr_threshold
        analyzer.min_pause_duration = min_pause_duration
        segments = analyzer.analyze(y, sr, envelope)

        # Calculate all metrics
        metrics = calculate_all_metrics(y, sr, envelope, segments, total_duration)

        # Add file metadata
        result = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size_mb": file_path.stat().st_size / (1024 * 1024),
            "total_duration": total_duration,
            "num_segments": len(segments),
            **metrics,
        }

        return result

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "error": str(e),
        }


def batch_process(
    root_dir: Path,
    output_csv: Path,
    zcr_threshold: float = 0.05,
    min_pause_duration: float = 0.02,
    max_files: int = None,
    subtype_filter: str = None,
) -> pd.DataFrame:
    """
    Batch process all audio files in the PPA dataset.

    Parameters
    ----------
    root_dir:
        Root directory of PPA dataset.
    output_csv:
        Path to output CSV file.
    zcr_threshold:
        ZCR threshold for pause classification.
    min_pause_duration:
        Minimum pause duration in seconds.
    max_files:
        Maximum number of files to process (None for all).
    subtype_filter:
        Filter by subtype (e.g., "nfvppa", "lvppa", "svppa", "controls", None for all).

    Returns
    -------
    df:
        DataFrame containing all results.
    """
    # Find all audio files
    print(f"Scanning for audio files in {root_dir}...")
    audio_files = find_audio_files(root_dir)

    # Filter by subtype if specified
    if subtype_filter:
        audio_files = [
            f for f in audio_files
            if extract_subtype_from_path(f, root_dir) == subtype_filter.lower()
        ]

    if max_files:
        audio_files = audio_files[:max_files]

    print(f"Found {len(audio_files)} audio files to process.")

    # Initialize processors
    preprocessor = AudioPreprocessor(target_sr=16000)
    analyzer = PauseAnalyzer(
        zcr_threshold=zcr_threshold,
        min_pause_duration=min_pause_duration,
    )

    # Process files
    results = []
    for file_path in tqdm(audio_files, desc="Processing files"):
        # Extract subtype
        subtype = extract_subtype_from_path(file_path, root_dir)

        # Process file
        result = process_single_file(
            file_path, preprocessor, analyzer, zcr_threshold, min_pause_duration
        )

        # Add subtype
        result["subtype"] = subtype

        results.append(result)

        # Save intermediate results every 100 files
        if len(results) % 100 == 0:
            df_temp = pd.DataFrame(results)
            df_temp.to_csv(output_csv, index=False)
            print(f"Saved intermediate results: {len(results)} files processed")

    # Create DataFrame
    df = pd.DataFrame(results)

    # Save to CSV
    df.to_csv(output_csv, index=False)
    print(f"\nProcessing complete! Results saved to {output_csv}")
    print(f"Total files processed: {len(results)}")
    if 'error' in df.columns:
        error_count = df['error'].notna().sum()
        print(f"Files with errors: {error_count}")
    else:
        print("Files with errors: 0")

    return df


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch process PPA audio dataset and extract features"
    )
    parser.add_argument(
        "--root",
        type=str,
        default="/data/jingzeyang/ppa",
        help="Root directory of PPA dataset",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="ppa_features.csv",
        help="Output CSV file path",
    )
    parser.add_argument(
        "--zcr-threshold",
        type=float,
        default=0.05,
        help="ZCR threshold for pause classification",
    )
    parser.add_argument(
        "--min-pause-duration",
        type=float,
        default=0.02,
        help="Minimum pause duration in seconds",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=None,
        help="Maximum number of files to process (for testing)",
    )
    parser.add_argument(
        "--subtype",
        type=str,
        default=None,
        choices=["nfvppa", "lvppa", "svppa", "controls"],
        help="Filter by subtype",
    )

    args = parser.parse_args()

    root_dir = Path(args.root)
    if not root_dir.exists():
        print(f"Error: Root directory {root_dir} does not exist!")
        sys.exit(1)

    output_csv = Path(args.output)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    # Run batch processing
    df = batch_process(
        root_dir=root_dir,
        output_csv=output_csv,
        zcr_threshold=args.zcr_threshold,
        min_pause_duration=args.min_pause_duration,
        max_files=args.max_files,
        subtype_filter=args.subtype,
    )

    # Print summary statistics
    if "subtype" in df.columns:
        print("\n=== Summary by Subtype ===")
        summary = df.groupby("subtype").agg({
            "file_path": "count",
            "total_duration": "sum",
            "pathological_pause_rate": "mean",
            "speaking_rate": "mean",
            "f0_mean": "mean",
        }).round(3)
        print(summary)


if __name__ == "__main__":
    main()
