import numpy as np
import matplotlib.pyplot as plt
from fad.design.LineDesign import LineDesign
import time
import os



# NOTE: LineDesign has only been tested under FAD-Toolset commit from July 11, 2025 main branch
# and MoorPy commit from June 16, 2025 from dev branch. More significant testing is needed for
# different optimizers in this example script. However, we show a comparison below with COBYLA.
# This is in addition to updating the SciPy package version and updating the tests for changes
# in SciPy convergence criteria.

# NOTE: the below COBYLA run should not run for as long as it is running currently. It should 
# be much faster. Future development will address this issue.

# The goal of this example is to show how initial conditions work, especially with optimizers 
# like COBYLA. Some optimizers need some attention to what their initial conditions are and 
# how that influences the overall optimization performance. Other optimizers can be used in 
# LineDesign too, but are not shown here because there needs to be more tests set up





__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
moorprops_file = os.path.join(__location__ , 'MoorProps_LineDesign.yaml')


# output results function
def getResults(X, ld):
    X = np.asarray(X, dtype=float)
    X_denorm = X * np.asarray(ld.X_denorm, dtype=float)

    print('\n--- Optimization Results ---')
    print('Normalized design variables:   ', [f'{x:8.4f}' for x in X])
    print('Denormalized design variables: ', [f'{x:8.3f}' for x in X_denorm])

    if 'xe' in ld.log and len(ld.log['xe']) > 0:
        print(f"Internal solver line length result: {ld.log['xe'][-1]:.3f} m")
    else:
        print('Internal solver line length result: n/a')

    print('\nConstraint evaluations (value >= 0 is feasible):')
    for i, con in enumerate(ld.constraints):
        name = con.get('name', f'constraint_{i}')
        value = float(con.get('value', np.nan))
        threshold = con.get('threshold', 'n/a')
        offset = con.get('offset', 'n/a')
        print(f"  {name:<22s} value={value:9.3f}  threshold={threshold}  offset={offset}")

    print('\nCost breakdown:')
    print(f"  Mooring line cost ($k): {ld.lineCost/1e3:,.2f}")
    print(f"  Anchor cost ($k):       {ld.anchorCost/1e3:,.2f}")
    print(f"  Total cost ($k):        {ld.cost/1e3:,.2f}")
    print(f"  Iterations:             {ld.iter}")





# set up the settings dictionary for a COBYLA optimization of a DEA-Chain-Rope configuration
depth = 200

settings = {}
settings['rBFair'] = [58,0,-14]
settings['x_ampl'] = 10
settings['fx_target'] = 1.95e6
settings['headings'] = [60, 180, 300]

settings['solve_for'] = 'none'
settings['x_target'] = 35
settings['x_mean_out'] = 35
settings['x_mean_in'] = 60



# Chain-Rope: DEA-Chain-Rope
settings['name'] = 'DEA-chain-rope'
settings['lineTypeNames'] = ['chain','polyester']
settings['anchorType'] = 'drag-embedment'



settings['solve_for'] = 'none'
settings['allVars'] = [750/10, 400, 100, 0, 300, 180]
settings['Xindices'] = [0, 1, 2, 'c', 3, 4]
settings['Xmin'] = [10, 10, 10, 10, 10]
settings['Xmax'] = [500, 1500, 300, 1000, 300]
settings['dX_last'] = [10, 10, 10, 10, 10]

settings['constraints'] = [dict(name='min_lay_length', index=0, threshold=20, offset='max'),
                           dict(name='max_offset'    , index=0, threshold=60, offset='min'),
                           dict(name='max_offset'    , index=0, threshold=35, offset='max'),
                           dict(name='rope_contact'  , index=1, threshold=5 , offset='min')]
for j in range(len(settings['lineTypeNames'])):
    settings['constraints'].append(dict(name='tension_safety_factor', index=j, threshold=2.0, offset='max'))


# set up the LineDesign object and optimize
ld = LineDesign(depth, lineProps=moorprops_file, **settings)

ld.setNormalization()

X, min_cost = ld.optimize(maxIter=4000, plot=False, display=3, stepfac=4, method='COBYLA')

getResults(X, ld)
ld.plotProfile()
plt.show()



# Notice how the result did not converge -- this is due to the behavior of the COBYLA optimizer

# If we adjust the initial conditions to an area of the design space, COBYLA has an easier time finding a solution


# simply adjust the initial conditions to the optimizer
settings['allVars'] = [750/10, 600, 100, 0, 100, 180]

# recreate the LineDesign object (there have been some instances where LineDesign does not behave the same when optimized multiple times)
ld = LineDesign(depth, lineProps=moorprops_file, **settings)

ld.setNormalization()

X, min_cost = ld.optimize(maxIter=4000, plot=False, display=3, stepfac=4, method='COBYLA')

getResults(X, ld)
ld.plotProfile()
plt.show()



# TRY OUT YOUR OWN OPTIMIZER!










# FUNCTION TO SAVE LONG LINEDESIGN RESULTS TO CSV/EXCEL
import pandas as pd


def save_results_ga_style(ld, filepath='Section2Results_GA.xlsx'):
    """Save optimization history using design variables from log['x'] and constraints from log['g'].
    
    Dynamically handles any number of design variables and constraints by iterating through
    log entries and extracting columns based on actual log dimensions.
    
    Parameters
    ----------
    ld : LineDesign
        LineDesign object after optimization with populated log
    filepath : str
        Path to save Excel file (default: 'Section2Results_GA.xlsx')
    """
    if not ld.log['x'] or len(ld.log['x']) == 0:
        print('Warning: No optimization history found in log.')
        return
    
    savedict_list = []
    n_vars = np.array(ld.log['x']).shape[1] if len(ld.log['x']) > 0 else 0
    n_constraints = np.array(ld.log['g']).shape[1] if len(ld.log['g']) > 0 and np.array(ld.log['g']).ndim > 1 else 0
    
    for i in range(len(ld.log['x'])):
        savedict = {}
        
        # Add design variables dynamically
        for j in range(n_vars):
            savedict[f'x{j}'] = np.array(ld.log['x'])[i, j]
        
        # Add objective function (cost)
        if ld.log['f'] and i < len(ld.log['f']):
            cost_val = ld.log['f'][i]
            savedict['cost'] = cost_val[0] if isinstance(cost_val, (list, np.ndarray)) else cost_val
        
        # Add constraints dynamically using names from ld.constraints if available
        for j in range(n_constraints):
            if ld.constraints and j < len(ld.constraints):
                constraint_name = ld.constraints[j].get('name', f'constraint_{j}')
                col_name = f'g_{constraint_name}'
            else:
                col_name = f'g{j}'
            
            savedict[col_name] = np.array(ld.log['g'])[i, j]
        
        savedict_list.append(savedict)
    
    df = pd.DataFrame(savedict_list)
    df.to_excel(filepath, index=False)
    print(f'Saved GA-style results to: {filepath}')


def save_results_solvefor_style(ld, filepath='Section2Results_SLSQP.xlsx'):
    """Save optimization history using alternate log sources (log['a'], log['xe'], log['x'], log['g']).
    
    This style uses internally-solved values (anchor spacing 'a' and external length 'xe')
    combined with design variables from log['x']. Handles any number of available constraints.
    
    Parameters
    ----------
    ld : LineDesign
        LineDesign object after optimization with populated log
    filepath : str
        Path to save Excel file (default: 'Section2Results_SLSQP.xlsx')
    """
    if not ld.log['x'] or len(ld.log['x']) == 0:
        print('Warning: No optimization history found in log.')
        return
    
    savedict_list = []
    n_vars = np.array(ld.log['x']).shape[1] if len(ld.log['x']) > 0 else 0
    n_constraints = np.array(ld.log['g']).shape[1] if len(ld.log['g']) > 0 and np.array(ld.log['g']).ndim > 1 else 0
    
    for i in range(len(ld.log['x'])):
        savedict = {}
        
        # Add internal variables (anchor spacing 'a' and external length 'xe')
        if ld.log['a'] and i < len(ld.log['a']):
            savedict['A'] = np.array(ld.log['a'][i])
        if ld.log['xe'] and i < len(ld.log['xe']):
            savedict['L1'] = np.array(ld.log['xe'][i])
        
        # Add remaining design variables dynamically (typically D2, L2, D3, etc.)
        for j in range(n_vars):
            savedict[f'x{j}'] = np.array(ld.log['x'])[i, j]
        
        # Add objective function (cost)
        if ld.log['f'] and i < len(ld.log['f']):
            cost_val = ld.log['f'][i]
            savedict['cost'] = cost_val[0] if isinstance(cost_val, (list, np.ndarray)) else cost_val
        
        # Add constraints dynamically using names from ld.constraints if available
        for j in range(n_constraints):
            if ld.constraints and j < len(ld.constraints):
                constraint_name = ld.constraints[j].get('name', f'constraint_{j}')
                col_name = f'g_{constraint_name}'
            else:
                col_name = f'g{j}'
            
            savedict[col_name] = np.array(ld.log['g'])[i, j]
        
        savedict_list.append(savedict)
    
    df = pd.DataFrame(savedict_list)
    df.to_excel(filepath, index=False)
    print(f'Saved solve_for-style results to: {filepath}')


# Example usage:
# save_results_ga_style(ld, filepath)
# save_results_solvefor_style(ld, filepath)
