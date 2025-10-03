"""
XRF Analysis Package
A comprehensive toolkit for X-ray fluorescence and differential phase contrast analysis
"""
from . import core # type: ignore
from . import visualization # type: ignore
from . import dpc # type: ignore

# Convenience imports for common workflow
from .core import ( #type: ignore
    correct_xrf_data,
    apply_energy_calibration,
    initialize_combined_xrf_database,
    detect_and_identify_xrf_peaks
)

from .visualization import ( #type: ignore
    plot_spectrum_with_energy,
    plot_peak_detection_results,
    plot_element_distribution
)

__version__ = '0.1.0'

__all__ = [
    'core',
    'visualization',
    'dpc',
    'correct_xrf_data',
    'apply_energy_calibration',
    'initialize_combined_xrf_database',
    'detect_and_identify_xrf_peaks',
    'plot_spectrum_with_energy',
    'plot_peak_detection_results',
    'plot_element_distribution',
]