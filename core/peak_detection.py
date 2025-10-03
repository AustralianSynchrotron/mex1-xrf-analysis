"""
Peak Detection Functions
Handles scatter peak detection and XRF peak identification
"""
import numpy as np
from scipy.signal import find_peaks
from scipy.ndimage import minimum_filter1d, uniform_filter1d

from .physics import calculate_compton_energy, get_absorption_edge_energy, calculate_excitation_efficiency
from .database import COMBINED_XRF_LINES


def detect_scatter_peaks(energy_keV, spectrum, incident_energy_keV, 
                        search_window_keV=3.0, min_prominence=20):
    """
    Detect elastic and Compton scatter peaks near the incident energy
    
    Parameters:
    -----------
    energy_keV : array
        Energy axis in keV
    spectrum : array  
        Spectrum data (smoothed/background subtracted)
    incident_energy_keV : float
        Incident beam energy in keV
    search_window_keV : float
        Search window below incident energy (for Compton)
    min_prominence : float
        Minimum prominence for scatter peak detection
        
    Returns:
    --------
    dict : Dictionary containing scatter peak information and exclusion zones
    """
    # Calculate expected Compton energy (90° scattering)
    expected_compton_energy = calculate_compton_energy(incident_energy_keV, 90)
    
    # Define search region
    search_min = incident_energy_keV - search_window_keV
    search_max = incident_energy_keV + 0.2
    
    # Create mask for search region
    search_mask = (energy_keV >= search_min) & (energy_keV <= search_max)
    search_energies = energy_keV[search_mask]
    search_spectrum = spectrum[search_mask]
    
    if len(search_spectrum) == 0:
        print(f"Warning: No data in scatter search region {search_min:.1f} - {search_max:.1f} keV")
        return {'elastic_peak': None, 'compton_peak': None, 'exclusion_zones': []}
    
    # Find peaks in the search region
    peaks, properties = find_peaks(search_spectrum, 
                                  prominence=min_prominence,
                                  distance=5)
    
    if len(peaks) == 0:
        print(f"No scatter peaks found in region {search_min:.1f} - {search_max:.1f} keV")
        return {'elastic_peak': None, 'compton_peak': None, 'exclusion_zones': []}
    
    # Get peak energies and heights
    peak_energies = search_energies[peaks]
    peak_heights = search_spectrum[peaks]
    peak_prominences = properties['prominences']
    
    print(f"\nScatter Peak Detection:")
    print(f"  Incident energy: {incident_energy_keV:.1f} keV")
    print(f"  Expected Compton energy (90°): {expected_compton_energy:.1f} keV")
    print(f"  Search region: {search_min:.1f} - {search_max:.1f} keV")
    print(f"  Found {len(peaks)} candidate peaks")
    
    # Identify elastic peak (closest to incident energy)
    elastic_peak = None
    elastic_distance = float('inf')
    elastic_idx = None
    
    for i, peak_energy in enumerate(peak_energies):
        distance = abs(peak_energy - incident_energy_keV)
        if distance < elastic_distance:
            elastic_distance = distance
            elastic_peak = {
                'energy_keV': peak_energy,
                'height': peak_heights[i],
                'prominence': peak_prominences[i],
                'distance_from_incident': distance
            }
            elastic_idx = i
    
    # Identify Compton peak
    compton_peak = None
    compton_distance = float('inf')
    max_compton_separation = 0.4  # keV
    
    for i, peak_energy in enumerate(peak_energies):
        if i == elastic_idx:
            continue
        
        # Compton must be lower energy than elastic
        if elastic_peak and peak_energy >= elastic_peak['energy_keV']:
            continue
        
        # Compton must be close to elastic
        if elastic_peak:
            elastic_compton_separation = elastic_peak['energy_keV'] - peak_energy
            if elastic_compton_separation > max_compton_separation:
                continue
        
        distance = abs(peak_energy - expected_compton_energy)
        if distance < compton_distance:
            compton_distance = distance
            compton_peak = {
                'energy_keV': peak_energy,
                'height': peak_heights[i], 
                'prominence': peak_prominences[i],
                'distance_from_expected': distance,
                'separation_from_elastic': elastic_compton_separation if elastic_peak else None
            }
    
    # Print identification results
    if elastic_peak:
        print(f"  → Elastic peak: {elastic_peak['energy_keV']:.2f} keV (δ = {elastic_peak['distance_from_incident']:.2f} keV)")
    if compton_peak:
        print(f"  → Compton peak: {compton_peak['energy_keV']:.2f} keV (δ = {compton_peak['distance_from_expected']:.2f} keV)")
        print(f"    Separation from elastic: {compton_peak['separation_from_elastic']:.3f} keV")
    
    # Create exclusion zones
    exclusion_zones = []
    exclusion_width_keV = 0.5
    
    if elastic_peak:
        elastic_zone = (elastic_peak['energy_keV'] - exclusion_width_keV,
                       elastic_peak['energy_keV'] + exclusion_width_keV)
        exclusion_zones.append(('elastic', elastic_zone))
        print(f"  → Elastic exclusion zone: {elastic_zone[0]:.2f} - {elastic_zone[1]:.2f} keV")
    
    if compton_peak:
        compton_zone = (compton_peak['energy_keV'] - 1.0,
                       compton_peak['energy_keV'] + exclusion_width_keV)
        exclusion_zones.append(('compton', compton_zone))
        print(f"  → Compton exclusion zone: {compton_zone[0]:.2f} - {compton_zone[1]:.2f} keV")
    
    return {
        'elastic_peak': elastic_peak,
        'compton_peak': compton_peak,
        'exclusion_zones': exclusion_zones,
        'search_region': (search_min, search_max),
        'expected_compton_energy': expected_compton_energy,
        'all_peaks_in_region': list(zip(peak_energies, peak_heights))
    }


def detect_and_identify_xrf_peaks(results, 
                                 thresholds=[10, 50, 10],
                                 tolerance_keV=0.060,
                                 smooth_window=5,
                                 bkg_method='rolling_ball',
                                 bkg_radius=50,
                                 detect_scatter=True):
    """
    Comprehensive XRF peak detection using combined lines with detector resolution
    
    Parameters:
    -----------
    results : dict
        Results dictionary from corrections
    thresholds : list
        [height, distance_eV, prominence]
    tolerance_keV : float
        Energy tolerance for line matching (default 60 eV)
    smooth_window : int
        Smoothing window size
    bkg_method : str
        Background subtraction method ('rolling_ball', 'polynomial', 'none')
    bkg_radius : int
        Background filter radius
    detect_scatter : bool
        Whether to detect and exclude scatter peaks
        
    Returns:
    --------
    dict : Detection results with peaks, candidates, and scatter info
    """
    # Get data
    energy = results['energy_axis']
    energy_keV = energy / 1000.0
    normalized = results['normalized_spectrum'][0]  # (41496, 4, 4096)
    eV_per_channel = results['eV_per_channel']
    
    # Get maximum envelope spectrum
    max_spectrum = normalized.max(axis=(0, 1))
    
    # Limit to reasonable XRF energy range
    incident_energy = results['dcm_energy_ev']
    avg_incident_energy = np.mean(incident_energy)
    energy_limit = 1.1 * avg_incident_energy / 1000.0
    
    mask = energy_keV <= energy_limit
    energy_slice = energy_keV[mask]
    spectrum_slice = max_spectrum[mask]
    
    print(f"Analysis range: 0 - {energy_limit:.1f} keV")
    print(f"Data points in range: {len(spectrum_slice)}")
    
    # Step 1: Background subtraction
    if bkg_method == 'rolling_ball':
        background = minimum_filter1d(spectrum_slice, size=bkg_radius)
        background = uniform_filter1d(background, size=bkg_radius//2)
    elif bkg_method == 'polynomial':
        coeffs = np.polyfit(range(len(spectrum_slice)), spectrum_slice, deg=3)
        background = np.polyval(coeffs, range(len(spectrum_slice)))
    else:
        background = np.zeros_like(spectrum_slice)
    
    bkg_subtracted = spectrum_slice - background
    bkg_subtracted = np.maximum(bkg_subtracted, 0)
    
    # Step 2: Smoothing
    if smooth_window > 1:
        smoothed = uniform_filter1d(bkg_subtracted, size=smooth_window)
    else:
        smoothed = bkg_subtracted
    
    # Step 3: Scatter peak detection and exclusion
    scatter_results = None
    if detect_scatter:
        print(f"\n" + "="*50)
        print("SCATTER PEAK DETECTION")
        print("="*50)
        avg_incident_energy_keV = avg_incident_energy / 1000.0
        scatter_results = detect_scatter_peaks(energy_slice, smoothed, 
                                             avg_incident_energy_keV, 
                                             search_window_keV=3.0)
        
        # Create exclusion mask
        xrf_detection_mask = np.ones(len(energy_slice), dtype=bool)
        
        for scatter_type, (energy_min, energy_max) in scatter_results['exclusion_zones']:
            exclusion_mask = (energy_slice >= energy_min) & (energy_slice <= energy_max)
            xrf_detection_mask = xrf_detection_mask & ~exclusion_mask
            excluded_count = np.sum(exclusion_mask)
            print(f"  → Excluding {excluded_count} points for {scatter_type} scatter")
        
        print(f"  → Total excluded: {np.sum(~xrf_detection_mask)}/{len(xrf_detection_mask)} points")
    else:
        xrf_detection_mask = np.ones(len(energy_slice), dtype=bool)
    
    # Step 4: XRF Peak detection
    print(f"\n" + "="*50)
    print("XRF PEAK DETECTION")
    print("="*50)
    
    height_threshold = thresholds[0]
    distance_keV = thresholds[1] / 1000.0
    prominence_threshold = thresholds[2]
    
    distance_channels = int(distance_keV / (eV_per_channel / 1000.0))
    
    # Apply exclusion mask
    masked_spectrum = smoothed.copy()
    masked_spectrum[~xrf_detection_mask] = 0
    
    peaks, properties = find_peaks(masked_spectrum,
                                  height=height_threshold,
                                  distance=distance_channels,
                                  prominence=prominence_threshold)
    
    # Filter peaks in excluded regions
    valid_peaks = [peak for peak in peaks if xrf_detection_mask[peak]]
    peaks = np.array(valid_peaks)
    peak_energies_keV = energy_slice[peaks] if len(peaks) > 0 else np.array([])
    peak_heights = smoothed[peaks] if len(peaks) > 0 else np.array([])
    
    print(f"Found {len(peaks)} XRF peaks (after scatter exclusion):")
    for i, (energy_val, height) in enumerate(zip(peak_energies_keV, peak_heights)):
        print(f"  Peak {i+1}: {energy_val:.3f} keV (height: {height:.1f})")
    
    # Step 5: XRF line identification
    candidate_lines_dict = {}
    avg_incident_energy_keV = avg_incident_energy / 1000.0
    
    for peak_energy in peak_energies_keV:
        candidates = find_combined_xrf_lines(peak_energy, tolerance_keV, avg_incident_energy_keV)
        candidate_lines_dict[peak_energy] = candidates
        
        print(f"\nXRF Peak at {peak_energy:.3f} keV:")
        if candidates:
            for candidate in candidates:
                print(f"  → {candidate}")
        else:
            print(f"  → No physically possible XRF matches within {tolerance_keV*1000:.0f} eV tolerance")
    
    return {
        'energy_slice_keV': energy_slice,
        'original_spectrum': spectrum_slice,
        'background': background,
        'bkg_subtracted': bkg_subtracted,
        'smoothed_spectrum': smoothed,
        'xrf_detection_mask': xrf_detection_mask,
        'peak_indices': peaks,
        'peak_energies_keV': peak_energies_keV,
        'peak_heights': peak_heights,
        'candidate_lines': candidate_lines_dict,
        'scatter_results': scatter_results,
        'parameters': {
            'thresholds': thresholds,
            'tolerance_keV': tolerance_keV,
            'smooth_window': smooth_window,
            'bkg_method': bkg_method,
            'energy_range_keV': (0, energy_limit),
            'resolution_eV': 120,
            'detect_scatter': detect_scatter
        }
    }


def find_combined_xrf_lines(energy_keV, tolerance, incident_energy_keV):
    """
    Find combined XRF lines near given energy using physics-based filtering
    
    Parameters:
    -----------
    energy_keV : float
        Peak energy to match
    tolerance : float
        Energy tolerance in keV
    incident_energy_keV : float
        Incident beam energy in keV
        
    Returns:
    --------
    list : Formatted candidate strings with efficiency info
    """
    candidates = []
    
    for element, combined_lines in COMBINED_XRF_LINES.items():
        for line_name, line_energy, yield_val in combined_lines:
            if abs(line_energy - energy_keV) <= tolerance:
                # Extract line family
                parts = line_name.split()
                if len(parts) >= 2:
                    element_symbol = parts[0]
                    line_family = parts[1]
                    
                    # Check if line can be excited
                    edge_energy = get_absorption_edge_energy(element_symbol, line_family)
                    if edge_energy is None or incident_energy_keV <= edge_energy:
                        continue
                    
                    # Calculate excitation efficiency
                    efficiency = calculate_excitation_efficiency(element_symbol, line_family, incident_energy_keV)
                    
                    if efficiency > 0.01:
                        candidates.append({
                            'line_name': line_name,
                            'line_energy': line_energy,
                            'edge_energy': edge_energy,
                            'efficiency': efficiency,
                            'energy_diff': abs(line_energy - energy_keV)
                        })
    
    # Sort by excitation efficiency
    candidates.sort(key=lambda x: x['efficiency'], reverse=True)
    
    # Format output strings
    formatted_candidates = []
    for candidate in candidates:
        formatted_candidates.append(
            f"{candidate['line_name']} ({candidate['line_energy']:.3f} keV, eff: {candidate['efficiency']:.2f})"
        )
    
    return formatted_candidates