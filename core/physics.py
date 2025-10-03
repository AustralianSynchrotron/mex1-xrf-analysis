"""
XRF Physics Functions
Handles absorption edges, excitation efficiency, and scatter calculations
"""
import numpy as np

try:
    import xraylib as xrl #type: ignore
except ImportError:
    print("Warning: xraylib not installed. Some functions will not work.")
    xrl = None


def get_absorption_edge_energy(element_symbol, line_family):
    """
    Get absorption edge energy for a given element and line family
    
    Parameters:
    -----------
    element_symbol : str
        Element symbol (e.g., 'Fe', 'Cu')
    line_family : str
        Line family ('Ka', 'Kb', 'La', 'Lb')
        
    Returns:
    --------
    float : Absorption edge energy in keV, or None if not available
    """
    if xrl is None:
        return None
        
    try:
        z = xrl.SymbolToAtomicNumber(element_symbol)
        
        # Map line families to absorption edges
        line_edge_map = {
            'Ka': xrl.K_SHELL,
            'Kb': xrl.K_SHELL, 
            'La': xrl.L3_SHELL,
            'Lb': xrl.L3_SHELL
        }
        
        if line_family in line_edge_map:
            edge_energy = xrl.EdgeEnergy(z, line_edge_map[line_family])
            return edge_energy if edge_energy > 0 else None
        else:
            return None
            
    except:
        return None


def calculate_excitation_efficiency(element_symbol, line_family, incident_energy_keV):
    """
    Calculate relative excitation efficiency for XRF line using shell-specific physics
    
    Parameters:
    -----------
    element_symbol : str
        Element symbol
    line_family : str  
        Line family ('Ka', 'Kb', 'La', 'Lb')
    incident_energy_keV : float
        Incident photon energy in keV
        
    Returns:
    --------
    float : Relative excitation efficiency (0-1), or 0 if cannot excite
    """
    if xrl is None:
        return 0.0
        
    # Get absorption edge energy
    edge_energy = get_absorption_edge_energy(element_symbol, line_family)
    
    if edge_energy is None or incident_energy_keV <= edge_energy:
        return 0.0  # Cannot excite
    
    try:
        z = xrl.SymbolToAtomicNumber(element_symbol)
        
        # Map line families to shells for cross-section calculation
        line_shell_map = {
            'Ka': xrl.K_SHELL,
            'Kb': xrl.K_SHELL, 
            'La': xrl.L3_SHELL,
            'Lb': xrl.L3_SHELL
        }
        
        if line_family not in line_shell_map:
            return 0.0
        
        shell = line_shell_map[line_family]
        
        # Calculate shell-specific photoelectric cross-section
        partial_cross_section = xrl.CS_Photo_Partial(z, shell, incident_energy_keV)
        
        # Get fluorescence yield for this shell
        fluorescence_yield = xrl.FluorYield(z, shell)
        
        # Combined excitation efficiency
        efficiency = partial_cross_section * fluorescence_yield
        
        # Normalize to reasonable scale
        normalized_efficiency = efficiency / 10.0
        
        # Cap at 1.0 for relative efficiency display
        return min(normalized_efficiency, 1.0)
        
    except Exception as e:
        print(f"Warning: Could not calculate efficiency for {element_symbol} {line_family}: {e}")
        return 0.01


def calculate_compton_energy(incident_energy_keV, scattering_angle_deg=90):
    """
    Calculate Compton scattered photon energy
    
    Parameters:
    -----------
    incident_energy_keV : float
        Incident photon energy in keV
    scattering_angle_deg : float
        Scattering angle in degrees (default 90°)
    
    Returns:
    --------
    float : Compton scattered energy in keV
    """
    # Electron rest mass energy in keV
    electron_rest_energy = 511.0  # keV
    
    # Convert angle to radians
    theta_rad = np.radians(scattering_angle_deg)
    
    # Compton scattering formula
    compton_energy = incident_energy_keV / (
        1 + (incident_energy_keV / electron_rest_energy) * (1 - np.cos(theta_rad))
    )
    
    return compton_energy