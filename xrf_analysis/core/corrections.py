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
        abs_x = f['abs_x'][:].flatten() # type: ignore
        abs_y = f['abs_y'][:].flatten() # type: ignore
        dcm_energy_ev = f['dcm_energy_ev'][:]  # type: ignore Incident energy
        
        print(f"Original spectrum shape: {spectrum.shape}") # type: ignore
        print(f"DTFactor shape: {dtfactor.shape}") # type: ignore
        print(f"i0 shape: {i0.shape}") # type: ignore
        print(f"Incident energy shape: {dcm_energy_ev.shape}") # type: ignore
    
    # Reshape DTFactor: (1, 4, N) -> (1, N, 4, 1) for broadcasting
    dtfactor_aligned = dtfactor.transpose(0, 2, 1)[..., np.newaxis].astype(np.float32)  # type: ignore
    i0_aligned = i0[..., np.newaxis, np.newaxis].astype(np.float32)  # type: ignore (1, N, 1, 1)

    # Convert spectrum to float32 then apply corrections in-place.
    # This keeps peak memory ~2 GB instead of ~11 GB (avoids holding
    # spectrum + corrected + normalized simultaneously).
    normalized_spectrum = spectrum.astype(np.float32)  # type: ignore
    del spectrum

    normalized_spectrum *= dtfactor_aligned
    print("OK Deadtime correction applied")

    normalized_spectrum /= i0_aligned
    print("OK i0 normalization applied")

    return {
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