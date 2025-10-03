"""
Command-line interface for XRF analysis
"""
import argparse
import sys
import os

from . import core, visualization, dpc # type: ignore


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='XRF Analysis Toolkit - Analyze X-ray fluorescence data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full analysis workflow
  xrf-analyze process data.h5 --plot-all
  
  # Custom peak detection
  xrf-analyze detect-peaks data.h5 --height 20 --prominence 15
  
  # Element mapping
  xrf-analyze map-element data.h5 Fe Ka --scale log
  
  # DPC analysis
  xrf-analyze dpc data.h5
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # =========================================================================
    # PROCESS command - full workflow
    # =========================================================================
    process_parser = subparsers.add_parser(
        'process',
        help='Complete analysis workflow (correct → calibrate → detect → plot)'
    )
    process_parser.add_argument('file', help='Path to HDF5 data file')
    process_parser.add_argument(
        '--eV-per-channel', type=float, default=10,
        help='Energy per channel (default: 10 eV)'
    )
    process_parser.add_argument(
        '--energy-offset', type=float, default=0,
        help='Energy offset in eV (default: 0 eV)'
    )
    process_parser.add_argument(
        '--height', type=float, default=10,
        help='Peak height threshold (default: 10)'
    )
    process_parser.add_argument(
        '--distance', type=float, default=50,
        help='Minimum peak distance in eV (default: 50 eV)'
    )
    process_parser.add_argument(
        '--prominence', type=float, default=10,
        help='Peak prominence threshold (default: 10)'
    )
    process_parser.add_argument(
        '--tolerance', type=float, default=60,
        help='XRF line matching tolerance in eV (default: 60 eV)'
    )
    process_parser.add_argument(
        '--smooth-window', type=int, default=5,
        help='Smoothing window size (default: 5)'
    )
    process_parser.add_argument(
        '--bkg-method', choices=['rolling_ball', 'polynomial', 'none'], 
        default='rolling_ball',
        help='Background subtraction method (default: rolling_ball)'
    )
    process_parser.add_argument(
        '--bkg-radius', type=int, default=50,
        help='Background filter radius (default: 50)'
    )
    process_parser.add_argument(
        '--no-scatter', action='store_true',
        help='Disable scatter peak detection and exclusion'
    )
    process_parser.add_argument(
        '--plot-all', action='store_true',
        help='Generate all plots (spectrum + peak detection)'
    )
    process_parser.add_argument(
        '--y-min', type=float, default=0.1,
        help='Minimum y-axis value for log plots (default: 0.1)'
    )
    
    # =========================================================================
    # DETECT-PEAKS command - peak detection only
    # =========================================================================
    detect_parser = subparsers.add_parser(
        'detect-peaks',
        help='Detect and identify XRF peaks'
    )
    detect_parser.add_argument('file', help='Path to HDF5 data file')
    detect_parser.add_argument(
        '--eV-per-channel', type=float, default=10,
        help='Energy per channel (default: 10 eV)'
    )
    detect_parser.add_argument(
        '--height', type=float, default=10,
        help='Peak height threshold (default: 10)'
    )
    detect_parser.add_argument(
        '--distance', type=float, default=50,
        help='Minimum peak distance in eV (default: 50 eV)'
    )
    detect_parser.add_argument(
        '--prominence', type=float, default=10,
        help='Peak prominence threshold (default: 10)'
    )
    detect_parser.add_argument(
        '--tolerance', type=float, default=60,
        help='XRF line matching tolerance in eV (default: 60 eV)'
    )
    detect_parser.add_argument(
        '--smooth-window', type=int, default=5,
        help='Smoothing window size (default: 5)'
    )
    detect_parser.add_argument(
        '--no-scatter', action='store_true',
        help='Disable scatter peak detection'
    )
    detect_parser.add_argument(
        '--plot', action='store_true',
        help='Generate detection plots'
    )
    detect_parser.add_argument(
        '--y-min', type=float, default=0.1,
        help='Minimum y-axis value for plots (default: 0.1)'
    )
    
    # =========================================================================
    # MAP-ELEMENT command - spatial distribution
    # =========================================================================
    map_parser = subparsers.add_parser(
        'map-element',
        help='Create spatial distribution map for an element'
    )
    map_parser.add_argument('file', help='Path to HDF5 data file')
    map_parser.add_argument('element', help='Element symbol (e.g., Fe, Cu) or "elastic"/"compton"')
    map_parser.add_argument('line', nargs='?', default='Ka', help='Line family (default: Ka)')
    map_parser.add_argument(
        '--eV-per-channel', type=float, default=10,
        help='Energy per channel (default: 10 eV)'
    )
    map_parser.add_argument(
        '--width', type=float, default=0.15,
        help='Integration width in keV (default: 0.15 keV)'
    )
    map_parser.add_argument(
        '--scale', choices=['linear', 'log', 'sqrt'], default='linear',
        help='Color scale (default: linear)'
    )
    map_parser.add_argument(
        '--sensor', choices=['all', '0', '1', '2', '3'], default='all',
        help='Sensor selection (default: all)'
    )
    map_parser.add_argument(
        '--point-size', type=int, default=10,
        help='Scatter plot point size (default: 10)'
    )
    map_parser.add_argument(
        '--correct-45deg', action='store_true',
        help='Apply 45° geometry correction'
    )
    map_parser.add_argument(
        '--compress-x', action='store_true',
        help='Compress x-coords instead of expanding (with --correct-45deg)'
    )
    map_parser.add_argument(
        '--tripcolor', action='store_true',
        help='Use tripcolor interpolation instead of scatter plot'
    )
    
    # =========================================================================
    # DPC command - differential phase contrast
    # =========================================================================
    dpc_parser = subparsers.add_parser(
        'dpc',
        help='Perform DPC (differential phase contrast) analysis'
    )
    dpc_parser.add_argument('file', help='Path to HDF5 data file')
    dpc_parser.add_argument(
        '--Lx', type=float, default=10,
        help='Detector length in X (mm) (default: 10 mm)'
    )
    dpc_parser.add_argument(
        '--Ly', type=float, default=10,
        help='Detector length in Y (mm) (default: 10 mm)'
    )
    dpc_parser.add_argument(
        '--plot', action='store_true',
        help='Generate DPC plots'
    )
    
    # =========================================================================
    # PLOT-SPECTRUM command - spectrum visualization
    # =========================================================================
    plot_parser = subparsers.add_parser(
        'plot-spectrum',
        help='Plot XRF spectra'
    )
    plot_parser.add_argument('file', help='Path to HDF5 data file')
    plot_parser.add_argument(
        '--eV-per-channel', type=float, default=10,
        help='Energy per channel (default: 10 eV)'
    )
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    # Initialize XRF database for commands that need it
    if args.command in ['process', 'detect-peaks']:
        print("Initializing XRF line database...")
        core.initialize_combined_xrf_database()
        print()
    
    # Execute command
    if args.command == 'process':
        process_command(args)
    elif args.command == 'detect-peaks':
        detect_peaks_command(args)
    elif args.command == 'map-element':
        map_element_command(args)
    elif args.command == 'dpc':
        dpc_command(args)
    elif args.command == 'plot-spectrum':
        plot_spectrum_command(args)


def process_command(args):
    """Execute full analysis workflow"""
    print(f"Processing file: {args.file}")
    print("="*60)
    
    # Step 1: Load and correct data
    print("\n[1/4] Loading and correcting data...")
    results = core.correct_xrf_data(args.file)
    
    # Step 2: Apply energy calibration
    print("\n[2/4] Applying energy calibration...")
    results = core.apply_energy_calibration(
        results,
        eV_per_channel=args.eV_per_channel,
        energy_offset=args.energy_offset
    )
    
    # Step 3: Plot spectrum (if requested)
    if args.plot_all:
        print("\n[3/4] Plotting spectra...")
        visualization.plot_spectrum_with_energy(results)
    else:
        print("\n[3/4] Skipping spectrum plot (use --plot-all to enable)")
    
    # Step 4: Detect peaks
    print("\n[4/4] Detecting and identifying peaks...")
    detection_results = core.detect_and_identify_xrf_peaks(
        results,
        thresholds=[args.height, args.distance, args.prominence],
        tolerance_keV=args.tolerance / 1000.0,
        smooth_window=args.smooth_window,
        bkg_method=args.bkg_method,
        bkg_radius=args.bkg_radius,
        detect_scatter=not args.no_scatter
    )
    
    # Plot detection results (if requested)
    if args.plot_all:
        print("\nPlotting peak detection results...")
        visualization.plot_peak_detection_results(detection_results, y_min=args.y_min)
    
    print("\n" + "="*60)
    print("Processing complete!")


def detect_peaks_command(args):
    """Execute peak detection"""
    print(f"Detecting peaks in: {args.file}")
    print("="*60)
    
    # Load and correct
    print("\nLoading and correcting data...")
    results = core.correct_xrf_data(args.file)
    
    print("\nApplying energy calibration...")
    results = core.apply_energy_calibration(results, eV_per_channel=args.eV_per_channel)
    
    # Detect peaks
    print("\nDetecting and identifying peaks...")
    detection_results = core.detect_and_identify_xrf_peaks(
        results,
        thresholds=[args.height, args.distance, args.prominence],
        tolerance_keV=args.tolerance / 1000.0,
        smooth_window=args.smooth_window,
        detect_scatter=not args.no_scatter
    )
    
    if args.plot:
        visualization.plot_peak_detection_results(detection_results, y_min=args.y_min)
    
    print("\nPeak detection complete!")


def map_element_command(args):
    """Execute element mapping"""
    print(f"Mapping {args.element} {args.line} distribution")
    print("="*60)
    
    # Load and correct
    print("\nLoading and correcting data...")
    results = core.correct_xrf_data(args.file)
    
    print("\nApplying energy calibration...")
    results = core.apply_energy_calibration(results, eV_per_channel=args.eV_per_channel)
    
    # Initialize database if needed for element mapping
    if args.element.lower() not in ['elastic', 'compton']:
        print("\nInitializing XRF database...")
        core.initialize_combined_xrf_database()
    
    # Determine sensor sum
    sensor_sum = (args.sensor == 'all')
    
    # Create map
    print(f"\nCreating {args.scale} scale distribution map...")
    
    if args.tripcolor:
        intensities = visualization.plot_element_distribution_tripcolor(
            results,
            element_name=args.element,
            line_family=args.line,
            integration_width_keV=args.width,
            sensor_sum=sensor_sum,
            scale=args.scale,
            correct_45deg=args.correct_45deg,
            expand_x=not args.compress_x
        )
    else:
        intensities = visualization.plot_element_distribution(
            results,
            element_name=args.element,
            line_family=args.line,
            integration_width_keV=args.width,
            sensor_sum=sensor_sum,
            point_size=args.point_size,
            scale=args.scale,
            correct_45deg=args.correct_45deg,
            expand_x=not args.compress_x
        )
    
    print("\nElement mapping complete!")


def dpc_command(args):
    """Execute DPC analysis"""
    print(f"Performing DPC analysis on: {args.file}")
    print("="*60)
    
    import h5py
    
    # Load DPC-specific data
    print("\nLoading DPC data...")
    with h5py.File(args.file, 'r') as f:
        thor_x = f['thor_x'][:]     #type: ignore
        thor_y = f['thor_y'][:]     #type: ignore
        thor_Tot = f['thor_Tot'][:] #type: ignore
        i0 = f['i0'][:]             #type: ignore
        abs_x = f['abs_x'][:]       #type: ignore
        abs_y = f['abs_y'][:]       #type: ignore
    
    print(f"  thor_x shape: {thor_x.shape}")                            #type: ignore
    print(f"  thor_y shape: {thor_y.shape}")                            #type: ignore
    print(f"  thor_Tot shape: {thor_Tot.shape}")                        #type: ignore
    
    # Calculate deflections
    print("\nCalculating beam deflections...")
    dpc_results = dpc.calculate_dpc_deflections(
        thor_x, thor_y, thor_Tot, i0,
        Lx=args.Lx, Ly=args.Ly
    )
    
    print(f"  Beam deflection X range: {dpc_results['beam_x'].min():.3f} to {dpc_results['beam_x'].max():.3f}")
    print(f"  Beam deflection Y range: {dpc_results['beam_y'].min():.3f} to {dpc_results['beam_y'].max():.3f}")
    
    if args.plot:
        print("\nPlotting DPC results...")
        dpc.plot_dpc_results(
            abs_x, abs_y,
            dpc_results['beam_x'],
            dpc_results['beam_y'],
            thor_Tot
        )
    
    print("\nDPC analysis complete!")


def plot_spectrum_command(args):
    """Execute spectrum plotting"""
    print(f"Plotting spectrum from: {args.file}")
    print("="*60)
    
    # Load and correct
    print("\nLoading and correcting data...")
    results = core.correct_xrf_data(args.file)
    
    print("\nApplying energy calibration...")
    results = core.apply_energy_calibration(results, eV_per_channel=args.eV_per_channel)
    
    # Plot
    print("\nGenerating plots...")
    visualization.plot_spectrum_with_energy(results)
    
    print("\nPlotting complete!")


if __name__ == '__main__':
    main()