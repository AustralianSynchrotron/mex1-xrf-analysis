"""
Data Correction Functions
Handles deadtime correction, i0 normalization, and energy calibration
"""
import numpy as np
import h5py


def correct_xrf_data(file_path):
    """
    Apply deadtime correction and i0 normalization to XRF data
    
    Parameters:
    -----------
    file_path : str
        Path to HDF5 file containing XRF data
        
    Returns:
    --------
    dict : Dictionary containing corrected data and metadata
    """
    with h5py.File(file_path, 'r') as f:
        # Load the data
        spectrum = f['spectrum'][:]  # type: ignore (1, 41496, 4, 4096) type: ignore
        dtfactor = f['DTFactor'][:]  # type: ignore  (1, 4, 41496) 
        i0 = f['i0'][:]  # type: ignore (1, 41496)
        abs_x = f['abs_x'][:] # type: ignore
        abs_y = f['abs_y'][:] # type: ignore
        dcm_energy_ev = f['dcm_energy_ev'][:]  # type: ignore Incident energy
        
        print(f"Original spectrum shape: {spectrum.shape}") # type: ignore
        print(f"DTFactor shape: {dtfactor.shape}") # type: ignore
        print(f"i0 shape: {i0.shape}") # type: ignore
        print(f"Incident energy shape: {dcm_energy_ev.shape}") # type: ignore
    
    # Reshape DTFactor to align with spectrum dimensions
    # From (1, 4, 41496) to (1, 41496, 4, 1) for broadcasting
    dtfactor_aligned = dtfactor.transpose(0, 2, 1)  # type: ignore (1, 41496, 4)
    dtfactor_aligned = dtfactor_aligned[..., np.newaxis]  # (1, 41496, 4, 1)
    
    print(f"DTFactor aligned shape: {dtfactor_aligned.shape}")
    
    # Step 1: Apply deadtime correction
    corrected_spectrum = spectrum * dtfactor_aligned
    print("✓ Deadtime correction applied")
    
    # Step 2: Normalize by i0
    # Reshape i0 for broadcasting: (1, 41496) -> (1, 41496, 1, 1)
    i0_aligned = i0[..., np.newaxis, np.newaxis]  # type: ignore (1, 41496, 1, 1)
    normalized_spectrum = corrected_spectrum / i0_aligned
    print("✓ i0 normalization applied")
    
    return {
        'raw_spectrum': spectrum,
        'corrected_spectrum': corrected_spectrum, 
        'normalized_spectrum': normalized_spectrum,
        'dtfactor': dtfactor,
        'i0': i0,
        'abs_x': abs_x,
        'abs_y': abs_y,
        'dcm_energy_ev': dcm_energy_ev
    }


def apply_energy_calibration(results, eV_per_channel=10, energy_offset=0):
    """
    Apply energy calibration to XRF data results.
    
    Parameters:
    -----------
    results : dict
        Results dictionary from correct_xrf_data()
    eV_per_channel : float
        Energy per channel (default 10 eV)
    energy_offset : float  
        Energy offset in eV (default 0 eV)
    
    Returns:
    --------
    dict : Updated results with energy calibration added
    """
    # Get spectrum shape to determine number of channels
    spectrum_shape = results['normalized_spectrum'].shape
    n_channels = spectrum_shape[-1]  # Last dimension is energy channels
    
    # Create energy axis
    energy_axis = np.linspace(
        energy_offset, 
        energy_offset + eV_per_channel * (n_channels - 1), 
        n_channels
    )
    
    # Add energy calibration info to results
    results['energy_axis'] = energy_axis
    results['eV_per_channel'] = eV_per_channel
    results['energy_offset'] = energy_offset
    results['energy_range_eV'] = (energy_axis[0], energy_axis[-1])
    
    print(f"Energy calibration applied:")
    print(f"  Channels: {n_channels}")
    print(f"  Energy range: {energy_axis[0]:.0f} - {energy_axis[-1]:.0f} eV")
    print(f"  Energy step: {eV_per_channel} eV/channel")
    print(f"  Energy offset: {energy_offset} eV")
    
    return results