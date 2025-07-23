"""
Script para calcular dQ/dV de ciclos de carga/descarga de una bateria. Grafica QvsV, VvsQ y dQdV.

INPUT: archivo .txt exportado de BCycle.

Los ciclos que se graficarán son los presentes en el archivo de entrada. 
Qué ciclos son se elige en el BCycle.

"""
# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import IC_funciones as f

# %% ------- 1. Parámetros --------------------------------------------------------------------

# Datos editables
input_folder = Path('/home/mariajose/proc-icdv/data')
input_file = input_folder / "NMC_20C_cada3.txt"

output_folder = Path('./output')
output_folder.mkdir(parents=True, exist_ok=True)  # Create output directory if it doesn't exist

nombre_archivo = 'NMC-20'
N_ciclos = 10  # Número de ciclos a tomar, si no se especifica, toma todos los del archivo


# %% ------- 3. Cargado y procesado datos ----------------------------------------------------

dict_ciclos, dict_ciclos_sep, indices_ciclos = f.carga_y_procesa_datos(input_file)

#indices_ciclos = [2, 50, 100, 150, 200, 250, 300, 350,
#                   400, 450, 500, 550, 600, 650, 700, 750, 800, 850]#, 900]

#indices_ciclos = [2, 100, 150, 200, 300, 400, 500, 600,
#                   700, 800]#, 900

indices_ciclos_ = indices_ciclos[:-1] #quito el último
indices_ciclos_array = np.array(indices_ciclos_)

ciclos_disponibles = sorted(dict_ciclos_sep.keys())
ciclos_seleccionados = indices_ciclos_array[np.linspace(0, len(indices_ciclos_array)-1, N_ciclos, dtype=int)]

#N = 25  # tomá uno cada 25 múltiplos de 3
# Lista de múltiplos de 3
#mult_3 = [c for c in ciclos_disponibles if c % 3 == 0]

# Tomar cada N-ésimo múltiplo
#ciclos_reducidos = mult_3[::N]
#ciclos_reducidos = [c for c in ciclos_reducidos if c != 900] #quito el último

print("Ciclos seleccionados:", ciclos_seleccionados)
print(f"son {len(ciclos_seleccionados)} ciclos")

ciclos_reducidos = [3, 21, 78, 153, 228, 303, 378, 453, 528, 603, 678, 753, 828]

# %% ------- 5. Plot V vs t  -----------------------------------------------------------------

#ciclos = ciclos_reducidos
ciclos = ciclos_seleccionados

plt.figure(figsize=(8,5))
colors = cm.viridis(np.linspace(0, 1, len(ciclos)))

for i, color in zip(ciclos, colors):
    df_ch = dict_ciclos_sep[i]['Ch']
    df_dis = dict_ciclos_sep[i]['Dis']

    t_ch = df_ch['Time'].values
    V_ch = df_ch['CellV'].values
    t_dis = df_dis['Time'].values
    V_dis = df_dis['CellV'].values

    # Vvst Juntos
    plt.plot(t_ch, V_ch, marker='o', linestyle='-', markersize=1, color=color)
    plt.plot(t_dis, V_dis, marker='o', linestyle='-', markersize=1, color=color)

# Crear colorbar asociada a los ciclos
norm = mcolors.Normalize(vmin=min(ciclos), vmax=max(ciclos))
sm = cm.ScalarMappable(cmap=cm.viridis, norm=norm)
sm.set_array([])  # requerido
cbar = plt.colorbar(sm, ax=plt.gca())#, ticks=ciclos[::2])
cbar.set_label('Cycle number')

plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')
plt.title(f'Voltage vs Time')
plt.grid(True)
plt.legend()
#plt.savefig(output_folder/f'V_vs_C')
#plt.savefig(f'datos/isoterma_J{J}.png', dpi=300)
plt.show()

# %% ------- 6. Plot C vs V ------------------------------------------------------------------

ciclos = ciclos_reducidos

plt.figure(figsize=(8,5))
colors = cm.viridis(np.linspace(0, 1, len(ciclos)))


for i, color in zip(ciclos, colors):
    df_ch = dict_ciclos_sep[i]['Ch']
    df_dis = dict_ciclos_sep[i]['Dis']

    Q_ch = df_ch['Q'].values
    V_ch = df_ch['CellV'].values
    Q_dis = df_dis['Q'].values
    V_dis = df_dis['CellV'].values

    # Vvst Juntos
    plt.plot(V_ch, Q_ch, marker='o', linestyle='-', markersize=1, color=color)
    plt.plot(V_dis, Q_dis, marker='o', linestyle='-', markersize=1, color=color)

# Crear colorbar asociada a los ciclos
norm = mcolors.Normalize(vmin=min(ciclos), vmax=max(ciclos))
sm = cm.ScalarMappable(cmap=cm.viridis, norm=norm)
sm.set_array([])  # requerido
cbar = plt.colorbar(sm, ax=plt.gca(), ticks=ciclos[::2])
cbar.set_label('Cycle number')

plt.xlabel('Voltage (V)')
plt.ylabel('Capacity (mAh)')
plt.title(f'Capacity vs Voltage')
plt.grid(True)
plt.legend()
#plt.savefig(output_folder/f'C_vs_V')
#plt.savefig(f'datos/isoterma_J{J}.png', dpi=300)
plt.show()


# %% ------- 7. Plot dqdv --------------------------------------------------------------------

ciclos = ciclos_reducidos

plt.figure(figsize=(8,5))
colors = cm.viridis(np.linspace(0, 1, len(ciclos)))

for i, color in zip(ciclos, colors):
    df_ch = dict_ciclos_sep[i]['Ch']
    df_dis = dict_ciclos_sep[i]['Dis']

    dqdv_ch = df_ch['dCapacity/dCellV'].values
    V_ch = df_ch['CellV'].values
    dqdv_dis = df_dis['dCapacity/dCellV'].values
    V_dis = df_dis['CellV'].values

    # Vvst Juntos
    plt.plot(V_ch, dqdv_ch, marker='o', linestyle='-', markersize=0.5, color=color)
    plt.plot(V_dis, dqdv_dis, marker='o', linestyle='-', markersize=0.5, color=color)

# Crear colorbar asociada a los ciclos
norm = mcolors.Normalize(vmin=min(ciclos), vmax=max(ciclos))
sm = cm.ScalarMappable(cmap=cm.viridis, norm=norm)
sm.set_array([])  # requerido
cbar = plt.colorbar(sm, ax=plt.gca(), ticks=ciclos[::2])
cbar.set_label('Cycle number')

plt.xlabel('Voltage (V)')
plt.ylabel('dQ/dV (mAh/V)')
plt.title(f'dQ/dV')
plt.grid(True)
plt.legend()
#plt.savefig(output_folder/f'dqdv')
#plt.savefig(f'datos/isoterma_J{J}.png', dpi=300)
plt.show()


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


# %% ------- 9. Plot dqdv derivado con filtro + C vs V  --------------------------------------

ciclos = ciclos_reducidos

fig, ax = plt.subplots(figsize=(8,5))
ax2 = ax.twinx()  # Crear un segundo eje y para la capacidad
colors = cm.viridis(np.linspace(0, 1, len(indices_ciclos)))

for i, color in zip(indices_ciclos, colors):
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
    ax.plot(V_ch, dqdv_ch_calc_smooth, marker='o', linestyle='-', markersize=0.1, color=color)
    ax.plot(V_dis, -dqdv_dis_calc_smooth, marker='o', linestyle='-', markersize=0.1, color=color)
    ax2.plot(V_ch, Q_ch, color=color, marker='o', linestyle='None', markerfacecolor='none', markersize=0.5)
    ax2.plot(V_dis, Q_dis, color=color, marker='o', linestyle='None', markerfacecolor='none', markersize=0.5)
    #ax2.plot(V_ch_smooth, Q_ch_smooth, linestyle='--')
    #ax2.plot(V_dis_smooth, Q_dis_smooth, linestyle='--')


# Crear colorbar asociada a los ciclos
norm = mcolors.Normalize(vmin=min(indices_ciclos), vmax=max(indices_ciclos))
sm = cm.ScalarMappable(cmap=cm.viridis, norm=norm)
sm.set_array([])  # requerido
cbar = plt.colorbar(sm, ax=plt.gca(), ticks=indices_ciclos[::2])
cbar.set_label('Cycle number')

ax2.set_ylabel('Capacity (mAh)')
#ax2.set_xlabel('Voltage (V)')
ax.set_xlabel('Voltage (V)')
ax.set_ylabel('dQ/dV (mAh/V)')
ax.set_title(f'dQ/dV derivado con filtro y Q vs V')
ax.grid(True)
ax.legend()
#fig.savefig(f'datos/isoterma_J{J}.png', dpi=300)
plt.show()


# %% ------- 10. Plot SoH ---------------------------------------------------------------------

soh_data = []

# Encontrar la q_max_global
ciclos = indices_ciclos

for ciclo in ciclos:
    qmax = dict_ciclos_sep[ciclo]['Ch']['Q'].max()
    soh_data.append({'ciclo': ciclo, 'qmax': qmax})

# Encontrar qmax global y el ciclo correspondiente
qmax_global = max(d['qmax'] for d in soh_data)
ciclo_qmax_global = next(d['ciclo'] for d in soh_data if d['qmax'] == qmax_global)

print(f"La capacidad máxima es {qmax_global:.3f} mAh y se alcanza en el ciclo {ciclo_qmax_global}.")

# Calcular SoH para cada ciclo
soh_data = []

ciclos = ciclos_reducidos

for ciclo in ciclos:
    qmax = dict_ciclos_sep[ciclo]['Ch']['Q'].max()
    soh_data.append({'ciclo': ciclo, 'qmax': qmax})

for d in soh_data:
    d['soh'] = 100 * d['qmax'] / qmax_global

# Convertir lista de dicts a DataFrame
df_soh = pd.DataFrame(soh_data)

# Ordenar por ciclo, por si acaso
df_soh = df_soh.sort_values('ciclo')

# Graficar
plt.figure(figsize=(6, 4))
plt.plot(df_soh['ciclo'], df_soh['soh'], marker='o', linestyle='-', color='tab:red')
plt.xlabel('Cycle number')
plt.ylabel('State of Health (%)')
plt.title(f'SoH vs Cycle NMC 20°C (Q_max = {qmax_global:.3f})')
plt.grid(True)
plt.tight_layout()
#plt.savefig(output_folder/f'SoH_vs_cycle_todos')
plt.show()


# %% -- Plot SoH colorido 
# Crear colormap normalizado según el ciclo
norm = mcolors.Normalize(vmin=df_soh['ciclo'].min(), vmax=df_soh['ciclo'].max())
cmap = cm.viridis

# Graficar con colores variables
plt.figure(figsize=(6, 4))
sc = plt.scatter(df_soh['ciclo'], df_soh['soh'], c=df_soh['ciclo'], cmap=cmap, norm=norm, edgecolors='k')

# Añadir colorbar
cbar = plt.colorbar(sc, ticks=df_soh['ciclo'][::2])
cbar.set_label('Cycle number')

plt.xlabel('Cycle number')
plt.ylabel('State of Health (%)')
plt.title(f'SoH vs Cycle NMC 20°C (Q_max = {qmax_global:.3f})')
plt.grid(True)
plt.tight_layout()
#plt.savefig(output_folder/f'SoH_vs_cycle_reducido_colorido')
plt.show()

# %%
