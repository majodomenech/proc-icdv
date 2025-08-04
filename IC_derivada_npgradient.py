from pathlib import Path
import numpy as np
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import funciones_ic as f
from scipy.signal import savgol_filter

import func_deriv as func_deriv

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
dict = dict_ciclos_sep
indices_ciclos = ciclos_seleccionados

indices_ciclos = [21]
# Estudio resolucion y tamaño ventana
#func_deriv.resolucion(indices_ciclos,dict)

# Plot derivada con filtro
windowlength = 153  # Longitud de la ventana del filtro
polyorder = 3 # Orden del polinomio del filtro

def extend_and_smooth(y, window_length, polyorder):
    '''
    Extiendo datos para evitar artefacto del borde del suavizado
    '''
    factor = 8
    n = factor * (window_length - 1) // 2  # cantidad extendida (mitad de un wl)
    y_ext = np.concatenate([np.full(n, y[0]), y, np.full(n, y[-1])])
    y_smooth_ext = savgol_filter(y_ext, window_length=window_length, polyorder=polyorder)
    return y_smooth_ext[n:-n]

# Graficar dQ/dV calculado
plt.figure(figsize=(8,5))
colors = cm.viridis(np.linspace(0, 1, len(indices_ciclos)))

factor = 20
n = factor * (windowlength - 1) // 2  # cantidad extendida (mitad de un wl)

for i, color in zip(indices_ciclos, colors):
    df_ch = dict_ciclos_sep[i]['Ch']
    df_dis = dict_ciclos_sep[i]['Dis']

    Q_ch = df_ch['Q'].values
    V_ch = df_ch['CellV'].values
    Q_dis = df_dis['Q'].values
    V_dis = df_dis['CellV'].values

    # Extensión en Q: constante en los bordes
    #Q_ch_ext = np.concatenate([np.full(n, Q_ch[0]), Q_ch, np.full(n, Q_ch[-1])])

    # --- Extensión del eje V ---
    dV_mean = np.mean(np.diff(V_ch)) # Promedio del paso de voltaje
    V_start = V_ch[0] - dV_mean * np.arange(n, 0, -1)
    V_end = V_ch[-1] + dV_mean * np.arange(1, n + 1)
    V_ch_ext = np.concatenate([V_start, V_ch, V_end])

    # Ajuste lineal en los primeros k puntos (inicio)
    k=2
    coef_start = np.polyfit(V_ch[:k], Q_ch[:k], deg=1)  # coef_start[0] = pendiente
    slope_start = coef_start[0]
    intercept_start = coef_start[1]
    print(coef_start)

    # Ajuste lineal en los últimos k puntos (fin)
    k=100
    coef_end = np.polyfit(V_ch[-k:], Q_ch[-k:], deg=1)
    slope_end = coef_end[0]
    intercept_end = coef_end[1]
    print(coef_end)
    
    # --- Extensión del eje Q ---
    Q_start = slope_start * V_start + intercept_start
    Q_end = slope_end * V_end + intercept_end
    Q_ch_ext = np.concatenate([Q_start, Q_ch, Q_end])
    
    #plt.plot(V_ch[:2], Q_ch[:2], 'o', label='Datos inicio')
    #plt.plot(V_start, Q_start, '-', label='Extensión')
    #plt.legend()
    #plt.grid(True)
    #plt.title("Chequeo de extensión inicial")
    #plt.show()

    #print(n)

    #plt.plot(V_ch_ext,Q_ch_ext, marker='o', linestyle='-',color='red',markersize=0.1)
    #plt.plot(V_ch,Q_ch, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
    #print(Q_ch_ext.shape)
    #print(Q_ch.shape)

    # Aplica filtro Savitzky-Golay (smooth de la señal extendida)
    Q_ch_savgol = savgol_filter(Q_ch_ext, window_length=windowlength, polyorder=polyorder)
    V_ch_savgol = savgol_filter(V_ch_ext, window_length=windowlength, polyorder=polyorder)
    dqdv_ch_calc = np.gradient(Q_ch_savgol, V_ch_savgol)

    plt.plot(V_ch_ext,Q_ch_ext-5000, marker='o', linestyle='-',color='orange',markersize=0.1)
    plt.plot(V_ch,Q_ch-5000, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')

    plt.plot(V_ch_savgol, dqdv_ch_calc, marker='o', linestyle='-',color=color,markersize=0.1)#, label=f'Ciclo {i}')
    
    for idx in range(windowlength, len(V_ch_ext), windowlength):
        plt.axvline(x=V_ch_ext[idx], color='gray', linestyle='--', linewidth=0.8)

    # Aplica filtro Savitzky-Golay (smooth de la señal)
    #df_ch['Q_ch_savgol'] = savgol_filter(Q_ch, window_length=windowlength, polyorder=polyorder)
    #df_ch['V_ch_savgol'] = savgol_filter(V_ch, window_length=windowlength, polyorder=polyorder)
    #df_dis['Q_dis_savgol'] = savgol_filter(Q_dis, window_length=windowlength, polyorder=polyorder)
    #df_dis['V_dis_savgol'] = savgol_filter(V_dis, window_length=windowlength, polyorder=polyorder)
    
    #Q_ch_savgol = df_ch['Q_ch_savgol'].values
    #V_ch_savgol = df_ch['V_ch_savgol'].values
    #dqdv_ch_calc = np.gradient(Q_ch_savgol, V_ch_savgol)
    #dqdv_ch = dqdv_ch_calc
    #Q_dis_savgol = df_dis['Q_dis_savgol'].values
    #V_dis_savgol = df_dis['V_dis_savgol'].values
    #Q_dis_min = Q_dis_savgol.min()


    #plt.plot(V_dis_savgol,Q_dis_savgol-Q_dis_min, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
    
    #dqdv_dis_calc = np.gradient(Q_dis_savgol, V_dis_savgol)
    #dqdv_dis = dqdv_dis_calc

    #plt.plot(V_ch, dqdv_ch, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
    #plt.plot(V_dis, dqdv_dis, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
    
    # Asegurate de que sea impar
    #if window_length % 2 == 0:
    #    window_length += 1
    

# Crear colorbar asociada a los ciclos
#norm = mcolors.Normalize(vmin=min(ciclos), vmax=max(ciclos))
#sm = cm.ScalarMappable(cmap=cm.viridis, norm=norm)
#sm.set_array([])  # requerido
#cbar = plt.colorbar(sm, ax=plt.gca(), ticks=ciclos[::2])
#cbar.set_label('Cycle number')

plt.xlabel('Voltage (V)')
plt.ylabel('dQ/dV (mAh/V)')
plt.title(f'dQ/dV wl={windowlength}, po={polyorder}')
plt.grid(True)
plt.legend()
plt.show()



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