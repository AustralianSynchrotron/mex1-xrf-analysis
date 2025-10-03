"""
Core XRF analysis functionality
"""
from .physics import (
    get_absorption_edge_energy,
    calculate_excitation_efficiency,
    calculate_compton_energy
)

from .database import (
    COMBINED_XRF_LINES,
    calculate_combined_xrf_lines,
    process_line_group,
    initialize_combined_xrf_database
)

from .corrections import (
    correct_xrf_data,
    apply_energy_calibration
)

from .peak_detection import (
    detect_scatter_peaks,
    detect_and_identify_xrf_peaks,
    find_combined_xrf_lines
)

__all__ = [
    # Physics
    'get_absorption_edge_energy',
    'calculate_excitation_efficiency',
    'calculate_compton_energy',
    # Database
    'COMBINED_XRF_LINES',
    'calculate_combined_xrf_lines',
    'process_line_group',
    'initialize_combined_xrf_database',
    # Corrections
    'correct_xrf_data',
    'apply_energy_calibration',
    # Peak detection
    'detect_scatter_peaks',
    'detect_and_identify_xrf_peaks',
    'find_combined_xrf_lines',
]