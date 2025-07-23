"""
Script para guardar json de ciclos de carga/descarga.

INPUT: archivo .txt exportado de BCycle.

"""
# %%
from pathlib import Path
import json
import IC_funciones as f

# %% ------- 1. Parámetros --------------------------------------------------------------------

# Datos editables
input_folder = Path('/home/mariajose/proc-icdv/data')
input_file = input_folder / "NMC_20C_cada3.txt"
output_folder = Path('/home/mariajose/proc-icdv/data-proc')
nombre_archivo = 'NMC-20'

# %% ------- 2. Cargado y procesado datos  ----------------------------------------------------

dict_ciclos, dict_ciclos_sep, indices_ciclos = f.carga_y_procesa_datos(input_file)

"""
dict_ciclos_sep = {ciclo: Ch': df_ciclo_ch, 'Dis': df_ciclo_dis}} 

Uso: ciclos_sep[100]['Ch'] te da el df de carga del ciclo 100

Convierto clave ciclo a string y los DataFrames a dicts para poder serializarlo a JSON
"""

serializable_dict = {
    str(ciclo): {
        etapa: df.to_dict(orient='list') for etapa, df in etapas.items()
    }
    for ciclo, etapas in dict_ciclos_sep.items()
}

with open(output_folder / f'{nombre_archivo}.json', 'w') as f_json:
    json.dump(serializable_dict, f_json)

"""
luego para cargarlo:

with open(output_folder / f'{nombre_archivo}_procesado.json') as f_json:
    raw_dict = json.load(f_json)

dict_ciclos_sep = {
    int(ciclo): {
        etapa: pd.DataFrame(data) for etapa, data in etapas.items()
    }
    for ciclo, etapas in raw_dict.items()
}
"""

