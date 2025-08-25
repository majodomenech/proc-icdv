from pathlib import Path
import numpy as np
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from scipy.signal import savgol_filter

import func_deriv as func_deriv
import func_plots as func_plots

# %% ------- Cargar ciclos ------------------------------------------------------------
input_folder = Path('/home/mariajose/proc-icdv/tmp')
nombre_archivo = "NMC-20"
output_folder = Path('/home/mariajose/proc-icdv/output')
output_folder.mkdir(parents=True, exist_ok=True)  # Create output directory if it doesn't exist

with open(input_folder / f'{nombre_archivo}.json') as f_json:
    raw_dict = json.load(f_json)

dict_ciclos_sep = {
    int(ciclo): {
        etapa: pd.DataFrame(data) for etapa, data in etapas.items()
    }
    for ciclo, etapas in raw_dict.items()
}

indices_ciclos = list(dict_ciclos_sep.keys())

# %% ------- Elegir ciclos ------------------------------------------------------------

# Elijo en todo el rango, equiespaciados
N_ciclos = 10  # Número de ciclos a tomar, si no se especifica, toma todos los del archivo
indices_ciclos_ = indices_ciclos[:-1] # Quito el último
indices_ciclos_array = np.array(indices_ciclos_)
ciclos_disponibles = sorted(dict_ciclos_sep.keys())
ciclos_seleccionados = indices_ciclos_array[np.linspace(0, len(indices_ciclos_array)-1, N_ciclos, dtype=int)]
#print("Ciclos seleccionados:", ciclos_seleccionados)
#print(f"son {len(ciclos_seleccionados)} ciclos")

# Elecciones rangos más pequeños
N1 = 115  # cantidad de ciclos hasta 99
N2 = 10  # cantidad de ciclos hasta 200
indices_hasta_99 = indices_ciclos_array[indices_ciclos_array <= 115]
#indices_hasta_200 = indices_ciclos_array[(indices_ciclos_array > 99) & (indices_ciclos_array <= 200)]
indices_hasta_200 = indices_ciclos_array[(indices_ciclos_array <= 200)]
#seleccion_99 = indices_hasta_99[np.linspace(0, len(indices_hasta_99)-1, N1, dtype=int)]
seleccion_99 = indices_hasta_99[np.linspace(2, len(indices_hasta_99)-1, dtype=int)]
seleccion_200 = indices_hasta_200[np.linspace(2, len(indices_hasta_200)-1, N2, dtype=int)]
#print("Ciclos hasta 99:", seleccion_99)
#print("Ciclos hasta 200:", seleccion_200)

#ciclos_seleccionados = indices_ciclos_array

# Elecciones manuales 
#ciclos_reducidos = [3, 21, 78, 153, 228, 303, 378, 453, 528, 603, 678, 753, 828]
#ciclos_seleccionados = [2, 99, 192, 300, 414, 504, 600, 702, 801, 897]
ciclos_seleccionados = [2, 21, 99, 198, 297, 396, 498, 597, 696, 795, 897]
ciclos_seleccionados = [21, 99, 198, 297, 396, 498, 597, 696, 795, 897]

# -----------------------------------------------------------------------------------------------------------------------------

# Grafico la dQdV directa de Bview
func_plots.plot_n_cycles(ciclos_seleccionados, dict_ciclos_sep, 'CellV', 'dCapacity/dCellV', nombre_grafico=nombre_archivo)

# Grafico la dQdV obtenida de hacer 1/dVdQ, con dVdQ directa de Bview
func_plots.plot_n_cycles(ciclos_seleccionados, dict_ciclos_sep, 'CellV', 'dCellV/dCapacity', nombre_grafico=nombre_archivo)


#func_plots.plot_n_cycles(ciclos_seleccionados, dict_ciclos_sep, 'Q', 'dCellV/dCapacity', nombre_grafico=nombre_archivo)#+'scatter')

#func_plots.plot_n_cycles(ciclos_seleccionados, dict_ciclos_sep, 'CellV', 'dCellV/dCapacity', nombre_grafico=nombre_archivo)#+'scatter')
#func_plots.plot_n_cycles(ciclos_seleccionados, dict_ciclos_sep, 'CellV', 'dCapacity/dCellV', nombre_grafico=nombre_archivo)#+'scatter')
#func_plots.plot_n_cycles(ciclos_seleccionados, dict_ciclos_sep, 'Q', 'dCellV/dCapacity', nombre_grafico=nombre_archivo)#+'scatter')

#func_deriv.resolucion_Q(ciclos_seleccionados,dict_ciclos_sep)
#func_deriv.plot_dvdq([ciclos_seleccionados[0]],dict_ciclos_sep)