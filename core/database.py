"""
XRF Line Database
Pre-calculates and manages combined XRF lines considering detector resolution
"""

try:
    import xraylib as xrl # type: ignore
except ImportError:
    print("Warning: xraylib not installed. Database functions will not work.")
    xrl = None


# Module-level dictionary for pre-calculated combined XRF lines
COMBINED_XRF_LINES = {}


def calculate_combined_xrf_lines(element_symbol, resolution_eV=120):
    """
    Calculate combined XRF lines considering detector resolution
    Only calculates relevant lines based on element weight
    
    Parameters:
    -----------
    element_symbol : str
        Element symbol
    resolution_eV : float
        Detector energy resolution in eV (default 120 eV)
        
    Returns:
    --------
    list : List of (line_name, energy_keV, yield) tuples
    """
    if xrl is None:
        return []
        
    try:
        z = xrl.SymbolToAtomicNumber(element_symbol)
    except:
        return []
    
    raw_lines = []
    
    # Define which elements should use K, L, or M edges
    k_edge_elements = [
        'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 
        'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 
        'Ga', 'Ge', 'As', 'Se', 'Br'
    ]
    
    l_edge_elements = [
        'Br', 'Zr', 'Mo', 'Pd', 'Ag', 'Cd', 'I',
        'La', 'Ce', 'Sm', 'Eu', 'Gd', 'Lu',
        'W', 'Ir', 'Pt', 'Au', 'Hg', 'Pb'
    ]
    
    m_edge_elements = ['U']
    
    # Calculate K lines for K-edge elements
    if element_symbol in k_edge_elements:
        k_lines = [
            ('Ka1', xrl.KA1_LINE),
            ('Ka2', xrl.KA2_LINE), 
            ('Kb1', xrl.KB1_LINE),
            ('Kb3', xrl.KB3_LINE)
        ]
        
        for line_name, line_code in k_lines:
            try:
                energy = xrl.LineEnergy(z, line_code)
                yield_val = xrl.RadRate(z, line_code)
                if energy > 0 and yield_val > 0:
                    raw_lines.append((line_name, energy, yield_val))
            except:
                continue
    
    # Calculate L lines for L-edge elements
    if element_symbol in l_edge_elements:
        l_lines = [
            ('La1', xrl.LA1_LINE),
            ('La2', xrl.LA2_LINE),
            ('Lb1', xrl.LB1_LINE),
            ('Lb2', xrl.LB2_LINE),
            ('Lb3', xrl.LB3_LINE),
            ('Lb4', xrl.LB4_LINE)
        ]
        
        for line_name, line_code in l_lines:
            try:
                energy = xrl.LineEnergy(z, line_code)
                yield_val = xrl.RadRate(z, line_code)
                if energy > 0 and yield_val > 0:
                    raw_lines.append((line_name, energy, yield_val))
            except:
                continue

    # Calculate M lines for M-edge elements
    if element_symbol in m_edge_elements:
        m_lines = [
            ('Ma1', xrl.MA1_LINE),
            ('Ma2', xrl.MA2_LINE),
            ('Mb', xrl.MB_LINE)
        ]
        
        for line_name, line_code in m_lines:
            try:
                energy = xrl.LineEnergy(z, line_code)
                yield_val = xrl.RadRate(z, line_code)
                if energy > 0 and yield_val > 0:
                    raw_lines.append((line_name, energy, yield_val))
            except:
                continue
    
    if not raw_lines:
        return []
    
    # Sort by energy
    raw_lines.sort(key=lambda x: x[1])
    
    # Group lines within resolution_eV
    combined_lines = []
    current_group = [raw_lines[0]]
    
    for i in range(1, len(raw_lines)):
        current_line = raw_lines[i]
        last_in_group = current_group[-1]
        
        if abs(current_line[1] - last_in_group[1]) <= resolution_eV/1000.0:
            current_group.append(current_line)
        else:
            if current_group:
                combined_line = process_line_group(current_group, element_symbol)
                if combined_line:
                    combined_lines.append(combined_line)
            current_group = [current_line]
    
    # Process final group
    if current_group:
        combined_line = process_line_group(current_group, element_symbol)
        if combined_line:
            combined_lines.append(combined_line)
    
    return combined_lines


def process_line_group(line_group, element_symbol):
    """
    Process a group of lines into a single combined line
    
    Parameters:
    -----------
    line_group : list
        List of (line_name, energy, yield) tuples
    element_symbol : str
        Element symbol
        
    Returns:
    --------
    tuple : (combined_name, weighted_energy, total_yield) or None
    """
    if not line_group:
        return None
    
    if len(line_group) == 1:
        line_name, energy, yield_val = line_group[0]
        # Simplify name (Ka1 -> Ka, La1 -> La, etc.)
        if line_name.startswith(('Ka', 'Kb', 'La', 'Lb', 'Ma', 'Mb')):
            family = line_name[:2]
        else:
            family = line_name
        return (f"{element_symbol} {family}", energy, yield_val)
    
    # Multiple lines - calculate weighted average
    total_yield = sum(line[2] for line in line_group)
    weighted_energy = sum(line[1] * line[2] for line in line_group) / total_yield
    
    # Determine combined name based on line families
    line_names = [line[0] for line in line_group]
    
    if any(name.startswith('Ka') for name in line_names):
        family = 'Ka'
    elif any(name.startswith('Kb') for name in line_names):
        family = 'Kb'  
    elif any(name.startswith('La') for name in line_names):
        family = 'La'
    elif any(name.startswith('Lb') for name in line_names):
        family = 'Lb'
    elif any(name.startswith('Ma1') for name in line_names):
        family = 'Ma'
    elif any(name.startswith('Mb') for name in line_names):
        family = 'Mb'
    else:
        family = 'X'
    
    return (f"{element_symbol} {family}", weighted_energy, total_yield)


def initialize_combined_xrf_database():
    """
    Pre-calculate combined XRF lines for common elements
    Call this once at startup
    """
    global COMBINED_XRF_LINES
    
    if xrl is None:
        print("Cannot initialize database: xraylib not available")
        return
    
    # K-edge elements
    k_elements = [
        'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 
        'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 
        'Ga', 'Ge', 'As', 'Se', 'Br'
    ]
    
    # L-edge elements  
    l_elements = [
        'Br', 'Zr', 'Mo', 'Pd', 'Ag', 'Cd', 'I',
        'La', 'Ce', 'Sm', 'Eu', 'Gd', 'Lu',
        'W', 'Ir', 'Pt', 'Au', 'Hg', 'Pb'
    ]
    
    # M-edge elements  
    m_elements = ['U']
    
    all_elements = k_elements + l_elements + m_elements
    
    print("Initializing combined XRF line database...")
    for element in all_elements:
        try:
            combined_lines = calculate_combined_xrf_lines(element)
            COMBINED_XRF_LINES[element] = combined_lines
            print(f"  {element}: {len(combined_lines)} combined lines")
        except Exception as e:
            print(f"  {element}: Error - {e}")
            COMBINED_XRF_LINES[element] = []
    
    print(f"Database initialized with {len(all_elements)} elements.")