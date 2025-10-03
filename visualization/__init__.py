"""
Visualization functions for XRF analysis
"""
from .spectra import (
    plot_spectrum_with_energy,
    plot_peak_detection_results
)

from .spatial import (
    analyze_scan_pattern,
    plot_element_distribution,
    plot_element_distribution_tripcolor
)

__all__ = [
    # Spectra
    'plot_spectrum_with_energy',
    'plot_peak_detection_results',
    # Spatial
    'analyze_scan_pattern',
    'plot_element_distribution',
    'plot_element_distribution_tripcolor',
]