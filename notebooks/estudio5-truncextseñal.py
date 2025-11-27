
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

# %% ------- Plots -----------------------------------------------------------------------

#dict_extendido = func_deriv.extender_señal(ciclos_seleccionados, dict_ciclos_sep)

#func_deriv.dqdv_muchos_wl([ciclos_seleccionados[5]], dict_extendido)

#func_deriv.extender_señal_y_plot(ciclos_seleccionados, dict_ciclos_sep)

#func_deriv.truncar_señal_y_plot(ciclos_seleccionados, dict_ciclos_sep)

#func_deriv.detectar_cambios_resolucion([ciclos_seleccionados[5]],dict_ciclos_sep)

# ----- Trunco y luego grafico -----
dict_truncado = func_deriv.truncar_señal_y_plot(ciclos_seleccionados, dict_ciclos_sep)
func_deriv.plot_dqdv(ciclos_seleccionados, dict_truncado)
func_deriv.plot_dqdv_muchos_wl(ciclos_seleccionados, dict_truncado)

# %% ------- Pruebas -----------------------------------------------------------------------

# --- plot para varios wl ---
#func_deriv.dqdv_muchos_wl(indices_ciclos,dict_ciclos_sep)

# ----------- plot dvdq --------------
'''
dict = dict_ciclos_sep
indices_ciclos = ciclos_seleccionados

windowlength = 51  # Longitud de la ventana del filtro
polyorder = 3 # Orden del polinomio del filtro

# Graficar dQ/dV calculado
plt.figure(figsize=(8,5))
colors = cm.viridis(np.linspace(0, 1, len(indices_ciclos)))

for i, color in zip(indices_ciclos, colors):
    df_ch = dict_ciclos_sep[i]['Ch']
    df_dis = dict_ciclos_sep[i]['Dis']

    Q_ch = df_ch['Q'].values
    V_ch = df_ch['CellV'].values

    Q_dis = df_dis['Q'].values
    V_dis = df_dis['CellV'].values

    # Aplica filtro Savitzky-Golay (smooth de la señal)
    df_ch['Q_ch_savgol'] = savgol_filter(Q_ch, window_length=windowlength, polyorder=polyorder)
    df_ch['V_ch_savgol'] = savgol_filter(V_ch, window_length=windowlength, polyorder=polyorder)
    df_dis['Q_dis_savgol'] = savgol_filter(Q_dis, window_length=windowlength, polyorder=polyorder)
    df_dis['V_dis_savgol'] = savgol_filter(V_dis, window_length=windowlength, polyorder=polyorder)
    
    Q_ch_savgol = df_ch['Q_ch_savgol'].values
    V_ch_savgol = df_ch['V_ch_savgol'].values
    dqdv_ch_calc = np.gradient(V_ch_savgol,Q_ch_savgol)
    dqdv_ch = dqdv_ch_calc
    
    Q_dis_savgol = df_dis['Q_dis_savgol'].values
    V_dis_savgol = df_dis['V_dis_savgol'].values

    Q_dis_min = Q_dis_savgol.min()

    #plt.plot(V_dis_savgol,Q_dis_savgol-Q_dis_min, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
    
    dqdv_dis_calc = np.gradient(V_dis_savgol,Q_dis_savgol)
    dqdv_dis = dqdv_dis_calc

    #plt.plot(V_ch, dqdv_ch, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
    plt.plot(V_dis, dqdv_dis, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')

    '''
'''
    # para ver el tamaño de window_length
    #print(V_dis)
    salto_prom_1 = np.mean(np.abs(np.diff(V_dis))) # Promedio del salto (paso) entre elementos consecutivos
    print(f"Salto promedio entre elementos consecutivos de arr1: {salto_prom_1:.4f} V")
    ventana_en_volt = 0.002  # 2 mV
    window_length = int(np.round(ventana_en_volt / salto_prom_1))
    print(f"Ventana de suavizado: {window_length} puntos")

    #print(V_dis_savgol)
    #salto_prom_2 = np.mean(np.abs(np.diff(V_dis_savgol)))
    #print(f"Salto promedio entre elementos consecutivos de arr2: {salto_prom_2}")

    # Asegurate de que sea impar
    if window_length % 2 == 0:
        window_length += 1

    #print(f"Ventana de suavizado: {window_length} puntos")
    '''
'''
# Crear colorbar asociada a los ciclos
#norm = mcolors.Normalize(vmin=min(ciclos), vmax=max(ciclos))
#sm = cm.ScalarMappable(cmap=cm.viridis, norm=norm)
#sm.set_array([])  # requerido
#cbar = plt.colorbar(sm, ax=plt.gca(), ticks=ciclos[::2])
#cbar.set_label('Cycle number')

plt.xlabel('Voltage (V)')
plt.ylabel('dV/dQ (V/mAh)')
plt.title(f'dV/dQ wl={windowlength}, po={polyorder}')
plt.grid(True)
plt.legend()
plt.show()

'''