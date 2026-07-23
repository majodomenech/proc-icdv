# proc-icdv

Acá listo algunas cosas para trabajar de forma más prolija.

## Estructura

```
proc-icdv/
├── README.md
├── setup/                 # se corre una vez al clonar el repo
│   ├── crear-venv.sh
│   └── requirements.txt
├── data/                  # datos originales
├── output/                # figuras, CSVs, resultados
├── notebooks/             # todos los Jupyter notebooks
│   ├── estudio1_plots.ipynb
│   └── ...
├── src/                   # código fuente modular
│   ├── __init__.py
│   ├── plotting.py        # funciones de graficado estándar.
│   ├── processing.py      # funciones de carga y procesamiento de datos.
│   ├── deriv.py           # funciones que suavizan y calculan derivadas
│   ├── fitting.py         # ajustes de picos, curvas, etc.
│   └── ic_main.py         # scripts principales de ejecución
├── tmp/                   # archivos temporales generados automáticamente
├── old/                   # código antiguo que quieras conservar
└── tests/                 # pruebas unitarias (opcional)
```


- La idea es hacer los experimentos/estudios de cada cosa que se nos ocurre en notebooks separados, para no mezclar. 
    - Formato: ```estudio[n]_[descripción].ipynb```

- Las funciones de uso general están en src para usarlas cuando haga falta. Se puede importar en cada notebook usando:
    -   ```python
        # Notebook
        import icdv as icdv
        ```

- Las funciones toman los datos y los guardan siempre de la misma manera.
    -  Luego de cargar los datos, siempre trabajo con **dicts**:
         ```
        dict_ciclos_sep = {ciclo: {'Ch': df_ciclo_ch, 'Dis': df_ciclo_dis}} 
        
        Uso: ciclos_sep[100]['Ch'] ---> te da el df de carga del ciclo 100
        ```
    - Si una función calcula una derivada, o devuelve datos suavizados, etc, agrega una clave más al dict con esa info. Claves actuales:
        ```
        Creadas inicialmente por carga_y_procesa_datos en processing.py
        'Time'
        'Current'
        'CellV'
        'dCapacity/dCellV'
        'dCellV/dCapacity'
        'Q'

        Creadas por plot_dqdv en deriv.py
        'Q_ch_savgol'
        'V_ch_savgol'
        'Q_dis_savgol'
        'V_dis_savgol'
        'dqdv_ch_calc'
        'dqdv_dis_calc'
        ```

- Los graficos toman los datos y devuelven siempre de la misma manera:
    - toman los datos así: ```plot_ejemplo(indices_ciclos, dict_ciclos_sep)```
    - en el caso que calcula derivada y plotea devuelve ```return dict_ciclos_sep``` para seguir usando el dict.

## Uso

### Importar y procesar datos de Arbin

```python
# 1) Convertir Excel a CSV (una sola vez)
#icdv.processing.arbin_excel_a_csv("../data/raw/jd_grcom_sw3_c_1_sinresorte_doslanavidrio.xls", "./tmp/ARBIN_jd_grcom_sw3_c_1_sinresorte_doslanavidrio")

# 2) Cargar todos los CSV (rápido)
df_all = icdv.processing.cargar_csv_arbin("/home/mariajose/proc-icdv/notebooks/tmp/ARBIN_jd_grcom_sw3_c_1_sinresorte_doslanavidrio")
df_all.head()

# 3) Procesar
dict_ciclos, dict_ciclos_sep, indices = icdv.processing.procesar_arbin(df_all)
dict_ciclos_sep[10]['Ch'].head()
```

### Plots iniciales (SoH, Vvst, VvsQ)

Así vemos lo que podemos graficar:
```python
print(len(indices))
print(indices[0:15])
print(indices[len(indices)-15:len(indices)])
print(dict_ciclos_sep[10]['Ch'].head())
```

- Primero ploteamos el SoH de todos los ciclos posibles para observar los datos.
    ```python
    icdv.plotting.plot_soh(indices[:], dict_ciclos_sep, nombre_grafico='grcom')
    ```
- Ploteamos el V vs t todo junto, el de solo carga y solo descarga para observar los datos.
    ```python
    icdv.plotting.plot_n_cycles_tvsV(indices[:], dict_ciclos_sep, nombre_grafico='plot', scatter=False)

    icdv.plotting.plot_n_cycles_tvsV(indices[:], dict_ciclos_sep, graficar='Ch', nombre_grafico='plot', scatter=False)
    
    icdv.plotting.plot_n_cycles_tvsV(indices[:], dict_ciclos_sep, graficar='Dis', nombre_grafico='plot', scatter=False)
    ```
- Luego evaluamos quitar los ciclos "anómalos" o rotos.
    ```python
    # Quitar ciclos anómalos
    indices = [i for i in indices if i not in [6,39,40,46,49]]
    ```
### Calcular dQdV



### Probar cosas nuevas

