"""
Spectrum Visualization Functions
Handles plotting of XRF spectra and peak detection results
"""
import numpy as np
import matplotlib.pyplot as plt


def plot_spectrum_with_energy(results, eV_per_channel=10):
    """
    Create two plots:
    1) Integrated spectra for all 4 sensors + mean
    2) Maximum envelope spectrum across all pixels/sensors
    
    Parameters:
    -----------
    results : dict
        Results dictionary from corrections
    eV_per_channel : float
        Energy per channel (for display)
    """
    # Get data
    energy = results['energy_axis']
    normalized = results['normalized_spectrum'][0]  # (41496, 4, 4096)
    
    # Get incident energy for plot limits
    incident_energy = results['dcm_energy_ev']
    avg_incident_energy = np.mean(incident_energy)
    energy_limit = 1.1 * avg_incident_energy
    mask = energy <= energy_limit
    
    print(f"Average incident energy: {avg_incident_energy:.0f} eV")
    print(f"Plot energy limit (1.1x): {energy_limit:.0f} eV")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Plot 1: Integrated spectra for each sensor + mean
    sensor_spectra = []
    colors = ['blue', 'red', 'green', 'orange']
    
    for sensor in range(4):
        integrated_spectrum = normalized[:, sensor, :].sum(axis=0)
        sensor_spectra.append(integrated_spectrum)
        
        ax1.plot(energy[mask], integrated_spectrum[mask], 
                color=colors[sensor], label=f'Sensor {sensor}', alpha=0.8)
    
    # Mean of all 4 sensors
    mean_spectrum = np.mean(sensor_spectra, axis=0)
    ax1.plot(energy[mask], mean_spectrum[mask], 
            color='black', linewidth=2, label='Mean (4 sensors)', linestyle='--')
    
    ax1.set_xlabel('Energy (eV)')
    ax1.set_ylabel('Integrated Counts')
    ax1.set_title('Integrated XRF Spectra (All Pixels)')
    ax1.set_xlim(0, energy_limit)
    ax1.set_yscale('log')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Maximum envelope spectrum
    max_spectrum = normalized.max(axis=(0, 1))
    
    ax2.plot(energy[mask], max_spectrum[mask], color='purple', linewidth=1.5)
    ax2.set_xlabel('Energy (eV)')
    ax2.set_ylabel('Maximum Counts')
    ax2.set_title('Maximum Envelope Spectrum (Across All Pixels & Sensors)')
    ax2.set_xlim(0, energy_limit)
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    print(f"\nSummary:")
    print(f"Total pixels: {normalized.shape[0]}")
    print(f"Energy channels: {normalized.shape[2]}")
    print(f"Max count in envelope: {max_spectrum.max():.2e}")


def plot_peak_detection_results(detection_results, y_min=0.1):
    """
    Plot the peak detection results with scatter peak visualization
    
    Parameters:
    -----------
    detection_results : dict
        Results from detect_and_identify_xrf_peaks()
    y_min : float
        Minimum y-axis value for log plots
    """
    # Extract data
    energy_keV = detection_results['energy_slice_keV']
    original = detection_results['original_spectrum']
    background = detection_results['background']
    bkg_subtracted = detection_results['bkg_subtracted']
    smoothed = detection_results['smoothed_spectrum']
    peak_energies = detection_results['peak_energies_keV']
    peak_heights = detection_results['peak_heights']
    candidate_lines = detection_results['candidate_lines']
    scatter_results = detection_results.get('scatter_results', None)
    xrf_mask = detection_results.get('xrf_detection_mask', np.ones(len(energy_keV), dtype=bool))
    
    # Determine consistent y-limits
    y_max = max(original.max(), bkg_subtracted.max(), smoothed.max())
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Plot 1: Original spectrum with background
    axes[0,0].plot(energy_keV, original, 'k-', alpha=0.8, linewidth=1, label='Original spectrum')
    axes[0,0].plot(energy_keV, background, 'r--', alpha=0.8, label='Background')
    
    # Add scatter peak markers
    if scatter_results:
        if scatter_results['elastic_peak']:
            elastic_energy = scatter_results['elastic_peak']['energy_keV']
            elastic_idx = np.argmin(np.abs(energy_keV - elastic_energy))
            axes[0,0].plot(elastic_energy, original[elastic_idx], 'bs', markersize=8, 
                          label='Elastic scatter')
        
        if scatter_results['compton_peak']:
            compton_energy = scatter_results['compton_peak']['energy_keV']
            compton_idx = np.argmin(np.abs(energy_keV - compton_energy))
            axes[0,0].plot(compton_energy, original[compton_idx], 'cs', markersize=8, 
                          label='Compton scatter')
    
    axes[0,0].set_xlabel('Energy (keV)')
    axes[0,0].set_ylabel('Counts')
    axes[0,0].set_title('Original Spectrum with Background & Scatter Peaks')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    axes[0,0].set_yscale('log')
    axes[0,0].set_ylim(y_min, y_max)
    
    # Plot 2: Background subtracted with exclusion zones
    axes[0,1].plot(energy_keV, bkg_subtracted, 'g-', alpha=0.7, label='Background subtracted')
    
    # Show exclusion zones
    if scatter_results and scatter_results['exclusion_zones']:
        for scatter_type, (energy_min, energy_max) in scatter_results['exclusion_zones']:
            color = 'lightblue' if scatter_type == 'elastic' else 'lightcyan'
            axes[0,1].axvspan(energy_min, energy_max, alpha=0.3, color=color, 
                             label=f'{scatter_type.capitalize()} exclusion')
    
    # Add XRF peak markers
    for peak_energy, peak_height in zip(peak_energies, peak_heights):
        axes[0,1].vlines(peak_energy, y_min, peak_height, colors='red', 
                        linestyles='--', alpha=0.8, linewidth=1)
        axes[0,1].plot(peak_energy, peak_height, 'ro', markersize=6)
    
    axes[0,1].set_xlabel('Energy (keV)')
    axes[0,1].set_ylabel('Counts')
    axes[0,1].set_title('Background Subtracted with Exclusion Zones & XRF Peaks')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)
    axes[0,1].set_yscale('log')
    axes[0,1].set_ylim(y_min, y_max)
    
    # Plot 3: Smoothed spectrum with peak identification
    axes[1,0].plot(energy_keV, smoothed, 'blue', alpha=0.8, linewidth=1.5, 
                   label='Smoothed spectrum')
    
    # Show excluded regions
    if scatter_results and scatter_results['exclusion_zones']:
        excluded_spectrum = smoothed.copy()
        excluded_spectrum[xrf_mask] = np.nan
        axes[1,0].plot(energy_keV, excluded_spectrum, 'gray', alpha=0.5, 
                      linewidth=2, label='Excluded (scatter)')
    
    # Add XRF peak lines and annotations
    for i, (peak_energy, peak_height) in enumerate(zip(peak_energies, peak_heights)):
        axes[1,0].vlines(peak_energy, y_min, peak_height, colors='red', 
                        linestyles='-', alpha=0.8, linewidth=1)
        axes[1,0].plot(peak_energy, peak_height, 'ro', markersize=8)
        axes[1,0].annotate(f'P{i+1}', 
                          xy=(peak_energy, peak_height), 
                          xytext=(5, 10), 
                          textcoords='offset points',
                          fontsize=10, 
                          color='darkred',
                          weight='bold')
    
    axes[1,0].set_xlabel('Energy (keV)')
    axes[1,0].set_ylabel('Counts')
    axes[1,0].set_title('Smoothed Spectrum with XRF Peak Identification')
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)
    axes[1,0].set_yscale('log')
    axes[1,0].set_ylim(y_min, y_max)
    
    # Plot 4: Element/transition labels
    axes[1,1].plot(energy_keV, smoothed, 'blue', alpha=0.6, linewidth=1, 
                   label='Smoothed spectrum')
    
    # Add detailed element/transition labels
    for i, peak_energy in enumerate(peak_energies):
        candidates = candidate_lines.get(peak_energy, [])
        
        if candidates:
            peak_height = peak_heights[i]
            axes[1,1].vlines(peak_energy, y_min, peak_height, colors='red', 
                            linestyles='-', alpha=0.8, linewidth=1)
            
            # Create label text from candidates
            label_lines = []
            for candidate in candidates[:2]:  # Top 2 matches
                try:
                    parts = candidate.split(' ')
                    element = parts[0]
                    transition = parts[1]
                    label_lines.append(f"{element} {transition}")
                except:
                    label_lines.append(candidate.split(' (')[0])
            
            # Position labels alternately
            y_offset = 20 if i % 2 == 0 else -30
            label_text = '\n'.join(label_lines)
            
            axes[1,1].annotate(label_text,
                              xy=(peak_energy, peak_height),
                              xytext=(0, y_offset),
                              textcoords='offset points',
                              ha='center',
                              fontsize=9,
                              color='darkblue',
                              weight='bold',
                              bbox=dict(boxstyle="round,pad=0.3", 
                                       facecolor="white", 
                                       edgecolor="darkblue",
                                       alpha=0.8))
    
    # Add scatter peak labels
    if scatter_results:
        if scatter_results['elastic_peak']:
            elastic_energy = scatter_results['elastic_peak']['energy_keV']
            elastic_idx = np.argmin(np.abs(energy_keV - elastic_energy))
            elastic_height = smoothed[elastic_idx]
            axes[1,1].annotate('Elastic\nScatter',
                              xy=(elastic_energy, elastic_height),
                              xytext=(0, 40),
                              textcoords='offset points',
                              ha='center',
                              fontsize=9,
                              color='darkblue',
                              weight='bold',
                              bbox=dict(boxstyle="round,pad=0.3", 
                                       facecolor="lightblue", 
                                       edgecolor="darkblue",
                                       alpha=0.8))
        
        if scatter_results['compton_peak']:
            compton_energy = scatter_results['compton_peak']['energy_keV']
            compton_idx = np.argmin(np.abs(energy_keV - compton_energy))
            compton_height = smoothed[compton_idx]
            axes[1,1].annotate('Compton\nScatter',
                              xy=(compton_energy, compton_height),
                              xytext=(0, 40),
                              textcoords='offset points',
                              ha='center',
                              fontsize=9,
                              color='darkcyan',
                              weight='bold',
                              bbox=dict(boxstyle="round,pad=0.3", 
                                       facecolor="lightcyan", 
                                       edgecolor="darkcyan",
                                       alpha=0.8))
    
    axes[1,1].set_xlabel('Energy (keV)')
    axes[1,1].set_ylabel('Counts')
    axes[1,1].set_title('Identified XRF Lines, Transitions & Scatter Peaks')
    axes[1,1].legend()
    axes[1,1].grid(True, alpha=0.3)
    axes[1,1].set_yscale('log')
    axes[1,1].set_ylim(y_min, y_max)
    
    plt.tight_layout()
    plt.show()
    
    # Print summary
    print(f"\n" + "="*60)
    print("PEAK DETECTION SUMMARY")
    print("="*60)
    
    if scatter_results:
        print("Scatter Peaks:")
        if scatter_results['elastic_peak']:
            elastic = scatter_results['elastic_peak']
            print(f"  Elastic: {elastic['energy_keV']:.2f} keV (height: {elastic['height']:.1f})")
        if scatter_results['compton_peak']:
            compton = scatter_results['compton_peak']
            print(f"  Compton: {compton['energy_keV']:.2f} keV (height: {compton['height']:.1f})")
        print()
    
    print(f"XRF Peaks: {len(peak_energies)} peaks found")
    for i, peak_energy in enumerate(peak_energies):
        candidates = candidate_lines.get(peak_energy, [])
        if candidates:
            print(f"  P{i+1} ({peak_energy:.3f} keV): {candidates[0]}")
        else:
            print(f"  P{i+1} ({peak_energy:.3f} keV): No XRF match")