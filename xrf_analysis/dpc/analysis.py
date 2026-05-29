"""
Differential Phase Contrast (DPC) Analysis Functions
Handles beam deflection calculations and visualization
"""
import numpy as np
import matplotlib.pyplot as plt


def calculate_dpc_deflections(thor_x, thor_y, thor_Tot, i0, Lx=10, Ly=10):
    """
    Calculate DPC beam deflection positions
    
    Parameters:
    -----------
    thor_x : array
        X-direction Thor detector signal
    thor_y : array
        Y-direction Thor detector signal
    thor_Tot : array
        Total Thor detector signal
    i0 : array
        Incident beam intensity
    Lx : float
        Detector length in X (mm), default 10 mm for PDP90A
    Ly : float
        Detector length in Y (mm), default 10 mm for PDP90A
        
    Returns:
    --------
    dict : Dictionary containing beam_x, beam_y, and phase gradients
    """
    # Calculate actual beam deflection positions
    beam_x = (Lx * (thor_x[0][:] / i0[0][:])) / (2 * (thor_Tot[0][:] / i0[0][:]))
    beam_y = (Ly * (thor_y[0][:] / i0[0][:])) / (2 * (thor_Tot[0][:] / i0[0][:]))
    
    # For now, beam_x and beam_y ARE the phase gradients
    phase_gradient_x = beam_x
    phase_gradient_y = beam_y
    
    return {
        'beam_x': beam_x,
        'beam_y': beam_y,
        'phase_gradient_x': phase_gradient_x,
        'phase_gradient_y': phase_gradient_y
    }


def plot_dpc_results(abs_x, abs_y, beam_x, beam_y, thor_Tot, figsize=(6, 18)):
    """
    Plot DPC deflection results
    
    Parameters:
    -----------
    abs_x : array
        X positions
    abs_y : array
        Y positions
    beam_x : array
        X-component of beam deflection
    beam_y : array
        Y-component of beam deflection
    thor_Tot : array
        Total intensity
    figsize : tuple
        Figure size (width, height)
    """
    # Calculate deflection magnitude
    deflection_mag = np.sqrt(beam_x**2 + beam_y**2)
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    # Deflection magnitude
    axes[0,0].scatter(abs_x[0], abs_y[0], c=deflection_mag, s=3, alpha=0.66, cmap='gray')
    axes[0,0].set_title('Deflection Magnitude')
    axes[0,0].set_xlabel('abs_x')
    axes[0,0].set_ylabel('abs_y')
    plt.colorbar(axes[0,0].collections[0], ax=axes[0,0])
    
    # X-component of deflection
    axes[0,1].scatter(abs_x[0], abs_y[0], c=beam_x, s=3, alpha=0.66, cmap='RdBu_r')
    axes[0,1].set_title('X Deflection')
    axes[0,1].set_xlabel('abs_x')
    axes[0,1].set_ylabel('abs_y')
    plt.colorbar(axes[0,1].collections[0], ax=axes[0,1])
    
    # Y-component of deflection
    axes[1,0].scatter(abs_x[0], abs_y[0], c=beam_y, s=3, alpha=0.66, cmap='RdBu_r')
    axes[1,0].set_title('Y Deflection')
    axes[1,0].set_xlabel('abs_x')
    axes[1,0].set_ylabel('abs_y')
    plt.colorbar(axes[1,0].collections[0], ax=axes[1,0])
    
    # Total intensity
    axes[1,1].scatter(abs_x[0], abs_y[0], c=thor_Tot, s=3, alpha=0.66, cmap='hot')
    axes[1,1].set_title('Total Intensity')
    axes[1,1].set_xlabel('abs_x')
    axes[1,1].set_ylabel('abs_y')
    plt.colorbar(axes[1,1].collections[0], ax=axes[1,1])
    
    plt.tight_layout()
    plt.show()