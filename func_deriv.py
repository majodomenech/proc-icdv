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

def resolucion(indices_ciclos,dict_ciclos_sep):
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


def dqdv_muchos_wl(indices_ciclos,dict):

    windowlengths = [71, 91, 101, 111, 131, 121, 151, 161, 171]  # valores a probar
    polyorder = 3

    ncols = 3
    nrows = int(np.ceil(len(windowlengths) / ncols))

    fig, axs = plt.subplots(nrows, ncols, figsize=(12, 3 * nrows), sharex=True, sharey=True)
    axs = axs.flatten()

    colors = cm.viridis(np.linspace(0, 1, len(indices_ciclos)))

    for ax, wl in zip(axs, windowlengths):
        for i, color in zip(indices_ciclos, colors):
            df_ch = dict[i]['Ch']
            df_dis = dict[i]['Dis']

            Q_ch = df_ch['Q'].values
            V_ch = df_ch['CellV'].values
            Q_dis = df_dis['Q'].values
            V_dis = df_dis['CellV'].values

            # Verifica que wl sea menor que el tamaño de Q_dis y sea impar
            if wl >= len(Q_dis):
                continue
            if wl % 2 == 0:
                wl += 1

            Q_ch_savgol = savgol_filter(Q_ch, window_length=wl, polyorder=polyorder)
            V_ch_savgol = savgol_filter(V_ch, window_length=wl, polyorder=polyorder)
            dqdv_ch = np.gradient(Q_ch_savgol, V_ch_savgol)    
            Q_dis_savgol = savgol_filter(Q_dis, window_length=wl, polyorder=polyorder)
            V_dis_savgol = savgol_filter(V_dis, window_length=wl, polyorder=polyorder)
            dqdv_dis = np.gradient(Q_dis_savgol, V_dis_savgol)

            ax.plot(V_ch, dqdv_ch, color=color, markersize=0.1)
            #ax.plot(V_dis, dqdv_dis, color=color, markersize=0.1)

        ax.set_title(f'windowlength={wl}')
        ax.set_xlabel('Voltage (V)')
        #ax.set_ylim(-6000,1000)
        ax.set_ylim(-1000,11000)
        ax.set_ylabel('dQ/dV')

    # Eliminar subplots vacíos si hay
    for ax in axs[len(windowlengths):]:
        fig.delaxes(ax)

    plt.tight_layout()
    plt.show()


def plot_dqdv(indices_ciclos,dict_ciclos_sep):
    windowlength = 153  # Longitud de la ventana del filtro
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
        df_ch['Q_ch_savgol'] = savgol_filter(Q_ch, window_length=windowlength, polyorder=polyorder)
        df_ch['V_ch_savgol'] = savgol_filter(V_ch, window_length=windowlength, polyorder=polyorder)
        df_dis['Q_dis_savgol'] = savgol_filter(Q_dis, window_length=windowlength, polyorder=polyorder)
        df_dis['V_dis_savgol'] = savgol_filter(V_dis, window_length=windowlength, polyorder=polyorder)
        
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
        plt.plot(V_dis, dqdv_dis, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
        
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
    plt.title(f'dQ/dV wl={windowlength}, po={polyorder}')
    plt.grid(True)
    plt.legend()
    plt.show()