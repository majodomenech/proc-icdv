import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import os
from scipy.signal import savgol_filter
import matplotlib.gridspec as gridspec


'''
Funciones para cargar y procesar datos de ciclos de carga/descarga de baterías.
Se usa una sola vez sobre las mediciones para crear el json que queda en /tmp.
'''

# %% -------  Procesamiento de datos --------------------------------------------------------------------

def carga_y_procesa_datos(input_file):
    '''
    Carga datos de archivo csv del BCycle, separa por ciclos, separa en carga/descarga,
    y convierte los datos numéricos a float, agregando la columna Q en mAh.

    Outputs:
    - dict_ciclos = {ciclo: df_ciclo}. 
        Uso: dict_ciclo[50] da el df del ciclo 50
    - dict_ciclos_sep = {ciclo: {'Ch': df_ciclo_ch, 'Dis': df_ciclo_dis}}. 
        Uso: ciclos_sep[100]['Ch'] te da el df de carga del ciclo 100
    - indices_ciclos = lista de ciclos encontrados
    '''
    df = pd.read_csv(input_file, sep='\t', engine='c')
    df = df.drop(df.index[0]).reset_index(drop=True)
    df['filename'] = df['Data'].ffill()
    df['#Cycle'] = df['filename'].str.extract(r'Cycle (\d+)', expand=False).astype(int)

    dict_ciclos = {ciclo: grupo.reset_index(drop=True) for ciclo, grupo in df.groupby('#Cycle')}
    dict_ciclos_sep = {}
    cols = ['Time', 'Current', 'CellV', 'dCapacity/dCellV', 'dCellV/dCapacity']
    
    for ciclo, grupo in df.groupby('#Cycle'):
        df_ch = grupo[grupo['filename'].str.contains('Charging')][cols].reset_index(drop=True)
        df_dis = grupo[grupo['filename'].str.contains('Discharging')][cols].reset_index(drop=True)
        
        for df_temp in [df_ch, df_dis]:
            df_temp['Time'] = df_temp['Time'].str.replace(',', '.', regex=False).astype(float) # hour
            df_temp['Current'] = df_temp['Current'].str.replace(',', '.', regex=False).astype(float) # mA
            df_temp['CellV'] = df_temp['CellV'].str.replace(',', '.', regex=False).astype(float) # V
            df_temp['dCapacity/dCellV'] = df_temp['dCapacity/dCellV'].str.replace(',', '.', regex=False).astype(float) # mAh/V
            df_temp['dCellV/dCapacity'] = df_temp['dCellV/dCapacity'].str.replace(',', '.', regex=False).astype(float) # V/mAh
            df_temp['Q'] = df_temp['Time'] * (abs(df_temp['Current'])) # mAh #/ 3600
          
        dict_ciclos_sep[ciclo] = {'Ch': df_ch, 'Dis': df_dis}

    indices_ciclos = list(dict_ciclos.keys())
    print(f"Total de ciclos encontrados: {len(indices_ciclos)}")
    print(f"Ciclos disponibles: {indices_ciclos}")
    
    # Imprimir ejemplos de los DataFrames de carga y descarga
    df_ch = dict_ciclos_sep[indices_ciclos[15]]['Ch']
    df_dis = dict_ciclos_sep[indices_ciclos[15]]['Dis']
    print('df_ch:')
    print(df_ch.shape)
    print(df_ch.head())
    print(df_ch.iloc[500:505])
    print(df_ch.tail())
    print('df_dis:')
    print(df_dis.shape)
    print(df_dis.head())
    print(df_dis.iloc[500:505])
    print(df_dis.tail())

    return dict_ciclos, dict_ciclos_sep, indices_ciclos

# no está en uso
def guardar_ciclos_en_dat(dict_ciclos_sep, carpeta_salida='ciclos_dat'):
    '''
    Guarda los DataFrames de carga y descarga por ciclo en archivos .dat individuales.

    Para cada ciclo en `dict_ciclos_sep`, se generan dos archivos:
    - cicloXXX_Ch.dat  → datos de carga
    - cicloXXX_Dis.dat → datos de descarga

    Formato de salida:
    - La primera línea contiene los nombres de las columnas precedidos por "#"
    - Los datos están separados por tabulaciones
    - Los valores numéricos se escriben con 6 decimales
    - No se incluye el índice del DataFrame

    '''
    os.makedirs(carpeta_salida, exist_ok=True)

    for ciclo, datos in dict_ciclos_sep.items():
        for tipo, df in datos.items():  # 'Ch' o 'Dis'
            nombre_archivo = f'ciclo{ciclo}_{tipo}.dat'
            ruta = os.path.join(carpeta_salida, nombre_archivo)

            with open(ruta, 'w') as f:
                # Escribir encabezado con #
                columnas = ' '.join(df.columns)
                f.write(f'# {columnas}\n')
                # Escribir datos (sin índice, tabulado, formato flotante)
                df.to_csv(f, sep='\t', index=False, header=False, float_format='%.6f')