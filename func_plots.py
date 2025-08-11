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
Funciones para hacer plots simples.

'''


# %% -------  Plots simples --------------------------------------------------------------------

def plot_n_cycles(indices_ciclos, dict, x, y, nombre_grafico='plot', scatter=False):
    '''
    x,y = 'Time', 'CellV', 'dCapacity/dCellV', 'dCellV/dCapacity' 'Q'

    dict es:  
        dict_ciclos_sep = {ciclo: {'Ch': df_ciclo_ch, 'Dis': df_ciclo_dis}} 
        Uso: ciclos_sep[100]['Ch'] te da el df de carga del ciclo 100
    '''

    plt.figure(figsize=(8,5))
    colors = cm.viridis(np.linspace(0, 1, len(indices_ciclos)))

    for i, color in zip(indices_ciclos, colors):
        df_ch = dict[i]['Ch']
        df_dis = dict[i]['Dis']

        x_ch = df_ch[x].values
        y_ch = df_ch[y].values
        x_dis = df_dis[x].values
        y_dis = df_dis[y].values

        if scatter:
            # y vs x Juntos
            plt.scatter(x_ch, y_ch, marker='o', linestyle='-',color=color,s=1)#, markersize=0.1)
            #plt.scatter(x_dis, y_dis, marker='o', linestyle='-',color=color,s=0.1)#,markersize=0.1)
        else:
            # y vs x Juntos
            
            # ------- Charge -------
            plt.plot(x_ch, y_ch, marker='o', linestyle='-',color=color, markersize=0.1, label=f'Ciclo {i}')
            # -- para 1/dVdQ = dQdV vs CellV
            #plt.plot(x_ch, 1/y_ch, marker='o', linestyle='-',color=color, markersize=0.1, label=f'Ciclo {i}')
            
            # ------- Discharge -------
            #plt.plot(x_dis, y_dis, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
            # -- para cellV vs Time
            #plt.plot(x_dis-np.max(x_ch), y_dis, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
            # -- para Q vs cellV
            #plt.plot(x_dis-np.min(x_dis), y_dis, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
            # -- para CellV vs Q
            #plt.plot(x_dis, y_dis-np.min(y_dis), marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
            # -- para Q vs dVdQ
            plt.plot(x_dis-np.min(x_dis), y_dis, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
            # -- para 1/dVdQ = dQdV vs CellV
            #plt.plot(x_dis, 1/y_dis, marker='o', linestyle='-',color=color,markersize=0.1)#, label=f'Ciclo {i}')

            # chequeos
            #x_max_ch=np.max(x_ch)
            #x_min_dis=np.min(x_dis)
            #plt.axvline(x_max_ch, color='gray', linestyle='--', linewidth=1, label=f'Q max ({x_max_ch:.2f} mAh)')
            #plt.axvline(x_min_dis, color='gray', linestyle='--', linewidth=1, label=f'Q max ({x_min_dis:.2f} mAh)')


    # Crear colorbar asociada a los ciclos
    #norm = mcolors.Normalize(vmin=min(indices_ciclos), vmax=max(indices_ciclos))
    #sm = cm.ScalarMappable(cmap=cm.viridis, norm=norm)
    #sm.set_array([])  # requerido
    #cbar = plt.colorbar(sm, ax=plt.gca(), ticks=indices_ciclos[::2])
    #cbar.set_label('Cycle number')

    x_string = 'dQdV' if x == 'dCapacity/dCellV' else 'dVdQ' if x == 'dCellV/dCapacity' else x
    y_string = 'dQdV' if y == 'dCapacity/dCellV' else 'dVdQ' if y == 'dCellV/dCapacity' else y
    
    labels_con_unidades = {
        'Time': 'Time (hour)',
        'Q': 'Q (mAh)',
        'CellV': 'CellV (V)',
        'dCapacity/dCellV': 'dQdV (mAh/V)',
        'dCellV/dCapacity': 'dVdQ (V/mAh)',
        'Current': 'Current (A)',
        }

    x_label = labels_con_unidades.get(x, x)
    y_label = labels_con_unidades.get(y, y)
    
    plt.ylim(-0.0025,0.0025) # para dV/dQ
    #plt.ylim(0,0.002) # para dV/dQ charge
    #plt.ylim(-0.002,0) # para dV/dQ discharge
    #plt.xlim(0,3000)
    #plt.ylim(2.9,4.5)
    #plt.xlim(-60,2650)
    
    plt.xlabel(f'{x_label}')
    plt.ylabel(f'{y_label}')
    plt.title(f'{y} vs {x}')
    plt.grid(True)
    #plt.legend()
    #plt.legend()
    plt.savefig(f'./output/{nombre_grafico}_{y_string}vs{x_string}.png', dpi=300)
    plt.show()
    return


def plot_n_cycles_superpuesto(indices_ciclos, dict, x, y, nombre_grafico='plot', scatter=False):
    '''
    x,y = 'Time', 'CellV', 'dCapacity/dCellV', 'Q'

    dict es:  
        dict_ciclos_sep = {ciclo: {'Ch': df_ciclo_ch, 'Dis': df_ciclo_dis}} 
        Uso: ciclos_sep[100]['Ch'] te da el df de carga del ciclo 100
    '''

    fig, ax = plt.subplots(figsize=(8,5))
    ax2 = ax.twinx()
    colors = cm.viridis(np.linspace(0, 1, len(indices_ciclos)))

    for i, color in zip(indices_ciclos, colors):
        df_ch = dict[i]['Ch']
        df_dis = dict[i]['Dis']

        x_ch = df_ch[x].values
        y_ch = df_ch[y].values
        x_dis = df_dis[x].values
        y_dis = df_dis[y].values

        if scatter:
            # y vs x Juntos
            ax.scatter(x_ch, y_ch, marker='o', linestyle='-',color=color,s=1)#, markersize=0.1)
            ax.scatter(x_dis, y_dis, marker='o', linestyle='-',color=color,s=0.1)#,markersize=0.1)
        else:
            # y vs x Juntos
            ax.plot(x_ch, y_ch, marker='o', linestyle='-',color=color, markersize=0.1, label=f'Ciclo {i}')
            ax.plot(x_dis, y_dis, marker='o', linestyle='-',color=color,markersize=0.1)
            ax2.scatter(df_ch['Time'][::100], df_ch['Current'][::100]/1000, marker='*', color=color, label=f'Current',facecolors='none')
            ax2.scatter(df_dis['Time'][::100], df_dis['Current'][::100]/1000, marker='*', color=color, facecolors='none')
            

    # Crear colorbar asociada a los ciclos
    #norm = mcolors.Normalize(vmin=min(indices_ciclos), vmax=max(indices_ciclos))
    #sm = cm.ScalarMappable(cmap=cm.viridis, norm=norm)
    #sm.set_array([])  # requerido
    #cbar = plt.colorbar(sm, ax=plt.gca(), ticks=indices_ciclos[::2])
    #cbar.set_label('Cycle number')

    x_string = x.replace('dCapacity/dCellV', 'dQdV') if x == 'dCapacity/dCellV' else x
    y_string = y.replace('dCapacity/dCellV', 'dQdV') if y == 'dCapacity/dCellV' else y

    ax2.set_ylabel('Current (A)')
    ax2.set_ylabel('Current (A)')
    ax2.set_ylim(-4,4)
    ax.set_ylabel(f'{y}')
    ax.set_title(f'{y} vs {x}')
    ax.grid(True)
    ax.legend()
    #ax2.legend()
    plt.tight_layout()
    fig.savefig(f'./output/{nombre_grafico}_{y_string}vs{x_string}.png', dpi=300)
    #plt.show()
    return

def plot_n_cycles_withCurrent(indices_ciclos, dict, x, y, nombre_grafico='plot', scatter=False):
    '''
    x,y = 'Time', 'CellV', 'dCapacity/dCellV', 'Q'

    dict es:  
        dict_ciclos_sep = {ciclo: {'Ch': df_ciclo_ch, 'Dis': df_ciclo_dis}} 
        Uso: ciclos_sep[100]['Ch'] te da el df de carga del ciclo 100
    '''

    fig = plt.figure(figsize=(10, 7), constrained_layout=True)
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1], hspace=0.15)  # más alto arriba

    ax1 = fig.add_subplot(gs[0])  # eje superior
    ax2 = fig.add_subplot(gs[1], sharex=ax1)  # eje inferior, comparte eje x
    
    colors = cm.viridis(np.linspace(0, 1, len(indices_ciclos)))

    for i, color in zip(indices_ciclos, colors):
        df_ch = dict[i]['Ch']
        df_dis = dict[i]['Dis']

        x_ch = df_ch[x].values
        y_ch = df_ch[y].values
        x_dis = df_dis[x].values
        y_dis = df_dis[y].values

        if scatter:
            # y vs x Juntos
            ax1.scatter(x_ch, y_ch, marker='o', linestyle='-',color=color,s=1)#, markersize=0.1)
            ax1.scatter(x_dis, y_dis, marker='o', linestyle='-',color=color,s=0.1)#,markersize=0.1)
        else:
            # y vs x Juntos
            ax1.plot(x_ch, y_ch, marker='o', linestyle='-',color=color, markersize=0.1, label=f'Ciclo {i}')
            ax1.plot(x_dis, y_dis, marker='o', linestyle='-',color=color,markersize=0.1)
            ax2.plot(df_ch['Time'][::100], df_ch['Current'][::100]/1000, marker='o', linestyle='-',color=color, markersize=0.1, label=f'Ciclo {i}')
            ax2.plot(df_dis['Time'][::100], df_dis['Current'][::100]/1000, marker='o', linestyle='-',color=color,markersize=0.1)
            #ax2.scatter(df_ch['Time'][::100], df_ch['Current'][::100]/1000, marker='*', color=color, label=f'Current',facecolors='none')
            #ax2.scatter(df_dis['Time'][::100], df_dis['Current'][::100]/1000, marker='*', color=color, facecolors='none')
            

    # Crear colorbar asociada a los ciclos
    #norm = mcolors.Normalize(vmin=min(indices_ciclos), vmax=max(indices_ciclos))
    #sm = cm.ScalarMappable(cmap=cm.viridis, norm=norm)
    #sm.set_array([])  # requerido
    #cbar = plt.colorbar(sm, ax=plt.gca(), ticks=indices_ciclos[::2])
    #cbar.set_label('Cycle number')

    x_string = x.replace('dCapacity/dCellV', 'dQdV') if x == 'dCapacity/dCellV' else x
    y_string = y.replace('dCapacity/dCellV', 'dQdV') if y == 'dCapacity/dCellV' else y

    ax2.set_ylabel('Current (A)')
    ax2.set_ylabel('Current (A)')
    ax2.set_ylim(-4,4)
    ax1.set_ylabel(f'{y}')
    ax2.set_xlabel(f'{x}')
    ax1.set_title(f'{y} vs {x}')
    ax1.grid(True)
    ax1.legend()
    #ax2.legend()
    #plt.tight_layout()
    fig.savefig(f'./output/{nombre_grafico}_{y_string}vs{x_string}.png', dpi=300)
    #plt.show()
    return

