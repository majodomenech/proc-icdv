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

### Uso

- La idea es hacer los experimentos/estudios de cada cosa que se nos ocurre en notebooks separados, para no mezclar. 
    - Formato: ```estudio[n]_[descripción].ipynb```

- Las funciones de uso general están en src para usarlas cuando haga falta. Se puede importar en cada notebook usando:
    -   ```python
        # Notebook
        from src import dataproc, deriv, plots, fitting
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