from pathlib import Path
import numpy as np
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import funciones_ic as f
from scipy.signal import savgol_filter



'''
Funciones para trabajar con las derivadas IC, DV.

'''

def resolucion_V(indices_ciclos,dict_ciclos_sep):
    '''
    estudio resolucion datos de voltaje y tamaño ventana de suavizado
    '''

    puntos_por_ventana_ch = []
    puntos_por_ventana_dis = []
    resoluciones_ch = []
    resoluciones_dis = []

    for i in indices_ciclos:
        df_ch = dict_ciclos_sep[i]['Ch']
        df_dis = dict_ciclos_sep[i]['Dis']
        Q_ch = df_ch['Q'].values
        V_ch = df_ch['CellV'].values
        Q_dis = df_dis['Q'].values
        V_dis = df_dis['CellV'].values

        # Para ver la resolución y el tamaño de window_length
        resolucion_prom_ch = np.mean(np.abs(np.diff(V_ch))) # Promedio del salto (paso) entre elementos consecutivos
        print(f"Salto promedio entre elementos consecutivos (resolución) de V_ch: {resolucion_prom_ch:.4f} V")
        ventana_en_volt = 0.002  # 2 mV
        window_length_ch = int(np.round(ventana_en_volt / resolucion_prom_ch))
        print(f"Ventana de suavizado: {window_length_ch} puntos")
        
        resolucion_prom_dis = np.mean(np.abs(np.diff(V_dis)))
        print(f"Salto promedio entre elementos consecutivos (resolución) de V_dis: {resolucion_prom_dis}")
        ventana_en_volt = 0.002  # 2 mV
        window_length_dis = int(np.round(ventana_en_volt / resolucion_prom_dis))
        print(f"Ventana de suavizado: {window_length_dis} puntos")

        puntos_por_ventana_ch.append(window_length_ch)
        resoluciones_ch.append(resolucion_prom_ch)
        puntos_por_ventana_dis.append(window_length_dis)
        resoluciones_dis.append(resolucion_prom_dis)

    # histograma de resolución de voltaje
    plt.figure(figsize=(8, 5))
    ciclos = indices_ciclos
    ventanas = puntos_por_ventana_ch  # Resolución de voltaje en mV
    #ventanas = puntos_por_ventana_dis

    plt.bar(ciclos, ventanas, width=50, color='skyblue', label='Charge')
    plt.yticks(range(0, 18, 1))
    plt.xticks(indices_ciclos)
    plt.xlabel('Ciclo')
    plt.ylabel('Puntos por ventanas de 2 mV')
    plt.title('Resolución de voltaje según ciclo')
    plt.grid(True, axis='y')
    plt.legend()
    plt.tight_layout()
    plt.show()

    # grafico resolución de voltaje
    plt.figure(figsize=(8, 5))
    ciclos = indices_ciclos
    resoluciones = resoluciones_ch  # Resolución de voltaje en mV
    #resoluciones = resoluciones_dis
    resoluciones = [r * 1000 for r in resoluciones]

    plt.scatter(ciclos, resoluciones, color='c', label='Charge')
    plt.ylim(0, 0.8)
    plt.xticks(indices_ciclos)
    plt.xlabel('Ciclo')
    plt.ylabel('Resolución de voltaje (mV)')
    plt.title('Resolución de voltaje según ciclo')
    plt.grid(True, axis='y')
    plt.legend()
    plt.tight_layout()
    plt.show()


def resolucion_Q(indices_ciclos,dict_ciclos_sep):
    '''
    estudio resolucion de Q
    '''

    puntos_por_ventana_ch = []
    puntos_por_ventana_dis = []
    resoluciones_ch = []
    resoluciones_dis = []

    for i in indices_ciclos:
        df_ch = dict_ciclos_sep[i]['Ch']
        df_dis = dict_ciclos_sep[i]['Dis']
        Q_ch = df_ch['Q'].values
        V_ch = df_ch['CellV'].values
        Q_dis = df_dis['Q'].values
        V_dis = df_dis['CellV'].values

        # Para ver la resolución y el tamaño de window_length
        resolucion_prom_ch = np.mean(np.abs(np.diff(Q_ch))) # Promedio del salto (paso) entre elementos consecutivos
        print(f"Salto promedio entre elementos consecutivos (resolución) de Q_ch: {resolucion_prom_ch:.4f} mAh")
        #ventana_en_volt = 0.002  # 2 mV
        #window_length_ch = int(np.round(ventana_en_volt / resolucion_prom_ch))
        #print(f"Ventana de suavizado: {window_length_ch} puntos")
        
        resolucion_prom_dis = np.mean(np.abs(np.diff(Q_dis)))
        print(f"Salto promedio entre elementos consecutivos (resolución) de Q_dis: {resolucion_prom_dis} mAh")
        #ventana_en_volt = 0.002  # 2 mV
        #window_length_dis = int(np.round(ventana_en_volt / resolucion_prom_dis))
        #print(f"Ventana de suavizado: {window_length_dis} puntos")

        #puntos_por_ventana_ch.append(window_length_ch)
        resoluciones_ch.append(resolucion_prom_ch)
        #puntos_por_ventana_dis.append(window_length_dis)
        resoluciones_dis.append(resolucion_prom_dis)

    # histograma de resolución de voltaje
    #plt.figure(figsize=(8, 5))
    #ciclos = indices_ciclos
    #ventanas = puntos_por_ventana_ch  # Resolución de voltaje en mV
    #ventanas = puntos_por_ventana_dis

    #plt.bar(ciclos, ventanas, width=50, color='skyblue', label='Charge')
    #plt.yticks(range(0, 18, 1))
    #plt.xticks(indices_ciclos)
    #plt.xlabel('Ciclo')
    #plt.ylabel('Puntos por ventanas de 2 mV')
    #plt.title('Resolución de voltaje según ciclo')
    #plt.grid(True, axis='y')
    #plt.legend()
    #plt.tight_layout()
    #plt.show()

    # grafico resolución de voltaje
    plt.figure(figsize=(8, 5))
    ciclos = indices_ciclos
    resoluciones = resoluciones_ch  # Resolución de Q
    #resoluciones = resoluciones_dis
    #resoluciones = [r * 1000 for r in resoluciones]

    plt.scatter(ciclos, resoluciones, color='c', label='Charge')
    plt.ylim(0.2, 0.35)
    plt.xticks(indices_ciclos)
    plt.xlabel('Ciclo')
    plt.ylabel('Resolución de Q (mAh)')
    plt.title('Resolución de Q según ciclo')
    plt.grid(True, axis='y')
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_dqdv_muchos_wl(indices_ciclos,dict):

    windowlengths_dis = np.array([31, 51, 71, 91, 101, 111, 131, 121, 151])  # valores a probar
    windowlengths_dis = np.array([41, 51, 61, 71, 81, 91])  # valores a probar
    windowlengths_dis = np.array([51,53,57,59,61,63])
    windowlengths_ch = windowlengths_dis * 3
    polyorder = 3

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


def plot_dqdv(indices_ciclos,dict_ciclos_sep):
    '''
    Función simple de plot dqdv con filtro
    '''
    windowlength_dis = 51  # Longitud de la ventana del filtro
    windowlength_ch = 3 * windowlength_dis  
    polyorder = 3 # Orden del polinomio del filtro

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
        df_ch['Q_ch_savgol'] = savgol_filter(Q_ch, window_length=windowlength_ch, polyorder=polyorder)
        df_ch['V_ch_savgol'] = savgol_filter(V_ch, window_length=windowlength_ch, polyorder=polyorder)
        df_dis['Q_dis_savgol'] = savgol_filter(Q_dis, window_length=windowlength_dis, polyorder=polyorder)
        df_dis['V_dis_savgol'] = savgol_filter(V_dis, window_length=windowlength_dis, polyorder=polyorder)
        
        Q_ch_savgol = df_ch['Q_ch_savgol'].values
        V_ch_savgol = df_ch['V_ch_savgol'].values
        dqdv_ch_calc = np.gradient(Q_ch_savgol, V_ch_savgol)
        dqdv_ch = dqdv_ch_calc
        
        Q_dis_savgol = df_dis['Q_dis_savgol'].values
        V_dis_savgol = df_dis['V_dis_savgol'].values

        Q_dis_min = Q_dis_savgol.min()
        #plt.plot(V_dis_savgol,Q_dis_savgol-Q_dis_min, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
        dqdv_dis_calc = np.gradient(Q_dis_savgol, V_dis_savgol)
        dqdv_dis = dqdv_dis_calc

        plt.plot(V_ch, dqdv_ch, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
        plt.plot(V_dis, dqdv_dis, marker='o', linestyle='-',color=color,markersize=0.1)#, label=f'Ciclo {i}')

        
        
        # Asegurate de que sea impar
        #if window_length % 2 == 0:
        #    window_length += 1
        

    # Crear colorbar asociada a los ciclos
    #norm = mcolors.Normalize(vmin=min(ciclos), vmax=max(ciclos))
    #sm = cm.ScalarMappable(cmap=cm.viridis, norm=norm)
    #sm.set_array([])  # requerido
    #cbar = plt.colorbar(sm, ax=plt.gca(), ticks=ciclos[::2])
    #cbar.set_label('Cycle number')

    plt.xlabel('Voltage (V)')
    plt.ylabel('dQ/dV (mAh/V)')
    plt.title(f'dQ/dV wl_ch={windowlength_ch}, wl_dis={windowlength_dis}, po={polyorder}')
    plt.grid(True)
    plt.legend()
    plt.show()


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
        #Q_ch_trunc = Q_ch[n:-n]
        #V_ch_trunc = V_ch[n:-n]
        Q_ch_trunc = Q_ch[n_ch:]
        V_ch_trunc = V_ch[n_ch:]
        Q_dis_trunc = Q_dis[n_dis:]  # El array de descarga tiene los voltajes ordenados de mayor a menor.
        V_dis_trunc = V_dis[n_dis:]

        # Crear nuevos DataFrames
        df_ch_trunc = pd.DataFrame({'Q': Q_ch_trunc, 'CellV': V_ch_trunc})
        df_dis_trunc = pd.DataFrame({'Q': Q_dis_trunc, 'CellV': V_dis_trunc})
        #df_dis_trunc = pd.DataFrame({'Q': Q_dis, 'CellV': V_dis})  # sin truncar

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


#no se usa
def detectar_cambios_resolucion(indices_ciclos, dict_ciclos_sep, umbral=1.5):
    """
    Detecta y grafica cambios significativos en la resolución de la señal de voltaje.
    """
    
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
    
        dV_ch = np.abs(np.diff(V_ch))
        paso_medio_ch = np.median(dV_ch)
        indices_cambio_ch = np.where(dV_ch > umbral * paso_medio_ch)[0]

        dV_dis = np.abs(np.diff(V_dis))
        paso_medio_dis = np.median(dV_dis)
        indices_cambio_dis = np.where(dV_dis > umbral * paso_medio_dis)[0]

        plt.plot(dV_ch, label='|ΔV|')
        plt.axhline(paso_medio_ch, color='green', linestyle='--', label='Paso medio')
        plt.axhline(umbral * paso_medio_ch, color='red', linestyle='--', label=f'Umbral ({umbral}×)')
        plt.scatter(indices_cambio_ch, dV_ch[indices_cambio_ch], color='red', zorder=5, label='Cambio detectado')

        plt.plot(dV_dis, label='|ΔV|')
        plt.axhline(paso_medio_dis, color='green', linestyle='--', label='Paso medio')
        plt.axhline(umbral * paso_medio_dis, color='red', linestyle='--', label=f'Umbral ({umbral}×)')
        plt.scatter(indices_cambio_dis, dV_dis[indices_cambio_dis], color='red', zorder=5, label='Cambio detectado')
    

    # Gráfico
    #plt.figure(figsize=(8, 4))
    #plt.plot(dV, label='|ΔV|')
    #plt.axhline(paso_medio, color='green', linestyle='--', label='Paso medio')
    #plt.axhline(umbral * paso_medio, color='red', linestyle='--', label=f'Umbral ({umbral}×)')
    #plt.scatter(indices_cambio, dV[indices_cambio], color='red', zorder=5, label='Cambio detectado')
    plt.xlabel('Índice')
    plt.ylabel('|ΔV| entre puntos')
    plt.title(f'Cambios de resolución')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return indices_cambio.tolist()


def plot_dvdq(indices_ciclos,dict_ciclos_sep):
    '''
    Función simple de plot dqdv con filtro
    '''
    windowlength_dis = 51  # Longitud de la ventana del filtro
    windowlength_ch = 3 * windowlength_dis  
    polyorder = 3 # Orden del polinomio del filtro

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
        df_ch['Q_ch_savgol'] = savgol_filter(Q_ch, window_length=windowlength_ch, polyorder=polyorder)
        df_ch['V_ch_savgol'] = savgol_filter(V_ch, window_length=windowlength_ch, polyorder=polyorder)
        df_dis['Q_dis_savgol'] = savgol_filter(Q_dis, window_length=windowlength_dis, polyorder=polyorder)
        df_dis['V_dis_savgol'] = savgol_filter(V_dis, window_length=windowlength_dis, polyorder=polyorder)
        
        Q_ch_savgol = df_ch['Q_ch_savgol'].values
        V_ch_savgol = df_ch['V_ch_savgol'].values
        dvdq_ch_calc = np.gradient(V_ch_savgol,Q_ch)
        dvdq_ch = dvdq_ch_calc
        
        Q_dis_savgol = df_dis['Q_dis_savgol'].values
        V_dis_savgol = df_dis['V_dis_savgol'].values
        Q_dis_min = Q_dis_savgol.min()
        #plt.plot(V_dis_savgol,Q_dis_savgol-Q_dis_min, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
        dvdq_dis_calc = np.gradient(V_dis_savgol, Q_dis)
        dvdq_dis = dvdq_dis_calc

        # Plot V vs Q
        #plt.scatter(Q_ch, V_ch_savgol-4, marker='o', linestyle='-',color=color, label=f'Ciclo {i}', s=1)
        #plt.scatter(Q_dis-np.min(Q_dis), V_dis_savgol-4, marker='o', linestyle='-',color=color, s=1)#, label=f'Ciclo {i}')

        # Plot dVdQ vs Q
        #plt.plot(Q_ch, dvdq_ch, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
        #plt.plot(Q_dis-np.min(Q_dis), dvdq_dis, marker='o', linestyle='-',color=color,markersize=0.1)#, label=f'Ciclo {i}')
        plt.scatter(Q_ch_savgol, dvdq_ch, marker='o', linestyle='-',color=color, label=f'Ciclo {i}', s=1)
        plt.scatter(Q_dis_savgol-np.min(Q_dis_savgol), dvdq_dis, marker='o', linestyle='-',color=color, s=1)#, label=f'Ciclo {i}')

        # Asegurate de que sea impar
        #if window_length % 2 == 0:
        #    window_length += 1
        

    # Crear colorbar asociada a los ciclos
    #norm = mcolors.Normalize(vmin=min(ciclos), vmax=max(ciclos))
    #sm = cm.ScalarMappable(cmap=cm.viridis, norm=norm)
    #sm.set_array([])  # requerido
    #cbar = plt.colorbar(sm, ax=plt.gca(), ticks=ciclos[::2])
    #cbar.set_label('Cycle number')

    #plt.ylim(-0.0025,0.0025) # para dV/dQ
    plt.xlabel('Voltage (V)')
    plt.ylabel('dQ/dV (mAh/V)')
    plt.title(f'dQ/dV wl_ch={windowlength_ch}, wl_dis={windowlength_dis}, po={polyorder}')
    plt.grid(True)
    plt.legend()
    plt.show()

