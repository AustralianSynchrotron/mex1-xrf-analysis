# XRF Analysis Toolkit

A comprehensive Python package for X-ray fluorescence (XRF) and differential phase contrast (DPC) analysis.

## Features

- **Data Correction**: Deadtime correction and i0 normalization
- **Energy Calibration**: Flexible energy axis calibration
- **Peak Detection**: Automated scatter and XRF peak detection
- **Physics-Based Identification**: XRF line identification using excitation physics
- **Spatial Mapping**: Element distribution visualization
- **DPC Analysis**: Beam deflection calculations

## Installation

### From source:
```bash
git clone https://github.com/yourusername/xrf-analysis.git
cd xrf-analysis
pip install -e .
```

### Requirements:
- Python >= 3.8
- numpy >= 1.20.0
- scipy >= 1.7.0
- matplotlib >= 3.3.0
- h5py >= 3.0.0
- xraylib >= 4.0.0

## Quick Start

```python
import xrf_analysis as xrf

# Initialize XRF database
xrf.initialize_combined_xrf_database()

# Load and correct data
results = xrf.correct_xrf_data('your_file.h5')
results = xrf.apply_energy_calibration(results, eV_per_channel=10)

# Detect peaks
detection_results = xrf.detect_and_identify_xrf_peaks(results)

# Visualize
xrf.plot_peak_detection_results(detection_results)
xrf.plot_element_distribution(results, 'Fe', 'Ka')
```

## Project Structure

```
xrf_analysis/
├── core/
│   ├── physics.py          # XRF physics calculations
│   ├── database.py         # XRF line database
│   ├── corrections.py      # Data corrections
│   └── peak_detection.py   # Peak detection algorithms
├── visualization/
│   ├── spectra.py         # Spectrum plotting
│   └── spatial.py         # Spatial distribution plots
└── dpc/
    └── analysis.py        # DPC calculations
```

## Workflow

### 1. Load and Correct Data
```python
# Load HDF5 file with deadtime and i0 correction
results = xrf.correct_xrf_data('data.h5')

# Apply energy calibration
results = xrf.apply_energy_calibration(
    results,
    eV_per_channel=10,
    energy_offset=0
)
```

### 2. Visualize Spectra
```python
# Plot integrated and maximum envelope spectra
xrf.plot_spectrum_with_energy(results)
```

### 3. Detect and Identify Peaks
```python
# Detect XRF peaks with scatter peak exclusion
detection_results = xrf.detect_and_identify_xrf_peaks(
    results,
    thresholds=[10, 50, 10],      # [height, distance_eV, prominence]
    tolerance_keV=0.060,           # 60 eV matching tolerance
    detect_scatter=True            # Exclude elastic/Compton peaks
)

# Visualize detection results
xrf.plot_peak_detection_results(detection_results)
```

### 4. Map Element Distributions
```python
# Create spatial distribution map
intensities = xrf.plot_element_distribution(
    results,
    element_name='Fe',
    line_family='Ka',
    integration_width_keV=0.15,
    sensor_sum=True,
    scale='log'
)
```

## Advanced Features

### Custom Peak Detection Parameters
```python
detection_results = xrf.detect_and_identify_xrf_peaks(
    results,
    thresholds=[20, 100, 15],      # Higher thresholds for cleaner data
    smooth_window=7,                # More smoothing
    bkg_method='polynomial',        # Polynomial background
    bkg_radius=100                  # Larger background filter
)
```

### 45° Geometry Correction
```python
# For samples measured at 45° to the beam
xrf.plot_element_distribution(
    results,
    'Cu', 'Ka',
    correct_45deg=True,
    expand_x=True  # Expand to sample surface coordinates
)
```

### DPC Analysis
```python
from xrf_analysis.dpc import calculate_dpc_deflections, plot_dpc_results

# Calculate beam deflections
dpc_results = calculate_dpc_deflections(
    thor_x, thor_y, thor_Tot, i0,
    Lx=10, Ly=10  # Detector dimensions in mm
)

# Visualize DPC results
plot_dpc_results(abs_x, abs_y, dpc_results['beam_x'], 
                 dpc_results['beam_y'], thor_Tot)
```

## API Reference

### Core Functions

#### `correct_xrf_data(file_path)`
Load and correct XRF data from HDF5 file.

#### `apply_energy_calibration(results, eV_per_channel, energy_offset)`
Apply energy calibration to create energy axis.

#### `initialize_combined_xrf_database()`
Pre-calculate XRF line database (call once at startup).

#### `detect_and_identify_xrf_peaks(results, **kwargs)`
Detect and identify XRF peaks with physics-based filtering.

### Visualization Functions

#### `plot_spectrum_with_energy(results)`
Plot integrated and envelope spectra.

#### `plot_peak_detection_results(detection_results, y_min)`
Visualize peak detection with annotations.

#### `plot_element_distribution(results, element_name, line_family, **kwargs)`
Create spatial distribution maps.

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Citation

If you use this package in your research, please cite:
```
[Your citation information]
```