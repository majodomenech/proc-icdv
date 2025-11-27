import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import os
from scipy.signal import savgol_filter
import matplotlib.gridspec as gridspec
import json

'''
Funciones para cargar y procesar datos de ciclos de carga/descarga de baterías.

'''

# -------  Procesamiento de datos --------------------------------------------------------------------

def cargar_json(path_json):
    """
    Carga un archivo JSON y devuelve un diccionario estructurado por ciclos y etapas.
    Cada valor es un DataFrame con los datos de esa etapa.
    Ejemplo:
        dict_ciclos_sep[100]['Ch'] -> DataFrame del ciclo 100 en carga.
    """
    path_json = Path(path_json)
    with open(path_json, "r") as f:
        raw_dict = json.load(f)

    dict_ciclos_sep = {
        int(ciclo): {
            etapa: pd.DataFrame(data) for etapa, data in etapas.items()
        }
        for ciclo, etapas in raw_dict.items()
    }

    print('Estructura: dict_ciclos_sep = {ciclo: {"Ch": df_ciclo_ch, "Dis": df_ciclo_dis}}')
    print(f"Total de ciclos en el JSON: {len(dict_ciclos_sep)}")

    return dict_ciclos_sep


def crear_json(dict_ciclos_sep, output_path):
    """
    Crea un archivo JSON a partir de un diccionario dict_ciclos_sep.
    Convierte las claves de ciclo a strings y los DataFrames a diccionarios serializables.
    """
    serializable_dict = {
        str(ciclo): {
            etapa: df.to_dict(orient='list') for etapa, df in etapas.items()
        }
        for ciclo, etapas in dict_ciclos_sep.items()
    }

    with open(output_path, 'w') as f_json:
        json.dump(serializable_dict, f_json)

    print(f"Archivo JSON creado en: {output_path}")


def seleccionar_ciclos(
    dict_ciclos_sep,
    n_ciclos=None,
    rango=None,
    excluir=None,
    manual=None,
    verbose=True
):
    """
    Selecciona los ciclos a analizar de un diccionario dict_ciclos_sep.

    Parámetros
    ----------
    dict_ciclos_sep : dict
        Diccionario con los ciclos (claves enteras).
    n_ciclos : int, opcional
        Número de ciclos equiespaciados a tomar (por defecto toma todos).
    rango : tuple[int, int], opcional
        Rango de ciclos (min, max) a considerar.
    excluir : list[int] | set[int], opcional
        Ciclos a excluir.
    manual : list[int], opcional
        Si se pasa, usa directamente estos ciclos.
    verbose : bool, opcional
        Si es True, imprime un resumen.

    Retorna
    -------
    list[int]
        Lista ordenada de ciclos seleccionados.
    """
    ciclos = sorted(dict_ciclos_sep.keys())
    ciclos = sorted(dict_ciclos_sep.keys())[:-1]  # excluye último

    # Filtrar rango
    if rango:
        ciclos = [c for c in ciclos if rango[0] <= c <= rango[1]]

    # Excluir
    if excluir:
        excluir = set(excluir)
        ciclos = [c for c in ciclos if c not in excluir]

    # Selección manual
    if manual:
        seleccionados = [c for c in manual if c in ciclos]
    else:
        if n_ciclos is None or n_ciclos >= len(ciclos):
            seleccionados = ciclos
        else:
            seleccionados = np.array(ciclos)[
                np.linspace(0, len(ciclos) - 1, n_ciclos, dtype=int)
            ].tolist()

    if verbose:
        print(f"✅ {len(seleccionados)} ciclos seleccionados")
        #print(f"   → {seleccionados[:10]}{'...' if len(seleccionados) > 10 else ''}")
        print(f"   → {seleccionados[:]}")

    return seleccionados


def carga_y_procesa_datos(input_file):
    '''
    Carga datos de archivo csv del BCycle, separa por ciclos, separa en carga/descarga,
    y convierte los datos numéricos a float, agregando la columna Q en mAh.
    Se usa una sola vez sobre las mediciones para crear el json que queda en /tmp.

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

    # Impresión más legible y segura
    print('\n' + '='*60)
    print('📦 Resultados de carga y procesamiento')
    print('-'*60)
    print(f'Total de ciclos encontrados: {len(indices_ciclos)}')
    if len(indices_ciclos) == 0:
        print('No se encontraron ciclos en el archivo.')
    else:
        if len(indices_ciclos) > 10:
            print(f'Ciclos disponibles (muestra 10 primeros): {indices_ciclos[:10]} ... (total {len(indices_ciclos)})')
        else:
            print(f'Ciclos disponibles: {indices_ciclos}')

        # Seleccionar un ciclo de ejemplo de forma segura
        example_idx = 15 if len(indices_ciclos) > 15 else (len(indices_ciclos) - 1)
        example_cycle = indices_ciclos[example_idx]
        df_ch = dict_ciclos_sep[example_cycle]['Ch']
        df_dis = dict_ciclos_sep[example_cycle]['Dis']

        print('\nEjemplo de ciclo para inspección rápida:')
        print(f'  → Ciclo seleccionado: {example_cycle} (índice {example_idx})')
        print(f'  · Carga (Ch): shape = {df_ch.shape}')
        if not df_ch.empty:
            print('    Primeras 3 filas de carga:')
            print(df_ch.head(3).to_string(index=False))
        else:
            print('    DataFrame de carga vacío.')

        print(f'  · Descarga (Dis): shape = {df_dis.shape}')
        if not df_dis.empty:
            print('    Primeras 3 filas de descarga:')
            print(df_dis.head(3).to_string(index=False))
        else:
            print('    DataFrame de descarga vacío.')

    print('\n✅ LISTO: dict_ciclos_sep = {ciclo: {"Ch": df_ciclo_ch, "Dis": df_ciclo_dis}}')
    print('   Uso: dict_ciclos_sep[100]["Ch"] devuelve el DataFrame de carga del ciclo 100, si existe')
    print('='*60 + '\n')

    return dict_ciclos, dict_ciclos_sep, indices_ciclos

