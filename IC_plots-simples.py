"""
Script para graficar ciclos de carga/descarga.

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
print("Ciclos seleccionados:", ciclos_seleccionados)
print(f"son {len(ciclos_seleccionados)} ciclos")

# Elecciones rangos más pequeños
N1 = 115  # cantidad de ciclos hasta 99
N2 = 10  # cantidad de ciclos hasta 200
indices_hasta_99 = indices_ciclos_array[indices_ciclos_array <= 115]
#indices_hasta_200 = indices_ciclos_array[(indices_ciclos_array > 99) & (indices_ciclos_array <= 200)]
indices_hasta_200 = indices_ciclos_array[(indices_ciclos_array <= 200)]
#seleccion_99 = indices_hasta_99[np.linspace(0, len(indices_hasta_99)-1, N1, dtype=int)]
seleccion_99 = indices_hasta_99[np.linspace(2, len(indices_hasta_99)-1, dtype=int)]
seleccion_200 = indices_hasta_200[np.linspace(2, len(indices_hasta_200)-1, N2, dtype=int)]
print("Ciclos hasta 99:", seleccion_99)
print("Ciclos hasta 200:", seleccion_200)

#ciclos_seleccionados = indices_ciclos_array

# Elecciones manuales 
#ciclos_reducidos = [3, 21, 78, 153, 228, 303, 378, 453, 528, 603, 678, 753, 828]
#ciclos_seleccionados = [2, 99, 192, 300, 414, 504, 600, 702, 801, 897]
ciclos_seleccionados = [2, 21, 99, 198, 297, 396, 498, 597, 696, 795, 897]
ciclos_seleccionados = [2,21, 99, 198, 297, 396, 498, 597, 696, 795, 897]

# %% ------- Plots -----------------------------------------------------------------------

print(dict_ciclos_sep[ciclos_seleccionados[0]]['Ch'].columns)

df_ch = dict_ciclos_sep[ciclos_seleccionados[0]]['Ch']
df_dis = dict_ciclos_sep[ciclos_seleccionados[0]]['Dis']

print(df_ch.head())
#f.plot_n_cycles(ciclos_seleccionados, dict_ciclos_sep, 'Time', 'CellV', nombre_grafico=nombre_archivo)#+'scatter')

#f.plot_n_cycles_withCurrent(ciclos_seleccionados, dict_ciclos_sep, 'Time', 'CellV', nombre_grafico=nombre_archivo)#+'scatter')


f.plot_n_cycles(ciclos_seleccionados, dict_ciclos_sep, 'Q', 'CellV', nombre_grafico=nombre_archivo)#+'scatter')

#f.plot_n_cycles(ciclos_seleccionados, dict_ciclos_sep, 'CellV', 'Time', nombre_grafico=nombre_archivo)#+'scatter')

#f.plot_n_cycles(ciclos_seleccionados, dict_ciclos_sep, 'CellV', 'Q', nombre_grafico=nombre_archivo)#+'scatter')

#f.plot_n_cycles(ciclos_seleccionados, dict_ciclos_sep, 'CellV', 'dCapacity/dCellV', nombre_grafico=nombre_archivo)#+'scatter')

#f.plot_n_cycles(ciclos_seleccionados, dict_ciclos_sep, 'Q', 'dCellV/dCapacity', nombre_grafico=nombre_archivo)#+'scatter')

# %% ------- 10. Plot SoH ---------------------------------------------------------------------

'''
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

ciclos = ciclos_seleccionados

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
plt.title(f'SoH vs Cycle {nombre_archivo} (Q_max = {qmax_global:.3f})')
plt.grid(True)
plt.tight_layout()
plt.savefig(output_folder/f'{nombre_archivo}_SoH_vs_cycle.png', dpi=300)
#plt.show()


# %% -- Plot SoH colorido 
# Crear colormap normalizado según el ciclo
norm = mcolors.Normalize(vmin=df_soh['ciclo'].min(), vmax=df_soh['ciclo'].max())
cmap = cm.viridis

# Graficar con colores variables
plt.figure(figsize=(7, 5))
plt.plot(df_soh['ciclo'], df_soh['soh'], linestyle='-', color='gray', label='SoH', zorder=1)
plt.scatter(df_soh['ciclo'], df_soh['soh'], c=df_soh['ciclo'], cmap=cmap, norm=norm, s=10, zorder=2)

#sc = plt.scatter(df_soh['ciclo'], df_soh['soh'], c=df_soh['ciclo'], cmap=cmap, norm=norm, edgecolors='k', s=60)

# Añadir colorbar
#cbar = plt.colorbar(sc, ticks=df_soh['ciclo'][::2])
#cbar.set_label('Cycle number')

# Añadir etiquetas con el número de ciclo
#for i, row in df_soh.iterrows():
#    plt.text(row['ciclo'], row['soh'] + 0.5, str(int(row['ciclo'])), ha='center', va='bottom', fontsize=7)

#xticks_filtrados = [x for x in df_soh['ciclo'] if x != 21]
#plt.xticks(xticks_filtrados)  # Fuerza los ticks a coincidir con los ciclos
#plt.xticks(df_soh['ciclo'])
plt.xlabel('Cycle number')
plt.ylabel('State of Health (%)')
plt.title(f'SoH vs Cycle {nombre_archivo} (Q_max = {qmax_global:.3f}, para ciclo {ciclo_qmax_global})')
plt.grid(True)
plt.tight_layout()
plt.savefig(output_folder/f'{nombre_archivo}_SoH_vs_cycle_colorido.png', dpi=300)
plt.show()
'''