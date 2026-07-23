"""
Script para calcular dQ/dV de ciclos de carga/descarga de una bateria. Grafica QvsV, VvsQ y dQdV.

INPUT: archivo .txt exportado de BCycle.

Los ciclos que se graficarán son los presentes en el archivo de entrada. 
Qué ciclos son se elige en el BCycle.

"""
# %% ------- 1. Parámetros -----------------------------------------------------------------

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# Datos editables
input_folder = Path(r"C:\Users\Maria Jose\Documents\Datos NMC comercial\selecciones exportadas por mi\20grados cada 50 ciclos")
output_folder = Path(r"C:\Users\Maria Jose\Documents\procesado-arbin\procesado-IC-DV") / "output/NMC_comercial_20grados_50ciclos"
output_folder.mkdir(parents=True, exist_ok=True)  # Create output directory if it doesn't exist 
input_file = input_folder / "NMC-20C-cada50ciclos.txt"  # Input file path


# %% ------- 2. Carga de datos -----------------------------------------------------------------

df = pd.read_csv(input_file, sep='\t', engine='c')
df = df.drop(df.index[0]).reset_index(drop=True)

# Agrupar por ciclo, descartando columnas auxiliares
df['filename'] = df['Data'].ffill()
df['#Cycle'] = df['filename'].str.extract(r'Cycle (\d+)', expand=False).astype(int)

# Crear un diccionario con un DataFrame por ciclo 
# uso: ciclos[100] te da el DataFrame del grupo cuyo #Cycle == 100
ciclos = {ciclo: grupo.reset_index(drop=True) for ciclo, grupo in df.groupby('#Cycle')}

# Crear un diccionario anidado: {ciclo: {'Charging': df, 'Discharging': df}}
# uso: ciclos_sep[100]['Ch'] te da el DataFrame de carga del ciclo 100
#      ciclos_sep[100]['Dis'] te da el DataFrame de descarga del ciclo 100
ciclos_sep = {}
cols = ['Time', 'Current', 'CellV', 'dCapacity/dCellV']
for ciclo, grupo in df.groupby('#Cycle'):
    carga = grupo[grupo['filename'].str.contains('Charging')][cols].reset_index(drop=True)
    descarga = grupo[grupo['filename'].str.contains('Discharging')][cols].reset_index(drop=True)
    ciclos_sep[ciclo] = {'Ch': carga, 'Dis': descarga}

lista_ciclos = list(ciclos.keys())
print(f"Total de ciclos encontrados: {len(lista_ciclos)}")
print(f"Ciclos disponibles: {lista_ciclos}")

# %% Preparo para 1 solo ciclo
#-------------------------------------------------------------------------------------------------

i = 50  # Ciclo a procesar
ciclo_data = ciclos_sep[i]

# Extraer datos de carga y descarga
df_ch = ciclo_data['Ch']
df_dis = ciclo_data['Dis']

df_dis['Time'] = df_dis['Time'].str.replace(',', '.', regex=False).astype(float)
df_dis['Current'] = df_dis['Current'].str.replace(',', '.', regex=False).astype(float)
df_dis['CellV'] = df_dis['CellV'].str.replace(',', '.', regex=False).astype(float)
df_dis['dCapacity/dCellV'] = df_dis['dCapacity/dCellV'].str.replace(',', '.', regex=False).astype(float)
df_dis['Q'] = df_dis['Time'] * df_dis['Current'] / 3600  # Convertir a mAh

df_ch['Time'] = df_ch['Time'].str.replace(',', '.', regex=False).astype(float)
df_ch['Current'] = df_ch['Current'].str.replace(',', '.', regex=False).astype(float)
df_ch['CellV'] = df_ch['CellV'].str.replace(',', '.', regex=False).astype(float)
df_ch['dCapacity/dCellV'] = df_ch['dCapacity/dCellV'].str.replace(',', '.', regex=False).astype(float)
df_ch['Q'] = df_ch['Time'] * df_ch['Current'] / 3600  # Convertir a mAh
# %% Plot VOLTAJE VS TIEMPO
#-------------------------------------------------------------------------------------------------
# Vvst Charge
t_ch = df_ch['Time'].values
V_ch = df_ch['CellV'].values

fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(t_ch, V_ch, label='Charge', color='orange')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Voltage (V)')
ax.set_title(f'Voltage vs Time for Cycle {i} (Charge)')
plt.show(fig)
plt.close(fig)

# Vvst Discharge
t_dis = df_dis['Time'].values
V_dis = df_dis['CellV'].values

fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(t_dis, V_dis, label='Discharge', color='blue')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Voltage (V)')
ax.set_title(f'Voltage vs Time for Cycle {i} (Discharge)')
plt.show(fig)
plt.close(fig)

# Vvst Juntos
fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(t_ch, V_ch, label='Charge', color='orange')
ax.plot(t_dis, V_dis, label='Discharge', color='blue')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Voltage (V)')
ax.set_title(f'Voltage vs Time for Cycle {i}')


# %% Plot VOLTAJE VS CAPACIDAD
#-------------------------------------------------------------------------------------------------
# VvsQ Charge
Q_ch = df_ch['Q'].values
V_ch = df_ch['CellV'].values

fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(Q_ch, V_ch, label='Charge', color='orange')
ax.set_xlabel('Capacity (mAh)')
ax.set_ylabel('Voltage (V)')
ax.set_title(f'Voltage vs Capacity for Cycle {i} (Charge)')
plt.show(fig)
plt.close(fig)

# VvsQ Discharge
Q_dis = df_dis['Q'].values
V_dis = df_dis['CellV'].values

fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(Q_dis, V_dis, label='Discharge', color='blue')
ax.set_xlabel('Capacity (mAh)')
ax.set_ylabel('Voltage (V)')
ax.set_title(f'Voltage vs Capacity for Cycle {i} (Discharge)')
plt.show(fig)
plt.close(fig)

# VvsQ Juntos
fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(Q_ch, V_ch, label='Charge', color='orange')
ax.plot(Q_dis, V_dis, label='Discharge', color='blue')
ax.set_xlabel('Capacity (mAh)')
ax.set_ylabel('Voltage (V)')
ax.set_title(f'Voltage vs Capacity for Cycle {i}')


# %% Plot CAPACIDAD VS VOLTAJE
#-------------------------------------------------------------------------------------------------
# QvsV Charge
Q_ch = df_ch['Q'].values
V_ch = df_ch['CellV'].values

fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(V_ch, Q_ch, label='Charge', color='orange')
ax.set_ylabel('Capacity (mAh)')
ax.set_xlabel('Voltage (V)')
ax.set_title(f'Capacity vs Voltage for Cycle {i} (Charge)')
plt.show(fig)
plt.close(fig)

# VvsQ Discharge
Q_dis = df_dis['Q'].values
V_dis = df_dis['CellV'].values

fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(V_dis, Q_dis, label='Discharge', color='blue')
ax.set_ylabel('Capacity (mAh)')
ax.set_xlabel('Voltage (V)')
ax.set_title(f'Capacity vs Voltage for Cycle {i} (Discharge)')
plt.show(fig)
plt.close(fig)

# VvsQ Juntos
fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(V_ch, Q_ch, label='Charge', color='orange')
ax.plot(V_dis, Q_dis, label='Discharge', color='blue')
ax.set_ylabel('Capacity (mAh)')
ax.set_xlabel('Voltage (V)')
ax.set_title(f'Capacity vs Voltage for Cycle {i}')


# %% Plot dQdV VS VOLTAJE
# -------------------------------------------------------------------------------------------------
dqdv_ch = df_ch['dCapacity/dCellV'].values
dqdv_dis = df_dis['dCapacity/dCellV'].values

# Graficar dQ/dV
fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(V_ch, dqdv_ch, label='dQ/dV Charging', color='orange')
ax.plot(V_dis, dqdv_dis, label='dQ/dV Discharging', color='blue')
ax.set_xlabel('Voltage (V)')
ax.set_ylabel('dQ/dV (mAh/V)')

ax2 = ax.twinx()  # Crear un segundo eje y para la capacidad
ax2.set_ylabel('Capacity (mAh)')
ax2.set_xlabel('Voltage (V)')
ax2.plot(V_ch, Q_ch, label='VvsQ', color='orange', linestyle='--')
ax2.plot(V_dis, Q_dis, label='VvsQ', color='blue', linestyle='--')

ax.set_title(f'dQ/dV for Cycle {i}')
ax.legend(loc='upper left')
ax2.legend(loc='upper right')

file_out = output_folder / f'dQdV_Cycle_{i}.png'
fig.savefig(file_out)

plt.show(fig)
plt.close(fig)

# %% Plot dQdV VS VOLTAJE CALCULADO
#-------------------------------------------------------------------------------------------------

Q_ch = df_ch['Q'].values
V_ch = df_ch['CellV'].values
dqdv_ch_calc = np.gradient(Q_ch, V_ch)

Q_dis = df_dis['Q'].values
V_dis = df_dis['CellV'].values
dqdv_dis_calc = np.gradient(Q_dis, V_dis)

# Graficar dQ/dV calculado
fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(V_ch, dqdv_ch_calc, label='dQ/dV CALC Charging', color='orange')
ax.plot(V_dis, -dqdv_dis_calc, label='dQ/dV CALC Discharging', color='blue')
ax.set_xlabel('Voltage (V)')
ax.set_ylabel('dQ/dV (mAh/V)')

ax2 = ax.twinx()  # Crear un segundo eje y para la capacidad
ax2.set_ylabel('Capacity (mAh)')
ax2.set_xlabel('Voltage (V)')
ax2.plot(V_ch, Q_ch, label='VvsQ', color='orange', linestyle='--')
ax2.plot(V_dis, Q_dis, label='VvsQ', color='blue', linestyle='--')

ax.set_title(f'dQ/dV for Cycle {i}')
ax.legend(loc='upper left')
ax2.legend(loc='upper right')

file_out = output_folder / f'dQdV_CALC_Cycle_{i}.png'
fig.savefig(file_out)

plt.show(fig)
plt.close(fig)
# %% Plot dQdV VS VOLTAJE CALCULADO CON FILTRO
#-------------------------------------------------------------------------------------------------

# Aplicar filtro Savitzky-Golay
from scipy.signal import savgol_filter
windowlength = 51  # Longitud de la ventana del filtro
polyorder = 3  # Orden del polinomio del filtro

Q_ch = df_ch['Q'].values
V_ch = df_ch['CellV'].values
Q_ch_smooth = savgol_filter(Q_ch, window_length=windowlength, polyorder=polyorder)
V_ch_smooth = savgol_filter(V_ch, window_length=windowlength, polyorder=polyorder)
dqdv_ch_calc_smooth = np.gradient(Q_ch_smooth, V_ch_smooth)

Q_dis = df_dis['Q'].values
V_dis = df_dis['CellV'].values
Q_dis_smooth = savgol_filter(Q_dis, window_length=windowlength, polyorder=polyorder)
V_dis_smooth = savgol_filter(V_dis, window_length=windowlength, polyorder=polyorder)
dqdv_dis_calc_smooth = np.gradient(Q_dis_smooth, V_dis_smooth)

# Graficar dQ/dV calculado
fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(V_ch, dqdv_ch_calc_smooth, label='dQ/dV Charging', color='orange')
ax.plot(V_dis, -dqdv_dis_calc_smooth, label='dQ/dV Discharging', color='blue')
ax.set_xlabel('Voltage (V)')
ax.set_ylabel('dQ/dV (mAh/V)')

ax2 = ax.twinx()  # Crear un segundo eje y para la capacidad
ax2.set_ylabel('Capacity (mAh)')
ax2.set_xlabel('Voltage (V)')
ax2.plot(V_ch, Q_ch, label='VvsQ original', color='gray')
ax2.plot(V_dis, Q_dis, color='gray')
ax2.plot(V_ch_smooth, Q_ch_smooth, label='VvsQ', color='orange', linestyle='--')
ax2.plot(V_dis_smooth, Q_dis_smooth, label='VvsQ', color='blue', linestyle='--')

ax.set_title(f'dQ/dV CALC smooth for Cycle {i}')
ax.legend(loc='upper left')
ax2.legend(loc='upper right')

file_out = output_folder / f'dQdV_CALC_smooth_Cycle_{i}.png'
fig.savefig(file_out)

plt.show(fig)
plt.close(fig)

# %%
