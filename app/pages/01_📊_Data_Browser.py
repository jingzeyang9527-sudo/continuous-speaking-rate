"""
Data Browser page for viewing processed PPA dataset results.
"""

import pandas as pd
import streamlit as st
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page config
st.set_page_config(
    page_title="DSAL - Data Browser",
    page_icon="📊",
    layout="wide",
)

st.title("📊 PPA Dataset Browser")

# Load processed data
@st.cache_data
def load_processed_data(csv_path: str):
    """Load processed features CSV."""
    if not Path(csv_path).exists():
        return None
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


# Sidebar: Data source
st.sidebar.header("📁 Data Source")

# Option 1: Upload CSV file
uploaded_csv = st.sidebar.file_uploader(
    "Upload Features CSV",
    type=["csv"],
    help="Upload a CSV file with processed features (from batch_process_ppa.py)",
)

# Option 2: Load from path (for local/server deployment)
csv_path = None
if not uploaded_csv:
    csv_path = st.sidebar.text_input(
        "Or specify CSV file path",
        value="ppa_features.csv",
        help="Path to the CSV file (for local/server deployment)",
    )

# Load data
if uploaded_csv:
    # Load from uploaded file
    try:
        df = pd.read_csv(uploaded_csv)
        st.sidebar.success(f"✅ Loaded {len(df)} records from uploaded file")
    except Exception as e:
        st.sidebar.error(f"Error loading uploaded file: {e}")
        df = None
elif csv_path:
    # Load from file path
    df = load_processed_data(csv_path)
else:
    df = None

if df is None:
    st.warning(
        f"""
        **No processed data found at `{csv_path}`**
        
        To generate the features CSV, run:
        ```bash
        python batch_process_ppa.py --root /data/jingzeyang/ppa --output ppa_features.csv
        ```
        """
    )
else:
    st.success(f"✅ Loaded {len(df)} records from `{csv_path}`")

    # Filters
    st.sidebar.header("🔍 Filters")
    
    if "subtype" in df.columns:
        subtypes = df["subtype"].unique()
        selected_subtypes = st.sidebar.multiselect(
            "Subtype",
            options=sorted(subtypes),
            default=sorted(subtypes),
        )
        df_filtered = df[df["subtype"].isin(selected_subtypes)]
    else:
        df_filtered = df

    # Duration filter
    if "total_duration" in df.columns:
        min_dur = float(df["total_duration"].min())
        max_dur = float(df["total_duration"].max())
        dur_range = st.sidebar.slider(
            "Duration Range (seconds)",
            min_value=min_dur,
            max_value=max_dur,
            value=(min_dur, max_dur),
        )
        df_filtered = df_filtered[
            (df_filtered["total_duration"] >= dur_range[0])
            & (df_filtered["total_duration"] <= dur_range[1])
        ]

    st.info(f"Showing {len(df_filtered)} records after filtering")

    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🔍 Search", "📊 Comparison", "📥 Export"])

    with tab1:
        st.header("Dataset Overview")

        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Files", len(df_filtered))
        
        with col2:
            if "total_duration" in df_filtered.columns:
                total_dur = df_filtered["total_duration"].sum() / 3600  # hours
                st.metric("Total Duration", f"{total_dur:.1f} hours")
        
        with col3:
            if "subtype" in df_filtered.columns:
                num_subtypes = df_filtered["subtype"].nunique()
                st.metric("Subtypes", num_subtypes)
        
        with col4:
            if "pathological_pause_rate" in df_filtered.columns:
                avg_ppr = df_filtered["pathological_pause_rate"].mean()
                st.metric("Avg Pathological Pause Rate", f"{avg_ppr:.1%}")

        # Subtype distribution
        if "subtype" in df_filtered.columns:
            st.subheader("Subtype Distribution")
            subtype_counts = df_filtered["subtype"].value_counts()
            fig = px.pie(
                values=subtype_counts.values,
                names=subtype_counts.index,
                title="Files by Subtype",
            )
            st.plotly_chart(fig, use_container_width=True)

        # Key metrics distribution
        st.subheader("Key Metrics Distribution")
        
        metric_cols = [
            "pathological_pause_rate",
            "speaking_rate",
            "articulation_rate",
            "f0_mean",
        ]
        
        available_metrics = [col for col in metric_cols if col in df_filtered.columns]
        
        if available_metrics:
            selected_metric = st.selectbox("Select Metric", available_metrics)
            
            if "subtype" in df_filtered.columns:
                fig = px.histogram(
                    df_filtered,
                    x=selected_metric,
                    color="subtype",
                    nbins=30,
                    title=f"Distribution of {selected_metric}",
                    barmode="overlay",
                )
            else:
                fig = px.histogram(
                    df_filtered,
                    x=selected_metric,
                    nbins=30,
                    title=f"Distribution of {selected_metric}",
                )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("Search Records")
        
        search_term = st.text_input("Search by file name or path", "")
        
        if search_term:
            mask = df_filtered["file_name"].str.contains(search_term, case=False, na=False)
            if "file_path" in df_filtered.columns:
                mask |= df_filtered["file_path"].str.contains(search_term, case=False, na=False)
            df_search = df_filtered[mask]
        else:
            df_search = df_filtered

        # Display table
        display_cols = ["file_name", "subtype", "total_duration"]
        display_cols.extend([col for col in metric_cols if col in df_search.columns])
        display_cols = [col for col in display_cols if col in df_search.columns]
        
        st.dataframe(
            df_search[display_cols],
            use_container_width=True,
            height=400,
        )

    with tab3:
        st.header("Subtype Comparison")
        
        if "subtype" not in df_filtered.columns:
            st.warning("Subtype information not available in the data.")
        else:
            # Comparison metrics
            comparison_metrics = [
                "pathological_pause_rate",
                "speaking_rate",
                "articulation_rate",
                "f0_mean",
                "f0_std",
                "jitter_local",
                "shimmer_db",
            ]
            
            available_comparison = [m for m in comparison_metrics if m in df_filtered.columns]
            
            if available_comparison:
                selected_comparison = st.multiselect(
                    "Select Metrics to Compare",
                    available_comparison,
                    default=available_comparison[:4],
                )
                
                if selected_comparison:
                    # Group by subtype and calculate statistics
                    summary = df_filtered.groupby("subtype")[selected_comparison].agg(
                        ["mean", "std"]
                    )
                    
                    st.subheader("Summary Statistics by Subtype")
                    st.dataframe(summary, use_container_width=True)
                    
                    # Box plots
                    for metric in selected_comparison:
                        st.subheader(f"{metric}")
                        fig = px.box(
                            df_filtered,
                            x="subtype",
                            y=metric,
                            title=f"{metric} by Subtype",
                        )
                        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.header("Export Data")
        
        st.subheader("Export Filtered Data")
        csv_export = df_filtered.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered CSV",
            data=csv_export,
            file_name="ppa_features_filtered.csv",
            mime="text/csv",
        )
        
        if "subtype" in df_filtered.columns:
            st.subheader("Export by Subtype")
            for subtype in df_filtered["subtype"].unique():
                df_subtype = df_filtered[df_filtered["subtype"] == subtype]
                csv_subtype = df_subtype.to_csv(index=False)
                st.download_button(
                    label=f"📥 Download {subtype} CSV",
                    data=csv_subtype,
                    file_name=f"ppa_features_{subtype}.csv",
                    mime="text/csv",
                    key=f"export_{subtype}",
                )
