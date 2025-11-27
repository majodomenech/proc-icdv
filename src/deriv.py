from pathlib import Path
import numpy as np
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from scipy.signal import savgol_filter



'''
Funciones para trabajar con las derivadas IC, DV.

'''
# ----------- tools -------------

def truncar_señal(indices_ciclos, dict_ciclos_sep, n_dis=10, n_ch=30):
    '''
    Trunca la señal eliminando extremos. Devuelve dict listo para usar con las otras funciones graficadoras.
    Parámetros
    ----------
    indices_ciclos : list[int]
        Ciclos a procesar.
    dict_ciclos_sep : dict
        Diccionario con DataFrames de ciclos separados en 'Ch' y 'Dis'.
    n_dis : int, opcional
        Número de puntos a truncar al FINAL de la descarga. Por defecto 10.
    n_ch : int, opcional
        Número de puntos a truncar al INICIO de la carga. Por defecto 3 * n_dis.

    Retorna
    -------
    dict
        Diccionario con DataFrames truncados por ciclo.
    '''
    dict_truncado = {}

    for i in indices_ciclos:
        df_ch = dict_ciclos_sep[i]['Ch']
        df_dis = dict_ciclos_sep[i]['Dis']

        Q_ch = df_ch['Q'].values
        V_ch = df_ch['CellV'].values
        Q_dis = df_dis['Q'].values
        V_dis = df_dis['CellV'].values

        # Truncar el eje Q y V
        Q_ch_trunc = Q_ch[n_ch:]
        V_ch_trunc = V_ch[n_ch:]
        Q_dis_trunc = Q_dis[n_dis:]  # El array de descarga tiene los voltajes ordenados de mayor a menor.
        V_dis_trunc = V_dis[n_dis:]

        # Crear nuevos DataFrames
        df_ch_trunc = pd.DataFrame({'Q': Q_ch_trunc, 'CellV': V_ch_trunc})
        df_dis_trunc = pd.DataFrame({'Q': Q_dis_trunc, 'CellV': V_dis_trunc})

        dict_truncado[i] = {
            'Ch': df_ch_trunc,
            'Dis': df_dis_trunc
        }

    return dict_truncado


def extender_señal(indices_ciclos, dict_ciclos_sep):
    '''
    Extiende señal conservando la pendiente. Devuelve dict listo para usar con las otras funciones graficadoras.
    
    nota: por ahora solo extiende los ciclos charge.
    '''

    dict_extendido = {}

    windowlength = 153
    factor = 20
    n = factor * (windowlength - 1) // 2  # cantidad extendida (mitad de un wl)

    colors = cm.viridis(np.linspace(0, 1, len(indices_ciclos)))

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

        # Crear nuevos DataFrames
        df_ch_ext = pd.DataFrame({'Q': Q_ch_ext, 'CellV': V_ch_ext})
        df_dis_ext = pd.DataFrame({'Q': Q_dis, 'CellV': V_dis})  # sin extensión

        dict_extendido[i] = {
            'Ch': df_ch_ext,
            'Dis': df_dis_ext
        }

    return dict_extendido


# ----------- ESTUDIO DERIVADA VARIANDO PARAMETROS FILTRO -------------
def plot_dqdv_muchos_wl(indices_ciclos,dict, wl_values=None, truncar_values=None):
    '''
    Función para plotear dQ/dV variando los parámetros del filtro Savitzky-Golay. También permite truncar.
    Parámetros
    indices_ciclos: lista de índices de ciclos a graficar
    dict: diccionario con los datos de los ciclos
    wl_values: lista de valores de window length a probar (para descarga). La carga será 3 veces este valor.
    truncar_values: lista de valores para truncar los datos (para descarga). La carga será 3 veces este valor.
    '''

    if wl_values is None:
        windowlengths_dis = np.array([51,53,57,59,61,63])
    else:
        windowlengths_dis = np.array(wl_values)
    windowlengths_ch = windowlengths_dis * 3
    polyorder = 3

    if truncar_values is not None:
        n_dis, n_ch = truncar_values
        dict = truncar_señal(indices_ciclos, dict, n_dis=n_dis, n_ch=n_ch)

    ncols = 3
    nrows = int(np.ceil(len(windowlengths_dis) / ncols))

    fig, axs = plt.subplots(nrows, ncols, figsize=(12, 3 * nrows), sharex=True, sharey=True)
    axs = axs.flatten()
    colors = cm.viridis(np.linspace(0, 1, len(indices_ciclos)))

    count = 0
    for ax, wl_dis in zip(axs, windowlengths_dis):
        wl_ch = windowlengths_ch[count]
        count+=1
        for i, color in zip(indices_ciclos, colors):
            df_ch = dict[i]['Ch']
            df_dis = dict[i]['Dis']

            Q_ch = df_ch['Q'].values
            V_ch = df_ch['CellV'].values
            Q_dis = df_dis['Q'].values
            V_dis = df_dis['CellV'].values

            # Verifica que wl sea menor que el tamaño de Q_dis y sea impar
            if wl_dis >= len(Q_dis) or wl_ch >= len(Q_ch):
                continue
            if wl_dis % 2 == 0 or wl_ch % 2 == 0:
                wl += 1

            Q_ch_savgol = savgol_filter(Q_ch, window_length=wl_ch, polyorder=polyorder)
            V_ch_savgol = savgol_filter(V_ch, window_length=wl_ch, polyorder=polyorder)
            dqdv_ch = np.gradient(Q_ch_savgol, V_ch_savgol)    
            Q_dis_savgol = savgol_filter(Q_dis, window_length=wl_dis, polyorder=polyorder)
            V_dis_savgol = savgol_filter(V_dis, window_length=wl_dis, polyorder=polyorder)
            dqdv_dis = np.gradient(Q_dis_savgol, V_dis_savgol)

            # Plotear modo curva
            ax.plot(V_ch, dqdv_ch, color=color, markersize=0.1)
            ax.plot(V_dis, dqdv_dis, color=color, markersize=0.1)
            
            # Plotear modo scatter
            #ax.scatter(V_ch,Q_ch, marker='o', linestyle='-',color=color, label=f'Ciclo {i}',s=1)
            #ax.scatter(V_ch, dqdv_ch, color=color, s=1) 
            #ax.scatter(V_dis,Q_dis-np.min(Q_dis), marker='o', linestyle='-',color=color)#, label=f'Ciclo {i}',s=1)
            #ax.scatter(V_dis, dqdv_dis, color=color, s=1)
            
            #for idx in range(wl, len(V_ch), wl):
            #    ax.axvline(x=V_ch[idx], color=color, linestyle='--', linewidth=0.8)

        ax.set_title(f'wl_ch={wl_ch}, wl_dis={wl_dis}')
        ax.set_xlabel('Voltage (V)')
        #ax.set_ylim(-6000,1000)
        #ax.set_ylim(-1000,11000)
        ax.set_ylabel('dQ/dV')
        ax.grid(True)

        
    # Eliminar subplots vacíos si hay
    for ax in axs[len(windowlengths_dis):]:
        fig.delaxes(ax)

    
    plt.tight_layout()
    plt.show()


def extender_señal_y_plot(indices_ciclos, dict_ciclos_sep):
    '''
    Extiende señal conservando la pendiente. Devuelve dict listo para usar con las otras funciones graficadoras.
    
    nota: por ahora solo extiende los ciclos charge.
    '''

    dict_extendido = {}

    # Plot derivada con filtro
    windowlength = 153  # Longitud de la ventana del filtro
    polyorder = 3 # Orden del polinomio del filtro

    factor = 20 #20
    n = factor * (windowlength - 1) // 2  # cantidad extendida (mitad de un wl)

    plt.figure(figsize=(8,5))
    colors = cm.viridis(np.linspace(0, 1, len(indices_ciclos)))

    count=0

    for i, color in zip(indices_ciclos, colors):

        count+=1

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

        # Crear nuevos DataFrames
        df_ch_ext = pd.DataFrame({'Q': Q_ch_ext, 'CellV': V_ch_ext})
        df_dis_ext = pd.DataFrame({'Q': Q_dis, 'CellV': V_dis})  # sin extensión

        dict_extendido[i] = {
            'Ch': df_ch_ext,
            'Dis': df_dis_ext
        }

        # Aplica filtro Savitzky-Golay (smooth de la señal extendida)
        Q_ch_savgol = savgol_filter(Q_ch_ext, window_length=windowlength, polyorder=polyorder)
        V_ch_savgol = savgol_filter(V_ch_ext, window_length=windowlength, polyorder=polyorder)
        dqdv_ch_calc = np.gradient(Q_ch_savgol, V_ch_savgol)

        #plt.plot(V_ch_ext,Q_ch_ext-5000, marker='o', linestyle='-',color='orange',markersize=0.1)
        #plt.plot(V_ch,Q_ch-5000, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')

        #plt.plot(V_ch_savgol, dqdv_ch_calc, marker='o', linestyle='-',color=color,markersize=0.1)#, label=f'Ciclo {i}')
        
        plt.scatter(V_ch_ext,Q_ch_ext-5000 - count*200, marker='o', linestyle='-',color='orange',s=1)
        plt.scatter(V_ch,Q_ch-5000 - count*200, marker='o', linestyle='-',color=color, label=f'Ciclo {i}',s=1)

        plt.scatter(V_ch_savgol, dqdv_ch_calc - count*200, marker='o', linestyle='-',color=color,s=1)#, label=f'Ciclo {i}')
        
        #for idx in range(windowlength, len(V_ch_ext), windowlength):
        #    plt.axvline(x=V_ch_ext[idx], color='red', linestyle='--', linewidth=0.8)

    plt.ylim(-7900,8200)
    plt.xlim(3.2,3.75)

    plt.xlabel('Voltage (V)')
    plt.ylabel('dQ/dV (mAh/V)')
    plt.title(f'dQ/dV wl={windowlength}, po={polyorder}')
    plt.grid(True)
    plt.legend()
    plt.show()

    return dict_extendido


def truncar_señal_y_plot(indices_ciclos, dict_ciclos_sep):
    '''
    Trunca la señal eliminando extremos. Devuelve dict listo para usar con las otras funciones graficadoras.
    
    Nota: por ahora solo trunca los ciclos charge.
    '''
    dict_truncado = {}

    # Parámetros del filtro
    windowlength_dis = 51  # Longitud de la ventana del filtro
    windowlength_ch = 3 * windowlength_dis  
    polyorder = 3 # Orden del polinomio del filtro

    factor = 1/4
    #n = int(factor * (windowlength - 1)) // 2  # cantidad que se recorta de cada extremo
    n_dis = 10
    n_ch = n_dis * 3

    plt.figure(figsize=(9,5.6))
    colors = cm.viridis(np.linspace(0, 1, len(indices_ciclos)))
    count = 0

    for i, color in zip(indices_ciclos, colors):
        count += 1

        df_ch = dict_ciclos_sep[i]['Ch']
        df_dis = dict_ciclos_sep[i]['Dis']

        Q_ch = df_ch['Q'].values
        V_ch = df_ch['CellV'].values
        Q_dis = df_dis['Q'].values
        V_dis = df_dis['CellV'].values

        # Truncar el eje Q y V
        Q_ch_trunc = Q_ch[n_ch:]
        V_ch_trunc = V_ch[n_ch:]
        Q_dis_trunc = Q_dis[n_dis:]  # El array de descarga tiene los voltajes ordenados de mayor a menor.
        V_dis_trunc = V_dis[n_dis:]

        # Crear nuevos DataFrames
        df_ch_trunc = pd.DataFrame({'Q': Q_ch_trunc, 'CellV': V_ch_trunc})
        df_dis_trunc = pd.DataFrame({'Q': Q_dis_trunc, 'CellV': V_dis_trunc})
        
        dict_truncado[i] = {
            'Ch': df_ch_trunc,
            'Dis': df_dis_trunc
        }

        # Aplica filtro Savitzky-Golay
        Q_ch_savgol = savgol_filter(Q_ch_trunc, window_length=windowlength_ch, polyorder=polyorder)
        V_ch_savgol = savgol_filter(V_ch_trunc, window_length=windowlength_ch, polyorder=polyorder)
        dqdv_ch_calc = np.gradient(Q_ch_savgol, V_ch_savgol)
        
        Q_dis_savgol = savgol_filter(Q_dis_trunc, window_length=windowlength_dis, polyorder=polyorder)
        V_dis_savgol = savgol_filter(V_dis_trunc, window_length=windowlength_dis, polyorder=polyorder)
        dqdv_dis_calc = np.gradient(Q_dis_savgol, V_dis_savgol)

        # Gráficos
        #plt.scatter(V_ch, Q_ch - 5000 - count * 200, marker='o', s=1, color='orange')
        #plt.scatter(V_ch_trunc, Q_ch_trunc - 5000 - count * 200, marker='o', s=1, color=color, label=f'Ciclo {i}')
        #plt.scatter(V_ch_savgol, dqdv_ch_calc - count * 200, marker='o', s=1, color=color)
        plt.scatter(V_ch, Q_ch, marker='o', s=1, color='orange')
        plt.scatter(V_ch_trunc, Q_ch_trunc, marker='o', s=1, color=color, label=f'Ciclo {i}')
        plt.scatter(V_ch_savgol, dqdv_ch_calc, marker='o', s=1, color=color)

        plt.scatter(V_dis, Q_dis-np.min(Q_dis), marker='o', s=1, color='orange')
        plt.scatter(V_dis_trunc, Q_dis_trunc-np.min(Q_dis_trunc), marker='o', s=1, color=color)#, label=f'Ciclo {i}')
        plt.scatter(V_dis_savgol, dqdv_dis_calc , marker='o', s=1, color=color)

    #plt.ylim(-7900, 8200)
    #plt.xlim(3.2, 3.75)
    plt.xlabel('Voltage (V)')
    plt.ylabel('dQ/dV (mAh/V)')
    plt.title(f'dQ/dV (TRUNCADO n_ch={n_ch}, n_dis={n_dis}) wl_ch={windowlength_ch}, wl_dis={windowlength_dis}, po={polyorder}')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    return dict_truncado


# ----------- CALCULO DERIVADA CON FILTRO SAVITZKY-GOLAY -------------

def plot_dqdV(indices_ciclos,dict_ciclos_sep, wl_dis=51, wl_ch=153, polyorder=3, colorbar=False):
    '''
    Función simple de plot dqdv con filtro
    Actualiza el dict de entrada con los datos de Q y V suavizados y los valores de dVdQ calculados.
    Devuelve el dict actualizado.

    Parámetros
    ----------
    indices_ciclos : list[int]
        Ciclos a procesar.
    dict_ciclos_sep : dict
        Diccionario con DataFrames de ciclos separados en 'Ch' y 'Dis'.

    wl_dis : int, opcional
        Longitud de la ventana del filtro Savitzky-Golay para descarga. Debe ser un número impar. Por defecto es 51.
    wl_ch : int, opcional
        Longitud de la ventana del filtro Savitzky-Golay para carga. Debe ser un número impar. Por defecto es 3 * wl_dis.
    polyorder : int, opcional
    '''

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
        df_ch['Q_ch_savgol'] = savgol_filter(Q_ch, window_length=wl_ch, polyorder=polyorder)
        df_ch['V_ch_savgol'] = savgol_filter(V_ch, window_length=wl_ch, polyorder=polyorder)
        df_dis['Q_dis_savgol'] = savgol_filter(Q_dis, window_length=wl_dis, polyorder=polyorder)
        df_dis['V_dis_savgol'] = savgol_filter(V_dis, window_length=wl_dis, polyorder=polyorder)

        # Calcula dQdV
        df_ch['dqdv_ch_calc'] = np.gradient(df_ch['Q_ch_savgol'].values, df_ch['V_ch_savgol'].values)
        dqdv_ch = df_ch['dqdv_ch_calc'].values
        df_dis['dqdv_dis_calc'] = np.gradient(df_dis['Q_dis_savgol'].values, df_dis['V_dis_savgol'].values)
        dqdv_dis = df_dis['dqdv_dis_calc'].values

        
        # Plot dQdV
        plt.plot(V_ch, dqdv_ch, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
        plt.plot(V_dis, dqdv_dis, marker='o', linestyle='-',color=color,markersize=0.1)#, label=f'Ciclo {i}')

        
    if len(indices_ciclos) > 10:
        plt.legend().remove()
        
        if plt.colorbar == True:
            # Crear colorbar asociada a los ciclos
            norm = mcolors.Normalize(vmin=min(indices_ciclos), vmax=max(indices_ciclos))
            sm = cm.ScalarMappable(cmap=cm.viridis, norm=norm)
            sm.set_array([])  # requerido
            cbar = plt.colorbar(sm, ax=plt.gca(), ticks=indices_ciclos[::2])
            cbar.set_label('Cycle number')
    else:
        plt.legend()

    plt.xlabel('Voltage (V)')
    plt.ylabel('dQ/dV (mAh/V)')
    plt.title(f'dQ/dV wl_ch={wl_ch}, wl_dis={wl_dis}, po={polyorder}')
    plt.grid(True)
    plt.show()

    return dict_ciclos_sep

def plot_dVdq(indices_ciclos,dict_ciclos_sep, wl_dis=51, wl_ch=153, polyorder=3, colorbar=False):
    '''
    Función simple de plot dqdv calculada con filtro Savitzky-Golay.
    Actualiza el dict de entrada con los datos de Q y V suavizados y los valores de dVdQ calculados.
    Devuelve el dict actualizado.
    '''

    # Graficar dVdQ calculado
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
        df_ch['Q_ch_savgol'] = savgol_filter(Q_ch, window_length=wl_ch, polyorder=polyorder)
        df_ch['V_ch_savgol'] = savgol_filter(V_ch, window_length=wl_ch, polyorder=polyorder)
        df_dis['Q_dis_savgol'] = savgol_filter(Q_dis, window_length=wl_dis, polyorder=polyorder)
        df_dis['V_dis_savgol'] = savgol_filter(V_dis, window_length=wl_dis, polyorder=polyorder)

        # Calcula dVdQ
        df_ch['dvdq_ch_calc'] = np.gradient(df_ch['V_ch_savgol'].values,Q_ch)
        dvdq_ch = df_ch['dvdq_ch_calc'].values
        df_dis['dvdq_dis_calc'] = np.gradient(df_dis['V_dis_savgol'].values, Q_dis)
        dvdq_dis = df_dis['dvdq_dis_calc'].values

        # Plot V vs Q
        #plt.scatter(Q_ch, V_ch_savgol-4, marker='o', linestyle='-',color=color, label=f'Ciclo {i}', s=1)
        #plt.scatter(Q_dis-np.min(Q_dis), V_dis_savgol-4, marker='o', linestyle='-',color=color, s=1)#, label=f'Ciclo {i}')

        # Plot dVdQ vs Q
        #plt.plot(Q_ch, dvdq_ch, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
        #plt.plot(Q_dis-np.min(Q_dis), dvdq_dis, marker='o', linestyle='-',color=color,markersize=0.1)#, label=f'Ciclo {i}')
        plt.scatter(Q_ch, dvdq_ch, marker='o', linestyle='-',color=color, label=f'Ciclo {i}', s=1)
        plt.scatter(Q_dis-np.min(Q_dis), dvdq_dis, marker='o', linestyle='-',color=color, s=1)#, label=f'Ciclo {i}')

            
    if len(indices_ciclos) > 10:
        plt.legend().remove()
        
        if plt.colorbar == True:
            # Crear colorbar asociada a los ciclos
            norm = mcolors.Normalize(vmin=min(indices_ciclos), vmax=max(indices_ciclos))
            sm = cm.ScalarMappable(cmap=cm.viridis, norm=norm)
            sm.set_array([])  # requerido
            cbar = plt.colorbar(sm, ax=plt.gca(), ticks=indices_ciclos[::2])
            cbar.set_label('Cycle number')
    else:
        plt.legend()


    #plt.ylim(-0.0025,0.0025) # para dV/dQ
    plt.xlabel('Voltage (V)')
    plt.ylabel('dQ/dV (mAh/V)')
    plt.title(f'dQ/dV wl_ch={wl_ch}, wl_dis={wl_dis}, po={polyorder}')
    plt.grid(True)
    plt.show()

    return dict_ciclos_sep

