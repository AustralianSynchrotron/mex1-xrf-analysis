"""
Test script to verify XRF analysis package installation
Run this after installing the package to check if everything works
"""
import sys

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    
    try:
        import numpy
        print("  ✓ numpy")
    except ImportError as e:
        print(f"  ✗ numpy: {e}")
        return False
    
    try:
        import scipy
        print("  ✓ scipy")
    except ImportError as e:
        print(f"  ✗ scipy: {e}")
        return False
    
    try:
        import matplotlib
        print("  ✓ matplotlib")
    except ImportError as e:
        print(f"  ✗ matplotlib: {e}")
        return False
    
    try:
        import h5py
        print("  ✓ h5py")
    except ImportError as e:
        print(f"  ✗ h5py: {e}")
        return False
    
    try:
        import xraylib #type: ignore
        print("  ✓ xraylib")
    except ImportError as e:
        print(f"  ✗ xraylib: {e}")
        print("     Note: Install with 'pip install xraylib'")
        return False
    
    return True


def test_package_import():
    """Test if xrf_analysis package can be imported"""
    print("\nTesting package import...")
    
    try:
        import xrf_analysis
        print("  ✓ xrf_analysis package")
    except ImportError as e:
        print(f"  ✗ xrf_analysis: {e}")
        print("     Run 'pip install -e .' in the package directory")
        return False
    
    # Test submodules
    try:
        from xrf_analysis import core
        print("  ✓ xrf_analysis.core")
    except ImportError as e:
        print(f"  ✗ xrf_analysis.core: {e}")
        return False
    
    try:
        from xrf_analysis import visualization
        print("  ✓ xrf_analysis.visualization")
    except ImportError as e:
        print(f"  ✗ xrf_analysis.visualization: {e}")
        return False
    
    try:
        from xrf_analysis import dpc
        print("  ✓ xrf_analysis.dpc")
    except ImportError as e:
        print(f"  ✗ xrf_analysis.dpc: {e}")
        return False
    
    return True


def test_core_functions():
    """Test if core functions are accessible"""
    print("\nTesting core functions...")
    
    try:
        import xrf_analysis as xrf
        
        # Test function availability
        functions = [
            'correct_xrf_data',
            'apply_energy_calibration',
            'initialize_combined_xrf_database',
            'detect_and_identify_xrf_peaks'
        ]
        
        for func_name in functions:
            if hasattr(xrf, func_name):
                print(f"  ✓ {func_name}")
            else:
                print(f"  ✗ {func_name} not found")
                return False
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    
    return True


def test_database_initialization():
    """Test if XRF database can be initialized"""
    print("\nTesting XRF database initialization...")
    
    try:
        import xrf_analysis as xrf
        
        # This will print initialization messages
        xrf.initialize_combined_xrf_database()
        
        # Check if database has entries
        if len(xrf.core.COMBINED_XRF_LINES) > 0:
            print(f"  ✓ Database initialized with {len(xrf.core.COMBINED_XRF_LINES)} elements")
            return True
        else:
            print("  ✗ Database is empty")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_physics_calculations():
    """Test basic physics calculations"""
    print("\nTesting physics calculations...")
    
    try:
        from xrf_analysis.core import physics #type: ignore
        
        # Test Compton energy calculation
        compton_energy = physics.calculate_compton_energy(10.0, 90)
        if 9.0 < compton_energy < 10.0:
            print(f"  ✓ Compton energy calculation: {compton_energy:.3f} keV")
        else:
            print(f"  ✗ Unexpected Compton energy: {compton_energy:.3f} keV")
            return False
        
        # Test edge energy lookup
        fe_ka_edge = physics.get_absorption_edge_energy('Fe', 'Ka')
        if fe_ka_edge and 7.0 < fe_ka_edge < 8.0:
            print(f"  ✓ Fe K-edge: {fe_ka_edge:.3f} keV")
        else:
            print(f"  ✗ Unexpected Fe K-edge: {fe_ka_edge}")
            return False
        
        # Test excitation efficiency
        efficiency = physics.calculate_excitation_efficiency('Fe', 'Ka', 10.0)
        if 0 <= efficiency <= 1.0:
            print(f"  ✓ Fe Ka excitation efficiency at 10 keV: {efficiency:.3f}")
        else:
            print(f"  ✗ Invalid efficiency: {efficiency}")
            return False
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """Run all tests"""
    print("="*60)
    print("XRF Analysis Package Installation Test")
    print("="*60)
    
    all_passed = True
    
    # Run tests
    all_passed &= test_imports()
    all_passed &= test_package_import()
    all_passed &= test_core_functions()
    all_passed &= test_database_initialization()
    all_passed &= test_physics_calculations()
    
    # Summary
    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("\nYour installation is working correctly!")
        print("You can now use the package:")
        print("  - Command line: xrf-analyze --help")
        print("  - Python: import xrf_analysis as xrf")
    else:
        print("✗ SOME TESTS FAILED")
        print("\nPlease check the errors above and:")
        print("  1. Install missing dependencies")
        print("  2. Verify package installation: pip install -e .")
        print("  3. Check Python path")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())