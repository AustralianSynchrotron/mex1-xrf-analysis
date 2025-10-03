# Quick Start Guide

## Step 1: Create Directory Structure

```bash
mkdir -p xrf-analysis/xrf_analysis/{core,visualization,dpc}
cd xrf-analysis
```

## Step 2: Create All Files

Copy the following files into their respective locations:

### Main Package (`xrf_analysis/`)
- `__init__.py` (main package)
- `cli.py`

### Core Module (`xrf_analysis/core/`)
- `__init__.py`
- `physics.py`
- `database.py`
- `corrections.py`
- `peak_detection.py`

### Visualization Module (`xrf_analysis/visualization/`)
- `__init__.py`
- `spectra.py`
- `spatial.py`

### DPC Module (`xrf_analysis/dpc/`)
- `__init__.py`
- `analysis.py`

### Root Directory
- `setup.py`
- `requirements.txt`
- `README.md`
- `.gitignore`
- `example_workflow.py`

## Step 3: Install Dependencies

```bash
pip install numpy scipy matplotlib h5py xraylib
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

## Step 4: Install Package

```bash
# Development mode (recommended for testing)
pip install -e .

# Or regular installation
pip install .
```

## Step 5: Verify Installation

```bash
# Check if command is available
xrf-analyze --help

# Should show available commands
```

```python
# Test Python import
python -c "import xrf_analysis as xrf; print('Success!')"
```

## Step 6: Run Your First Analysis

### Command-Line Usage

```bash
# Full workflow with plots
xrf-analyze process your_data.h5 --plot-all

# Just detect peaks
xrf-analyze detect-peaks your_data.h5 --plot

# Create element map
xrf-analyze map-element your_data.h5 Fe Ka --scale log
```

### Python Script Usage

Create a file `my_analysis.py`:

```python
import xrf_analysis as xrf

# Initialize database
print("Initializing XRF database...")
xrf.initialize_combined_xrf_database()

# Load and correct data
print("Loading data...")
results = xrf.correct_xrf_data('your_data.h5')
results = xrf.apply_energy_calibration(results, eV_per_channel=10)

# Detect peaks
print("Detecting peaks...")
detection = xrf.detect_and_identify_xrf_peaks(results)

# Visualize
print("Creating plots...")
xrf.plot_peak_detection_results(detection)
xrf.plot_element_distribution(results, 'Fe', 'Ka', scale='log')

print("Done!")
```

Run it:
```bash
python my_analysis.py
```

## Troubleshooting

### ImportError: No module named 'xraylib'

Install xraylib:
```bash
pip install xraylib
```

Or via conda:
```bash
conda install -c conda-forge xraylib
```

### Command 'xrf-analyze' not found

Make sure you installed the package:
```bash
pip install -e .
```

And that your Python scripts directory is in PATH.

### HDF5 file structure issues

Check your HDF5 file contains the expected datasets:
```python
import h5py

with h5py.File('your_data.h5', 'r') as f:
    print("Available datasets:")
    for key in f.keys():
        print(f"  {key}: {f[key].shape}")
```

Required datasets:
- `spectrum`: XRF spectra
- `DTFactor`: Deadtime correction factors
- `i0`: Incident beam intensity
- `abs_x`, `abs_y`: Spatial positions
- `dcm_energy_ev`: Incident energy

## Common Workflows

### 1. Quick Peak Identification

```bash
xrf-analyze detect-peaks data.h5 --plot \
  --height 20 \
  --prominence 15 \
  --tolerance 50
```

### 2. Multi-Element Mapping

```bash
# Map Fe
xrf-analyze map-element data.h5 Fe Ka --scale log

# Map Cu
xrf-analyze map-element data.h5 Cu Ka --scale log

# Map scatter
xrf-analyze map-element data.h5 elastic --scale log
```

### 3. Custom Background Subtraction

```bash
xrf-analyze process data.h5 --plot-all \
  --bkg-method polynomial \
  --smooth-window 7
```

### 4. 45° Geometry Correction

```bash
xrf-analyze map-element data.h5 Fe Ka \
  --scale log \
  --correct-45deg
```

## Next Steps

1. Read the full [README.md](README.md) for detailed API documentation
2. Check [example_workflow.py](example_workflow.py) for more examples
3. Explore the CLI help: `xrf-analyze <command> --help`
4. Customize thresholds and parameters for your data

## Getting Help

For command-line help:
```bash
xrf-analyze --help
xrf-analyze process --help
xrf-analyze map-element --help
```

For Python API documentation:
```python
import xrf_analysis as xrf
help(xrf.detect_and_identify_xrf_peaks)
help(xrf.plot_element_distribution)
```