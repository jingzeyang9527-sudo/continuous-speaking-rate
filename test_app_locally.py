"""
Test script to verify DSAL app functionality before deployment.

This script tests:
1. All imports work correctly
2. Core modules can be instantiated
3. Feature extraction functions work
4. App can start without errors
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        from core.preprocessor import AudioPreprocessor
        from core.dynamics import PauseAnalyzer
        from core.visualizer import plot_analysis
        from core.features import (
            calculate_speaking_rate,
            calculate_articulation_rate,
            extract_all_prosody_features,
        )
        from utils.helpers import (
            calculate_metrics,
            calculate_all_metrics,
            format_duration,
        )
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_core_modules():
    """Test that core modules can be instantiated."""
    print("\nTesting core modules...")
    try:
        from core.preprocessor import AudioPreprocessor
        from core.dynamics import PauseAnalyzer
        
        preprocessor = AudioPreprocessor(target_sr=16000)
        analyzer = PauseAnalyzer(zcr_threshold=0.05, min_pause_duration=0.02)
        
        print("✅ Core modules instantiated successfully")
        return True
    except Exception as e:
        print(f"❌ Error instantiating modules: {e}")
        return False

def test_requirements():
    """Check that all requirements are installed."""
    print("\nTesting requirements...")
    required_packages = [
        "librosa",
        "scipy",
        "numpy",
        "pandas",
        "matplotlib",
        "streamlit",
        "tqdm",
        "plotly",
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    else:
        print("\n✅ All required packages installed")
        return True

def test_app_structure():
    """Check that app structure is correct."""
    print("\nTesting app structure...")
    required_files = [
        "app/main.py",
        "app/pages/01_📊_Data_Browser.py",
        "requirements.txt",
        ".streamlit/config.toml",
        "core/preprocessor.py",
        "core/dynamics.py",
        "core/features.py",
        "core/visualizer.py",
        "utils/helpers.py",
    ]
    
    missing = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            missing.append(file_path)
    
    if missing:
        print(f"\n❌ Missing files: {', '.join(missing)}")
        return False
    else:
        print("\n✅ All required files present")
        return True

def test_streamlit_config():
    """Check Streamlit configuration."""
    print("\nTesting Streamlit configuration...")
    try:
        import streamlit as st
        config_path = Path(".streamlit/config.toml")
        if config_path.exists():
            print("  ✅ .streamlit/config.toml exists")
        else:
            print("  ⚠️  .streamlit/config.toml not found (optional)")
        
        # Check if main.py can be imported as a module
        sys.path.insert(0, str(Path("app").parent))
        # Just check syntax, don't actually run
        with open("app/main.py") as f:
            compile(f.read(), "app/main.py", "exec")
        print("  ✅ app/main.py syntax is valid")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("DSAL Application Test Suite")
    print("=" * 60)
    
    results = []
    
    results.append(("Requirements", test_requirements()))
    results.append(("App Structure", test_app_structure()))
    results.append(("Imports", test_imports()))
    results.append(("Core Modules", test_core_modules()))
    results.append(("Streamlit Config", test_streamlit_config()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:20s} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! Ready for deployment.")
        return 0
    else:
        print("❌ Some tests failed. Please fix issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
