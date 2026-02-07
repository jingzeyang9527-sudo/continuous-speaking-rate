"""
Streamlit Web App entry point for DSAL.

This app provides a user-friendly interface to:
- Upload audio files (.wav)
- Run pause analysis (preprocessing → segmentation → classification)
- Visualize results with colored pause regions
- Display calculated metrics (Pathological Pause Rate, Breath Frequency)
- Export results (CSV, PNG)
"""

import tempfile
import os
import io
from pathlib import Path

import streamlit as st
import numpy as np
import pandas as pd
import glob

# Import core modules
# Add parent directory to path for imports (works for both local and Streamlit Cloud)
import sys
from pathlib import Path

# Get project root directory
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import core modules
from core.preprocessor import AudioPreprocessor
from core.dynamics import PauseAnalyzer
from core.visualizer import plot_analysis
from utils.helpers import calculate_metrics, calculate_all_metrics, format_duration


# Page configuration
st.set_page_config(
    page_title="DSAL: Disordered Speech Analysis Library",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded",
)


def export_segments_csv(segments: list) -> bytes:
    """Export segments to CSV format."""
    if not segments:
        return b""
    df = pd.DataFrame(segments)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue().encode()

@st.cache_data(show_spinner=False)
def list_wavs_recursive(root_dir: str) -> list[str]:
    """
    List WAV files recursively under root_dir.
    Cached to keep the UI responsive on large datasets.
    """
    patterns = ["**/*.wav", "**/*.WAV"]
    results: list[str] = []
    for pat in patterns:
        results.extend(glob.glob(str(Path(root_dir) / pat), recursive=True))
    # Normalize + sort for stable dropdown ordering
    results = sorted({str(Path(p)) for p in results})
    return results


def main():
    """Main Streamlit app entry point."""
    st.title("🎤 Disordered Speech Analysis Library (DSAL)")
    st.markdown(
        """
        **Research Toolkit for Primary Progressive Aphasia (PPA) Speech Analysis**
        
        This tool analyzes speech recordings to distinguish between:
        - 🟢 **Physiological Pauses (Breathing)**
        - 🔴 **Pathological Pauses (Cognitive/Motor Blocks)**
        
        **📊 Use the sidebar to navigate to the Data Browser to view processed PPA dataset results.**
        """
    )

    # Sidebar: Analysis Parameters
    st.sidebar.header("⚙️ Analysis Parameters")
    zcr_threshold = st.sidebar.slider(
        "ZCR Threshold",
        min_value=0.01,
        max_value=0.20,
        value=0.05,
        step=0.01,
        help="Zero Crossing Rate threshold for breath detection. Higher values require more air friction to classify as breath.",
    )
    min_pause_duration = st.sidebar.slider(
        "Minimum Pause Duration (seconds)",
        min_value=0.01,
        max_value=1.0,
        value=0.03,
        step=0.01,
        help="Ignore pauses shorter than this duration. For fast, fluent speech, values between 0.01 and 0.05 are often needed.",
    )

    # Sidebar: Advanced Options
    with st.sidebar.expander("🔧 Advanced Options"):
        show_audio_player = st.checkbox("Show Audio Player", value=True)
        enable_caching = st.checkbox("Cache Results", value=True, help="Cache analysis results to avoid reprocessing")

    # Dataset demo selector (PPA folder)
    st.sidebar.header("🧪 Demo Dataset")
    demo_root = st.sidebar.text_input(
        "PPA dataset root",
        value="/data/jingzeyang/ppa",
        help="Root folder containing lvppa/nfvppa/svppa/controls WAV segments.",
    )

    use_dataset_selector = st.sidebar.checkbox(
        "Select from dataset (instead of upload)",
        value=True,
        help="If enabled, pick an audio file from the dataset path above.",
    )

    # Main content area
    st.header("📁 Upload Audio File")
    uploaded_file = None
    selected_dataset_path: str | None = None

    # Always show file uploader
    uploaded_file = st.file_uploader(
        "Choose a WAV file to upload",
        type=["wav"],
        help="Upload a mono or stereo WAV file. Any sample rate is supported (will be resampled to 16 kHz).",
    )

    # Dataset selector (optional, only if enabled and path exists)
    if use_dataset_selector:
        try:
            if Path(demo_root).exists():
                wavs = list_wavs_recursive(demo_root)
                if wavs:
                    st.sidebar.caption(f"Found {len(wavs)} WAV files")
                    # Show a compact relative path in the dropdown
                    rel_paths = [str(Path(p).relative_to(Path(demo_root))) for p in wavs]
                    choice = st.sidebar.selectbox("Or choose from dataset", options=rel_paths, index=0)
                    selected_dataset_path = str(Path(demo_root) / choice)

                    if st.sidebar.button("🎲 Random pick from dataset", use_container_width=True):
                        idx = np.random.randint(0, len(wavs))
                        selected_dataset_path = wavs[idx]
                        st.session_state["_random_pick_path"] = selected_dataset_path

                    # If random pick used, prefer it
                    if "_random_pick_path" in st.session_state:
                        selected_dataset_path = st.session_state["_random_pick_path"]

                    st.info(f"📄 **Dataset file:** `{selected_dataset_path}`")
                else:
                    st.sidebar.warning(f"No WAV files found under `{demo_root}`")
            else:
                st.sidebar.warning(f"Dataset path `{demo_root}` does not exist. Use file upload above.")
        except Exception as e:
            st.sidebar.warning(f"Cannot access dataset path: {e}. Use file upload above.")

    if uploaded_file is not None or selected_dataset_path is not None:
        # Create a cache key based on file content and parameters
        tmp_path = None
        if selected_dataset_path is not None:
            # Dataset mode: no need to copy bytes, just use the path directly
            tmp_path = selected_dataset_path
            cache_key = f"{selected_dataset_path}_{zcr_threshold}_{min_pause_duration}"
            file_size_mb = Path(selected_dataset_path).stat().st_size / (1024 * 1024)
            display_name = Path(selected_dataset_path).name
            file_content = None
        else:
            # Upload mode: read bytes and save to temporary file
            file_content = uploaded_file.read()
            uploaded_file.seek(0)  # Reset file pointer
            cache_key = f"{uploaded_file.name}_{zcr_threshold}_{min_pause_duration}"
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(file_content)
                tmp_path = tmp_file.name
            file_size_mb = len(file_content) / (1024 * 1024)
            display_name = uploaded_file.name

        try:
            # Display file info
            st.info(f"📄 **File:** {display_name} ({file_size_mb:.2f} MB)")

            # Audio player (if enabled)
            if show_audio_player:
                if uploaded_file is not None:
                    st.audio(uploaded_file, format="audio/wav")
                else:
                    # Dataset file playback: load bytes
                    st.audio(Path(tmp_path).read_bytes(), format="audio/wav")

            # Check cache
            results_cached = False
            if enable_caching and cache_key in st.session_state:
                cached_results = st.session_state[cache_key]
                st.sidebar.success("✅ Using cached results")
                results_cached = True
                y = cached_results["y"]
                sr = cached_results["sr"]
                envelope = cached_results["envelope"]
                segments = cached_results["segments"]
                metrics = cached_results["metrics"]
                total_duration = cached_results["total_duration"]
            else:
                # Analyze button
                if st.button("🔍 Analyze", type="primary", use_container_width=True):
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    try:
                        # Step 1: Preprocess
                        status_text.text("📥 Loading and preprocessing audio...")
                        progress_bar.progress(20)
                        
                        preprocessor = AudioPreprocessor(target_sr=16000)
                        y, sr, envelope = preprocessor.process(tmp_path)
                        total_duration = len(y) / sr

                        # Step 2: Analyze pauses
                        status_text.text("🔍 Analyzing pauses and classifying segments...")
                        progress_bar.progress(60)
                        
                        analyzer = PauseAnalyzer(
                            zcr_threshold=zcr_threshold,
                            min_pause_duration=min_pause_duration,
                        )
                        segments = analyzer.analyze(y, sr, envelope)

                        # Step 3: Calculate all metrics (pause, speaking rate, articulation rate, prosody)
                        status_text.text("📊 Calculating metrics and extracting features...")
                        progress_bar.progress(80)
                        
                        metrics = calculate_all_metrics(y, sr, envelope, segments, total_duration)

                        # Cache results
                        if enable_caching:
                            st.session_state[cache_key] = {
                                "y": y,
                                "sr": sr,
                                "envelope": envelope,
                                "segments": segments,
                                "metrics": metrics,
                                "total_duration": total_duration,
                            }

                        progress_bar.progress(100)
                        status_text.text("✅ Analysis complete!")
                        
                        # Small delay to show completion
                        import time
                        time.sleep(0.5)
                        progress_bar.empty()
                        status_text.empty()

                    except Exception as e:
                        progress_bar.empty()
                        status_text.empty()
                        raise e

            # Display results (if analysis was run or cached)
            if results_cached or ("segments" in locals()):
                st.success(f"✅ Analysis complete! Found {len(segments)} pause segments.")

                # Metrics display
                st.header("📊 Analysis Metrics")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Pathological Pause Rate",
                        f"{metrics['pathological_pause_rate']:.1%}",
                        help="Proportion of audio duration classified as pathological pauses",
                    )

                with col2:
                    st.metric(
                        "Breath Frequency",
                        f"{metrics['breath_frequency']:.2f} /s",
                        help="Number of breath pauses per second",
                    )

                with col3:
                    st.metric(
                        "Pathological Duration",
                        format_duration(metrics['pathological_duration']),
                    )

                with col4:
                    st.metric(
                        "Breath Count",
                        f"{metrics['breath_count']}",
                    )

                # Speaking Rate & Articulation Rate
                st.header("🗣️ Speaking Rate & Articulation Rate")
                col_sr1, col_sr2, col_sr3, col_sr4 = st.columns(4)
                
                with col_sr1:
                    st.metric(
                        "Speaking Rate",
                        f"{metrics.get('speaking_rate', 0.0):.1%}",
                        help="Proportion of time spent speaking (speech duration / total duration)",
                    )
                
                with col_sr2:
                    st.metric(
                        "Articulation Rate",
                        f"{metrics.get('articulation_rate', 0.0):.1%}",
                        help="Speech duration / (total duration - pause duration)",
                    )
                
                with col_sr3:
                    st.metric(
                        "Speech Duration",
                        format_duration(metrics.get('speech_duration', 0.0)),
                    )
                
                with col_sr4:
                    st.metric(
                        "Net Speech Duration",
                        format_duration(metrics.get('net_speech_duration', 0.0)),
                        help="Total duration minus all pause durations",
                    )

                # Prosody Features
                st.header("🎵 Prosody Features")
                
                # F0 (Pitch) features
                st.subheader("📊 Fundamental Frequency (F0 / Pitch)")
                col_f0_1, col_f0_2, col_f0_3, col_f0_4 = st.columns(4)
                
                with col_f0_1:
                    st.metric("F0 Mean", f"{metrics.get('f0_mean', 0.0):.1f} Hz")
                    st.metric("F0 Std", f"{metrics.get('f0_std', 0.0):.1f} Hz")
                
                with col_f0_2:
                    st.metric("F0 Min", f"{metrics.get('f0_min', 0.0):.1f} Hz")
                    st.metric("F0 Max", f"{metrics.get('f0_max', 0.0):.1f} Hz")
                
                with col_f0_3:
                    st.metric("F0 Range", f"{metrics.get('f0_range', 0.0):.1f} Hz")
                    st.metric("F0 CV", f"{metrics.get('f0_cv', 0.0):.3f}", help="Coefficient of variation (std/mean)")
                
                with col_f0_4:
                    st.metric("Voiced Ratio", f"{metrics.get('voiced_ratio', 0.0):.1%}", help="Proportion of voiced frames")
                
                # Jitter & Shimmer
                st.subheader("📈 Jitter & Shimmer")
                col_js1, col_js2, col_js3 = st.columns(3)
                
                with col_js1:
                    st.metric("Jitter (Local)", f"{metrics.get('jitter_local', 0.0):.6f}")
                    st.metric("Jitter (RAP)", f"{metrics.get('jitter_rap', 0.0):.6f}", help="Relative Average Perturbation")
                
                with col_js2:
                    st.metric("Jitter (PPQ5)", f"{metrics.get('jitter_ppq5', 0.0):.6f}", help="Pitch Period Perturbation Quotient (5-point)")
                    st.metric("Shimmer (Local)", f"{metrics.get('shimmer_local', 0.0):.6f}")
                
                with col_js3:
                    st.metric("Shimmer (dB)", f"{metrics.get('shimmer_db', 0.0):.3f} dB")
                    st.metric("Shimmer (APQ5)", f"{metrics.get('shimmer_apq5', 0.0):.6f}", help="Amplitude Perturbation Quotient (5-point)")
                
                # Intensity
                st.subheader("🔊 Intensity")
                col_int1, col_int2, col_int3 = st.columns(3)
                
                with col_int1:
                    st.metric("Intensity Mean", f"{metrics.get('intensity_mean', 0.0):.4f}")
                    st.metric("Intensity Std", f"{metrics.get('intensity_std', 0.0):.4f}")
                
                with col_int2:
                    st.metric("Intensity Min", f"{metrics.get('intensity_min', 0.0):.4f}")
                    st.metric("Intensity Max", f"{metrics.get('intensity_max', 0.0):.4f}")
                
                with col_int3:
                    st.metric("Intensity Range", f"{metrics.get('intensity_range', 0.0):.4f}")

                # Additional pause metrics in expander
                with st.expander("📈 Additional Pause Metrics"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Total Pause Duration", format_duration(metrics['total_pause_duration']))
                        st.metric("Total Pause Rate", f"{metrics['pause_rate']:.1%}")
                    with col_b:
                        st.metric("Audio Duration", format_duration(total_duration))
                        avg_pause_duration = (
                            metrics['total_pause_duration'] / len(segments) 
                            if len(segments) > 0 else 0
                        )
                        st.metric("Average Pause Duration", format_duration(avg_pause_duration))

                # Export buttons
                st.header("💾 Export Results")
                export_col1, export_col2 = st.columns(2)

                with export_col1:
                    # CSV export
                    if segments:
                        csv_data = export_segments_csv(segments)
                        st.download_button(
                            label="📥 Download Segments (CSV)",
                            data=csv_data,
                            file_name=f"{Path(display_name).stem}_segments.csv",
                            mime="text/csv",
                            use_container_width=True,
                        )
                    else:
                        st.info("No segments to export")

                with export_col2:
                    # Image export placeholder (user can right-click on figure to save)
                    st.info("💡 Right-click on the visualization below to save as image")

                # Visualization
                st.header("📈 Visualization")
                fig = plot_analysis(y, sr, envelope, segments, figsize=(14, 6))
                st.pyplot(fig)

                # Detailed segment list
                with st.expander("📋 View Detailed Segment List"):
                    if segments:
                        df = pd.DataFrame(segments)
                        # Format columns for display
                        df_display = df.copy()
                        df_display["start"] = df_display["start"].apply(lambda x: f"{x:.3f}")
                        df_display["end"] = df_display["end"].apply(lambda x: f"{x:.3f}")
                        df_display["duration"] = (df["end"] - df["start"]).apply(
                            lambda x: f"{x:.3f}"
                        )
                        if "zcr" in df_display.columns:
                            df_display["zcr"] = df_display["zcr"].apply(lambda x: f"{x:.4f}")
                        if "energy" in df_display.columns:
                            df_display["energy"] = df_display["energy"].apply(
                                lambda x: f"{x:.2e}"
                            )

                        # Display with sorting capability
                        st.dataframe(
                            df_display[["start", "end", "duration", "type", "zcr", "energy"]],
                            use_container_width=True,
                            height=400,
                        )

                        # Summary statistics
                        st.subheader("📊 Segment Statistics")
                        stat_col1, stat_col2, stat_col3 = st.columns(3)
                        with stat_col1:
                            breath_segments = [s for s in segments if s.get("type") == "breath"]
                            pathological_segments = [s for s in segments if s.get("type") == "pathological"]
                            st.write(f"**Breath segments:** {len(breath_segments)}")
                            st.write(f"**Pathological segments:** {len(pathological_segments)}")
                        with stat_col2:
                            if breath_segments:
                                avg_breath = np.mean([s["end"] - s["start"] for s in breath_segments])
                                st.write(f"**Avg breath duration:** {avg_breath:.3f}s")
                            if pathological_segments:
                                avg_path = np.mean([s["end"] - s["start"] for s in pathological_segments])
                                st.write(f"**Avg pathological duration:** {avg_path:.3f}s")
                        with stat_col3:
                            if breath_segments:
                                max_breath = max([s["end"] - s["start"] for s in breath_segments])
                                st.write(f"**Max breath duration:** {max_breath:.3f}s")
                            if pathological_segments:
                                max_path = max([s["end"] - s["start"] for s in pathological_segments])
                                st.write(f"**Max pathological duration:** {max_path:.3f}s")
                    else:
                        st.info("No pause segments detected.")

            else:
                # Show analyze button if not cached
                st.info("👆 Click 'Analyze' to process the audio file.")

        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            with st.expander("🔍 Error Details"):
                st.exception(e)
            st.info("💡 **Tips:**\n- Ensure the file is a valid WAV format\n- Check that the file is not corrupted\n- Try adjusting the analysis parameters")

        finally:
            # Clean up temporary file (only for upload mode)
            if uploaded_file is not None and tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass  # Ignore cleanup errors

    else:
        st.info("👆 Please upload a WAV file to begin analysis.")
        
        # Show example usage
        with st.expander("ℹ️ How to Use"):
            st.markdown("""
            **Step-by-step guide:**
            1. **Upload** a WAV audio file using the file uploader above
            2. **Adjust parameters** (optional) in the sidebar:
               - ZCR Threshold: Controls sensitivity for breath detection
               - Minimum Pause Duration: Filters out very short pauses
            3. **Click "Analyze"** to process the audio
            4. **Review** the metrics, visualization, and segment list
            5. **Export** results as CSV if needed
            
            **Tips:**
            - The app automatically resamples audio to 16 kHz
            - Larger files may take a few seconds to process
            - Enable caching to avoid reprocessing when adjusting visualization
            - Use the audio player to listen to your uploaded file
            """)


if __name__ == "__main__":
    main()
