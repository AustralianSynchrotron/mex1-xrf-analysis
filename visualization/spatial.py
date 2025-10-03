"""
Spatial Distribution Visualization Functions
Handles plotting of element distributions and scan patterns
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, PowerNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable

from ..core.physics import calculate_compton_energy
from ..core.database import COMBINED_XRF_LINES


def analyze_scan_pattern(results):
    """
    Analyze the scan pattern to understand the 2D grid structure
    
    Parameters:
    -----------
    results : dict
        Results dictionary from corrections
        
    Returns:
    --------
    tuple : (ny, nx, unique_x, unique_y)
    """
    abs_x = results['abs_x']
    abs_y = results['abs_y']
    
    print(f"Total measurement points: {len(abs_x)}")
    print(f"abs_x range: {abs_x.min():.3f} to {abs_x.max():.3f}")
    print(f"abs_y range: {abs_y.min():.3f} to {abs_y.max():.3f}")
    
    # Find unique positions
    unique_x = np.unique(abs_x)
    unique_y = np.unique(abs_y)
    
    print(f"Unique X positions: {len(unique_x)}")
    print(f"Unique Y positions: {len(unique_y)}")
    print(f"Expected grid size: {len(unique_x)} × {len(unique_y)} = {len(unique_x) * len(unique_y)}")
    
    # Check if it's a complete rectangular grid
    if len(unique_x) * len(unique_y) == len(abs_x):
        print("✓ Complete rectangular grid detected")
        return len(unique_y), len(unique_x), unique_x, unique_y
    else:
        print("⚠ Irregular or incomplete grid")
        return None, None, unique_x, unique_y


def plot_element_distribution(results, element_name, line_family='Ka', 
                             integration_width_keV=0.15, sensor_sum=True, 
                             point_size=10, scale='linear', 
                             correct_45deg=False, expand_x=True):
    """
    Plot spatial distribution with true spatial scaling (1 mm = 1 mm)
    
    Parameters:
    -----------
    results : dict
        Results dictionary from corrections
    element_name : str
        Element symbol or 'elastic'/'compton'
    line_family : str
        Line family ('Ka', 'Kb', 'La', 'Lb')
    integration_width_keV : float
        Integration width around peak
    sensor_sum : bool
        Sum all 4 sensors (True) or use sensor 0 only
    point_size : int
        Scatter plot point size
    scale : str
        Color scale ('linear', 'log', 'sqrt')
    correct_45deg : bool
        Apply 45° geometry correction
    expand_x : bool
        Expand x-coords (True) or compress (False)
        
    Returns:
    --------
    array : Element intensities
    """
    # Get data
    energy_axis = results['energy_axis'] / 1000.0
    normalized = results['normalized_spectrum'][0]
    abs_x = results['abs_x']
    abs_y = results['abs_y']
    
    # Apply 45° geometry correction if requested
    if correct_45deg:
        correction_factor = np.sqrt(2)
        if expand_x:
            abs_x_corrected = abs_x * correction_factor
            x_label = 'abs_x (corrected: sample surface)'
            correction_note = f'X coords expanded by √2 = {correction_factor:.3f}'
        else:
            abs_x_corrected = abs_x / correction_factor  
            x_label = 'abs_x (corrected: beam projection)'
            correction_note = f'X coords compressed by 1/√2 = {1/correction_factor:.3f}'
    else:
        abs_x_corrected = abs_x
        x_label = 'abs_x (position)'
        correction_note = 'No geometry correction'
    
    # Handle scatter peaks vs XRF lines
    if element_name.lower() == 'elastic':
        incident_energy = results['dcm_energy_ev']
        target_energy = np.mean(incident_energy) / 1000.0
        target_line_name = "Elastic Scatter"
        print(f"Mapping {target_line_name} at {target_energy:.3f} keV")
        
    elif element_name.lower() == 'compton':
        incident_energy = results['dcm_energy_ev']
        avg_incident_energy_keV = np.mean(incident_energy) / 1000.0
        target_energy = calculate_compton_energy(avg_incident_energy_keV, 90)
        target_line_name = "Compton Scatter"
        print(f"Mapping {target_line_name} at {target_energy:.3f} keV (90° scattering)")
        
    else:
        target_line_name = f"{element_name} {line_family}"
        target_energy = None
        
        if element_name in COMBINED_XRF_LINES:
            for line_name, line_energy, yield_val in COMBINED_XRF_LINES[element_name]:
                if line_name == target_line_name:
                    target_energy = line_energy
                    break
        
        if target_energy is None:
            print(f"Error: Could not find {target_line_name} in XRF database")
            return None
        
        print(f"Mapping {target_line_name} at {target_energy:.3f} keV")
    
    # Integration
    energy_min = target_energy - integration_width_keV
    energy_max = target_energy + integration_width_keV
    energy_mask = (energy_axis >= energy_min) & (energy_axis <= energy_max)
    
    if sensor_sum:
        summed_spectra = normalized.sum(axis=1)
        element_intensities = summed_spectra[:, energy_mask].sum(axis=1)
        title_suffix = " (4 sensors)"
    else:
        element_intensities = normalized[:, 0, energy_mask].sum(axis=1)
        title_suffix = " (sensor 0)"
    
    # Handle color scaling
    if scale.lower() == 'log':
        min_positive = element_intensities[element_intensities > 0].min() if np.any(element_intensities > 0) else 1e-6
        plot_intensities = np.where(element_intensities <= 0, min_positive/10, element_intensities)
        norm = LogNorm(vmin=plot_intensities.min(), vmax=plot_intensities.max())
        scale_label = "Log Scale"
    elif scale.lower() == 'sqrt':
        plot_intensities = element_intensities
        if np.any(plot_intensities < 0):
            plot_intensities = plot_intensities - plot_intensities.min()
        norm = PowerNorm(gamma=0.5, vmin=plot_intensities.min(), vmax=plot_intensities.max())
        scale_label = "Sqrt Scale"
    else:
        plot_intensities = element_intensities
        norm = None
        scale_label = "Linear Scale"
    
    # Calculate data ranges for true spatial scaling
    x_range = abs_x_corrected.max() - abs_x_corrected.min()
    y_range = abs_y.max() - abs_y.min()
    data_aspect_ratio = x_range / y_range
    
    # Set figure size
    base_size = 10
    if data_aspect_ratio > 1:
        fig_width = base_size
        fig_height = base_size / data_aspect_ratio
    else:
        fig_width = base_size * data_aspect_ratio
        fig_height = base_size
    
    fig_width = max(fig_width, 6)
    fig_height = max(fig_height, 4)
          
    plt.figure(figsize=(fig_width, fig_height))
    
    # Scatter plot
    scatter = plt.scatter(abs_x_corrected, abs_y, c=plot_intensities, s=point_size, 
                         cmap='jet', alpha=0.33, edgecolors='none', norm=norm)
    
    ax = plt.gca()
    ax.set_aspect('equal', adjustable='box')
    
    ax.set_xlabel(x_label)
    ax.set_ylabel('abs_y (position)')
    ax.set_title(f'{target_line_name} Distribution{title_suffix}\n'
                 f'Energy: {target_energy:.3f} ± {integration_width_keV:.3f} keV\n'
                 f'{correction_note}')
    ax.grid(True, alpha=0.3)
    
    # Create colorbar
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    cbar = plt.colorbar(scatter, cax=cax)
    cbar.set_label(f'Integrated Counts ({scale_label})', rotation=270, labelpad=20)
  
    print(f"Scan area: {x_range:.2f} × {y_range:.2f} units (1:1 aspect ratio)")
    print(f"Data aspect ratio: {data_aspect_ratio:.2f}")
    print(f"Intensity range: {element_intensities.min():.1f} - {element_intensities.max():.1f}")
    
    plt.tight_layout()
    plt.show()
    
    return element_intensities


def plot_element_distribution_tripcolor(results, element_name, line_family='Ka', 
                             integration_width_keV=0.15, sensor_sum=True, 
                             scale='linear', correct_45deg=False, expand_x=True):
    """
    Plot spatial distribution using triangular interpolation (tripcolor)
    Similar to plot_element_distribution but uses tripcolor instead of scatter
    
    Parameters are the same as plot_element_distribution
    """
    # Get data
    energy_axis = results['energy_axis'] / 1000.0
    normalized = results['normalized_spectrum'][0]
    abs_x = results['abs_x'][0]
    abs_y = results['abs_y'][0]
    
    # Apply 45° geometry correction if requested
    if correct_45deg:
        correction_factor = np.sqrt(2)
        if expand_x:
            abs_x_corrected = abs_x * correction_factor
            x_label = 'abs_x (corrected: sample surface)'
            correction_note = f'X coords expanded by √2 = {correction_factor:.3f}'
        else:
            abs_x_corrected = abs_x / correction_factor  
            x_label = 'abs_x (corrected: beam projection)'
            correction_note = f'X coords compressed by 1/√2 = {1/correction_factor:.3f}'
    else:
        abs_x_corrected = abs_x
        x_label = 'abs_x (position)'
        correction_note = 'No geometry correction'
    
    # Handle scatter peaks vs XRF lines (same as plot_element_distribution)
    if element_name.lower() == 'elastic':
        incident_energy = results['dcm_energy_ev']
        target_energy = np.mean(incident_energy) / 1000.0
        target_line_name = "Elastic Scatter"
        
    elif element_name.lower() == 'compton':
        incident_energy = results['dcm_energy_ev']
        avg_incident_energy_keV = np.mean(incident_energy) / 1000.0
        target_energy = calculate_compton_energy(avg_incident_energy_keV, 90)
        target_line_name = "Compton Scatter"
        
    else:
        target_line_name = f"{element_name} {line_family}"
        target_energy = None
        
        if element_name in COMBINED_XRF_LINES:
            for line_name, line_energy, yield_val in COMBINED_XRF_LINES[element_name]:
                if line_name == target_line_name:
                    target_energy = line_energy
                    break
        
        if target_energy is None:
            print(f"Error: Could not find {target_line_name} in XRF database")
            return None
    
    # Integration
    energy_min = target_energy - integration_width_keV
    energy_max = target_energy + integration_width_keV
    energy_mask = (energy_axis >= energy_min) & (energy_axis <= energy_max)
    
    if sensor_sum:
        summed_spectra = normalized.sum(axis=1)
        element_intensities = summed_spectra[:, energy_mask].sum(axis=1)
        title_suffix = " (4 sensors)"
    else:
        element_intensities = normalized[:, 0, energy_mask].sum(axis=1)
        title_suffix = " (sensor 0)"
    
    # Handle color scaling
    if scale.lower() == 'log':
        min_positive = element_intensities[element_intensities > 0].min() if np.any(element_intensities > 0) else 1e-6
        plot_intensities = np.where(element_intensities <= 0, min_positive/10, element_intensities)
        norm = LogNorm(vmin=plot_intensities.min(), vmax=plot_intensities.max())
        scale_label = "Log Scale"
    elif scale.lower() == 'sqrt':
        plot_intensities = element_intensities
        if np.any(plot_intensities < 0):
            plot_intensities = plot_intensities - plot_intensities.min()
        norm = PowerNorm(gamma=0.5, vmin=plot_intensities.min(), vmax=plot_intensities.max())
        scale_label = "Sqrt Scale"
    else:
        plot_intensities = element_intensities
        norm = None
        scale_label = "Linear Scale"
    
    # Calculate figure size
    x_range = abs_x_corrected.max() - abs_x_corrected.min()
    y_range = abs_y.max() - abs_y.min()
    data_aspect_ratio = x_range / y_range
    
    base_size = 10
    if data_aspect_ratio > 1:
        fig_width = base_size
        fig_height = base_size / data_aspect_ratio
    else:
        fig_width = base_size * data_aspect_ratio
        fig_height = base_size
    
    fig_width = max(fig_width, 6)
    fig_height = max(fig_height, 4)
          
    plt.figure(figsize=(fig_width, fig_height))
    
    # Tripcolor plot
    scatter = plt.tripcolor(abs_x_corrected, abs_y, plot_intensities, 
                           cmap='jet', alpha=0.66, edgecolors='none', norm=norm)

    ax = plt.gca()
    ax.set_aspect('equal', adjustable='box')
    
    ax.set_xlabel(x_label)
    ax.set_ylabel('abs_y (position)')
    ax.set_title(f'{target_line_name} Distribution{title_suffix}\n'
                 f'Energy: {target_energy:.3f} ± {integration_width_keV:.3f} keV\n'
                 f'{correction_note}')
    ax.grid(True, alpha=0.3)
    
    # Create colorbar
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    cbar = plt.colorbar(scatter, cax=cax)
    cbar.set_label(f'Integrated Counts ({scale_label})', rotation=270, labelpad=20)
  
    print(f"Scan area: {x_range:.2f} × {y_range:.2f} units")
    print(f"Intensity range: {element_intensities.min():.1f} - {element_intensities.max():.1f}")
    
    plt.tight_layout()
    plt.show()
    
    return element_intensities