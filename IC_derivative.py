"""
Script para graficar derivadas de ciclos de carga/descarga.

INPUT: archivo .json en data-proc exportado de BCycle.

"""
from pathlib import Path
import numpy as np
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import funciones_ic as f
from scipy.signal import savgol_filter

# %% ------- Cargar ciclos ------------------------------------------------------------
input_folder = Path('/home/mariajose/proc-icdv/data-proc')
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

# Elegir un ciclo de test
ciclo_test = 15

# Elegir varios ciclos
N_ciclos = 10  # Número de ciclos a tomar, si no se especifica, toma todos los del archivo

indices_ciclos_ = indices_ciclos[:-1] # Quito el último
indices_ciclos_array = np.array(indices_ciclos_)

ciclos_disponibles = sorted(dict_ciclos_sep.keys())
ciclos_seleccionados = indices_ciclos_array[np.linspace(0, len(indices_ciclos_array)-1, N_ciclos, dtype=int)]

print("Ciclos seleccionados:", ciclos_seleccionados)
print(f"son {len(ciclos_seleccionados)} ciclos")

#ciclos_reducidos = [3, 21, 78, 153, 228, 303, 378, 453, 528, 603, 678, 753, 828]

# %% ------- plot smooth -----------------------------------------------------------------------
'''
wl = 31  # Longitud de la ventana del filtro
po = 5  # Orden del polinomio del filtro
x = 'CellV'  # Eje x
y = 'Q'  # Eje y
nombre_grafico = f'{nombre_archivo}_savgol_smooth'
dict = dict_ciclos_sep
indices_ciclos = ciclos_seleccionados#[ciclo_test]

windowlength = wl  # Longitud de la ventana del filtro
polyorder = po  # Orden del polinomio del filtro

plt.figure(figsize=(8,5))
colors = cm.viridis(np.linspace(0, 1, len(indices_ciclos)))

for i, color in zip(indices_ciclos, colors):
    df_ch = dict[i]['Ch']   # Es una referencia al dict, no una copia. Al agregar valores se agrega al dict original
    df_dis = dict[i]['Dis']

    Q_ch = df_ch['Q'].values
    V_ch = df_ch['CellV'].values
    Q_dis = df_dis['Q'].values
    V_dis = df_dis['CellV'].values

    n_points = len(Q_dis)
    if n_points < windowlength:
        print('NO SE GRAFICA CICLO: ', i)
        continue
    
    # Aplica filtro Savitzky-Golay (smooth de la señal)
    df_ch['Q_ch_savgol'] = savgol_filter(Q_ch, window_length=windowlength, polyorder=polyorder)
    df_dis['Q_dis_savgol'] = savgol_filter(Q_dis, window_length=windowlength, polyorder=polyorder)        
    
    # Plot
    plt.plot(V_ch,df_ch['Q_ch_savgol'],  marker='o', linestyle='-', markersize=1, color=color)
    plt.plot(V_dis,df_dis['Q_dis_savgol'], marker='o', linestyle='-', markersize=1, color=color)

# Crear colorbar asociada a los ciclos
norm = mcolors.Normalize(vmin=min(indices_ciclos), vmax=max(indices_ciclos))
sm = cm.ScalarMappable(cmap=cm.viridis, norm=norm)
sm.set_array([])  # requerido
cbar = plt.colorbar(sm, ax=plt.gca(), ticks=indices_ciclos[::2])
cbar.set_label('Cycle number')

x_string = x.replace('dCapacity/dCellV', 'dQdV') if x == 'dCapacity/dCellV' else x
y_string = y.replace('dCapacity/dCellV', 'dQdV') if y == 'dCapacity/dCellV' else y

plt.xlabel(f'{x}')
plt.ylabel(f'{y}')
plt.title(f'{nombre_grafico} {y} vs {x}')
plt.grid(True)
#plt.legend()
plt.savefig(f'./output/{nombre_grafico}_{y_string}vs{x_string}.png', dpi=300)
'''
# ------------------ plot dqdv de Savitzky-Golay ------------------

i = ciclo_test
dict = dict_ciclos_sep
df_ch = dict[i]['Ch']   # Es una referencia al dict, no una copia. Al agregar valores se agrega al dict original
df_dis = dict[i]['Dis']

Q_ch = df_ch['Q'].values
V_ch = df_ch['CellV'].values
Q_dis = df_dis['Q'].values
V_dis = df_dis['CellV'].values

diffs = np.diff(V_ch)
#print(diffs)
#plt.plot(diffs, marker='o')
#plt.title("Diferencias entre valores consecutivos")
#plt.xlabel("Índice")
#plt.ylabel("Diferencia")
#plt.grid(True)
#plt.show()

plt.plot(df_ch['Q'].values[1:], diffs, marker='.')
plt.xlabel('Q')
plt.ylabel('Δ CellV')
plt.title('Espaciado según carga')
plt.grid(True)
plt.show()




    #df_ch['V_ch_savgol'] = savgol_filter(V_ch, window_length=windowlength, polyorder=polyorder)
    #dqdv_ch_calc_smooth = np.gradient(Q_ch_smooth, V_ch_smooth)
    #df_dis['V_dis_smooth'] = savgol_filter(V_dis, window_length=windowlength, polyorder=polyorder)
    #dqdv_dis_calc_smooth = np.gradient(Q_dis_smooth, V_dis_smooth)

    # x vs y Juntos
    #plt.plot(V_ch, df_ch['Q_ch_savgol'],  marker='o', linestyle='-', markersize=1, color=color)
    #plt.plot(V_dis, df_dis['Q_dis_savgol'], marker='o', linestyle='-', markersize=1, color=color)
    #xx = np.linspace(0, 1, len(df_ch['dqdv_ch_savgol']))
    #xxx = np.linspace(0, 1, len(df_dis['dqdv_dis_savgol']))
    #plt.plot(V_ch,df_ch['dqdv_ch_savgol'],  marker='o', linestyle='-', markersize=1, color=color)
    #plt.plot(V_dis,df_dis['dqdv_dis_savgol'], marker='o', linestyle='-', markersize=1, color=color)

    #plt.plot(Q_ch,df_ch['dvdq_ch_savgol'],  marker='o', linestyle='-', markersize=1, color=color)
    #plt.plot(Q_dis,df_dis['dvdq_dis_savgol'], marker='o', linestyle='-', markersize=1, color=color)



"""
df_ch['V_ch_savgol'] = savgol_filter(V_ch, window_length=windowlength, polyorder=polyorder)
df_dis['V_dis_savgol'] = savgol_filter(V_dis, window_length=windowlength, polyorder=polyorder)
df_ch['dqdv_ch_savgol'] = savgol_filter(df_ch['Q_ch_savgol'], window_length=windowlength, polyorder=polyorder, deriv=1)
df_dis['dqdv_dis_savgol'] = savgol_filter(df_dis['Q_dis_savgol'], window_length=windowlength, polyorder=polyorder, deriv=1) 
df_ch['dvdq_ch_savgol'] = savgol_filter(df_ch['V_ch_savgol'], window_length=windowlength, polyorder=polyorder, deriv=1)
df_dis['dvdq_dis_savgol'] = savgol_filter(df_dis['V_dis_savgol'], window_length=windowlength, polyorder=polyorder, deriv=1)




def plot_dqdv_savgol_n_cycles(indices_ciclos, dict, x, y, wl=51, po=3, nombre_grafico='plot'):

    windowlength = wl  # Longitud de la ventana del filtro
    polyorder = po  # Orden del polinomio del filtro

    plt.figure(figsize=(8,5))
    colors = cm.viridis(np.linspace(0, 1, len(indices_ciclos)))

    for i, color in zip(indices_ciclos, colors):
        df_ch = dict[i]['Ch']
        df_dis = dict[i]['Dis']

        Q_ch = df_ch['Q'].values
        V_ch = df_ch['CellV'].values
        Q_dis = df_dis['Q'].values
        V_dis = df_dis['CellV'].values

        n_points = len(Q_dis)
        if n_points < windowlength:
            print('NO SE GRAFICA CICLO: ', i)
            continue

        df_ch['Q_ch_savgol'] = savgol_filter(Q_ch, window_length=windowlength, polyorder=polyorder)
        df_ch['dqdv_ch_savgol'] = savgol_filter(Q_ch, window_length=windowlength, polyorder=polyorder, deriv=1)
        
        df_dis['Q_dis_savgol'] = savgol_filter(Q_dis, window_length=windowlength, polyorder=polyorder)        
        df_dis['dqdv_dis_savgol'] = savgol_filter(Q_dis, window_length=windowlength, polyorder=polyorder)
        
        #df_ch['V_ch_savgol'] = savgol_filter(V_ch, window_length=windowlength, polyorder=polyorder)
        #dqdv_ch_calc_smooth = np.gradient(Q_ch_smooth, V_ch_smooth)
        #df_dis['V_dis_smooth'] = savgol_filter(V_dis, window_length=windowlength, polyorder=polyorder)
        #dqdv_dis_calc_smooth = np.gradient(Q_dis_smooth, V_dis_smooth)

        # x vs y Juntos
        plt.plot(df_ch['Q_ch_savgol'], V_ch, marker='o', linestyle='-', markersize=1, color=color)
        plt.plot(df_dis['Q_dis_savgol'], V_dis, marker='o', linestyle='-', markersize=1, color=color)
    
    # Crear colorbar asociada a los ciclos
    norm = mcolors.Normalize(vmin=min(indices_ciclos), vmax=max(indices_ciclos))
    sm = cm.ScalarMappable(cmap=cm.viridis, norm=norm)
    sm.set_array([])  # requerido
    cbar = plt.colorbar(sm, ax=plt.gca(), ticks=indices_ciclos[::2])
    cbar.set_label('Cycle number')

    x_string = x.replace('dCapacity/dCellV', 'dQdV') if x == 'dCapacity/dCellV' else x
    y_string = y.replace('dCapacity/dCellV', 'dQdV') if y == 'dCapacity/dCellV' else y

    plt.xlabel(f'{x}')
    plt.ylabel(f'{y}')
    plt.title(f'{y} vs {x}')
    plt.grid(True)
    plt.legend()
    plt.savefig(f'./output/{nombre_grafico}_{y_string}vs{x_string}.png', dpi=300)
    #plt.show()
    return




# %% ------- 8. Plot dqdv derivado con filtro  -----------------------------------------------

ciclos = ciclos_reducidos

# Aplicar filtro Savitzky-Golay
from scipy.signal import savgol_filter
windowlength = 51  # Longitud de la ventana del filtro
polyorder = 3  # Orden del polinomio del filtro

plt.figure(figsize=(8,5))
colors = cm.viridis(np.linspace(0, 1, len(ciclos)))

for i, color in zip(ciclos, colors):
    df_ch = dict_ciclos_sep[i]['Ch']
    df_dis = dict_ciclos_sep[i]['Dis']

    Q_ch = df_ch['Q'].values
    V_ch = df_ch['CellV'].values
    Q_dis = df_dis['Q'].values
    V_dis = df_dis['CellV'].values

    n_points = len(Q_dis)
    if n_points < windowlength:
        print('NO SE GRAFICA CICLO: ', i)
        continue

    Q_ch_smooth = savgol_filter(Q_ch, window_length=windowlength, polyorder=polyorder)
    V_ch_smooth = savgol_filter(V_ch, window_length=windowlength, polyorder=polyorder)
    dqdv_ch_calc_smooth = np.gradient(Q_ch_smooth, V_ch_smooth)
    Q_dis_smooth = savgol_filter(Q_dis, window_length=windowlength, polyorder=polyorder)
    V_dis_smooth = savgol_filter(V_dis, window_length=windowlength, polyorder=polyorder)
    dqdv_dis_calc_smooth = np.gradient(Q_dis_smooth, V_dis_smooth)

    # Vvst Juntos
    plt.plot(V_ch, dqdv_ch_calc_smooth, marker='o', linestyle='-', markersize=0.5, color=color)
    plt.plot(V_dis, -dqdv_dis_calc_smooth, marker='o', linestyle='-', markersize=0.5, color=color)
    
# Crear colorbar asociada a los ciclos
norm = mcolors.Normalize(vmin=min(ciclos), vmax=max(ciclos))
sm = cm.ScalarMappable(cmap=cm.viridis, norm=norm)
sm.set_array([])  # requerido
cbar = plt.colorbar(sm, ax=plt.gca(), ticks=ciclos[::2])
cbar.set_label('Cycle number')

plt.xlabel('Voltage (V)')
plt.ylabel('dQ/dV (mAh/V)')
plt.title(f'dQ/dV derivado con filtro')
plt.grid(True)
plt.legend()
#plt.savefig(output_folder/f'dqdv_con_filtro')
#plt.savefig(f'datos/isoterma_J{J}.png', dpi=300)
plt.show()
"""