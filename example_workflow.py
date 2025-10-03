"""
Example XRF Analysis Workflow
Demonstrates the typical analysis pipeline: Load → Correct → Detect → Plot
"""
import xrf_analysis as xrf

# Step 1: Initialize the XRF line database (do this once at startup)
print("Initializing XRF database...")
xrf.initialize_combined_xrf_database()

# Step 2: Load and correct XRF data
print("\nLoading and correcting data...")
file_path = 'your_data_file.h5'  # Replace with your file path
results = xrf.correct_xrf_data(file_path)

# Step 3: Apply energy calibration
print("\nApplying energy calibration...")
results = xrf.apply_energy_calibration(
    results,
    eV_per_channel=10,  # Adjust for your detector
    energy_offset=0
)

# Step 4: Plot the spectrum
print("\nPlotting spectra...")
xrf.plot_spectrum_with_energy(results)

# Step 5: Detect and identify peaks
print("\nDetecting peaks...")
detection_results = xrf.detect_and_identify_xrf_peaks(
    results,
    thresholds=[10, 50, 10],  # [height, distance_eV, prominence]
    tolerance_keV=0.060,      # 60 eV tolerance
    smooth_window=5,
    bkg_method='rolling_ball',
    bkg_radius=50,
    detect_scatter=True
)

# Step 6: Plot peak detection results
print("\nPlotting peak detection results...")
xrf.plot_peak_detection_results(detection_results, y_min=0.1)

# Step 7: Plot element distributions (optional)
print("\nPlotting element distributions...")
# Example: Plot Fe Ka distribution
fe_intensities = xrf.plot_element_distribution(
    results,
    element_name='Fe',
    line_family='Ka',
    integration_width_keV=0.15,
    sensor_sum=True,
    scale='log',
    correct_45deg=False
)

print("\nAnalysis complete!")