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


def plot_soh(dict_ciclos_sep, ciclos, nombre_archivo, output_folder):
    """
    Calcula qmax por ciclo, obtiene el qmax global, calcula SoH y genera
    un gráfico de SoH coloreado según el número de ciclo.
    
    Parámetros:
        dict_ciclos_sep : dict con estructura {ciclo: {'Ch': df_ch, 'Dis': df_dis}}
        ciclos          : lista de ciclos a incluir en el gráfico
        nombre_archivo  : nombre base del archivo de salida
        output_folder   : carpeta donde guardar la imagen
    """

    # ---- Cálculo de qmax global ----
    soh_data = []
    for ciclo in ciclos:
        qmax = dict_ciclos_sep[ciclo]['Ch']['Q'].max()
        soh_data.append({'ciclo': ciclo, 'qmax': qmax})

    qmax_global = max(d['qmax'] for d in soh_data)
    ciclo_qmax_global = next(d['ciclo'] for d in soh_data if d['qmax'] == qmax_global)

    print(f"La capacidad máxima es {qmax_global:.3f} mAh y se alcanza en el ciclo {ciclo_qmax_global}.")

    # ---- Calcular SoH ----
    for d in soh_data:
        d['soh'] = 100 * d['qmax'] / qmax_global

    # ---- DataFrame ordenado ----
    df_soh = pd.DataFrame(soh_data).sort_values('ciclo')

    # ---- Gráfico ----
    norm = mcolors.Normalize(vmin=df_soh['ciclo'].min(), 
                              vmax=df_soh['ciclo'].max())
    cmap = cm.viridis

    plt.figure(figsize=(7, 5))
    #plt.rcParams.update({'font.size': 18})

    plt.plot(df_soh['ciclo'], df_soh['soh'], linestyle='-', color='gray', zorder=1)
    plt.scatter(df_soh['ciclo'], df_soh['soh'],
                c=df_soh['ciclo'], cmap=cmap, norm=norm,
                s=30, zorder=2)

    plt.xlabel('Cycle number')
    plt.ylabel('State of Health (%)')
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(output_folder / f'{nombre_archivo}_SoH_vs_cycle_colorido.png',
                dpi=300)
    plt.show()

    return df_soh, qmax_global, ciclo_qmax_global


def plot_n_cycles_dqdv(indices_ciclos, dict, nombre_grafico='plot_dqdv', scatter=False):
    '''
    x,y = 'CellV', 'dCapacity/dCellV'

    dict es:  
        dict_ciclos_sep = {ciclo: {'Ch': df_ciclo_ch, 'Dis': df_ciclo_dis}} 
        Uso: ciclos_sep[100]['Ch'] te da el df de carga del ciclo 100
    '''

    plt.figure(figsize=(8,5))
    colors = cm.viridis(np.linspace(0, 1, len(indices_ciclos)))

    x = 'CellV'
    y = 'dCapacity/dCellV'

    for i, color in zip(indices_ciclos, colors):
        df_ch = dict[i]['Ch']
        df_dis = dict[i]['Dis']

        x_ch = df_ch[x].values
        y_ch = df_ch[y].values
        x_dis = df_dis[x].values
        y_dis = df_dis[y].values

        if scatter:
            plt.scatter(x_ch, y_ch, marker='o', linestyle='-',color=color,s=1)#, markersize=0.1)
            plt.scatter(x_dis, y_dis, marker='o', linestyle='-',color=color,s=0.1)#,markersize=0.1)
        else:
            # ------- Charge -------
            plt.plot(x_ch, y_ch, marker='o', linestyle='-',color=color, markersize=0.1, label=f'Ciclo {i}')
            
            # ------- Discharge -------
            plt.plot(x_dis, y_dis, marker='o', linestyle='-',color=color,markersize=0.1)

            # chequeos
            #x_max_ch=np.max(x_ch)
            #x_min_dis=np.min(x_dis)
            #plt.axvline(x_max_ch, color='gray', linestyle='--', linewidth=1, label=f'Q max ({x_max_ch:.2f} mAh)')
            #plt.axvline(x_min_dis, color='gray', linestyle='--', linewidth=1, label=f'Q max ({x_min_dis:.2f} mAh)')

    if len(indices_ciclos) > 10:
        plt.legend().remove()
        
        # Crear colorbar asociada a los ciclos
        norm = mcolors.Normalize(vmin=min(indices_ciclos), vmax=max(indices_ciclos))
        sm = cm.ScalarMappable(cmap=cm.viridis, norm=norm)
        sm.set_array([])  # requerido
        # ---- Limitar la colorbar a máximo 20 ticks ----
        n_ticks = min(20, len(indices_ciclos))
        ticks_cb = np.linspace(min(indices_ciclos), max(indices_ciclos), n_ticks, dtype=int)
        cbar = plt.colorbar(sm, ax=plt.gca(), ticks=ticks_cb)
        cbar.ax.tick_params(labelsize=12)   # <--- ajustar fontsize de los ticks
        cbar.set_label('Cycle number', fontsize=14)
        #cbar = plt.colorbar(sm, ax=plt.gca(), ticks=indices_ciclos[::2])
    else:
        plt.legend()
    

    x_string = 'dQdV'
    
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
    
    #plt.ylim(-0.0025,0.0025) # para dV/dQ
    #plt.ylim(0,0.002) # para dV/dQ charge
    #plt.ylim(-0.002,0) # para dV/dQ discharge
    #plt.xlim(0,3000)
    #plt.ylim(2.9,4.5)
    #plt.xlim(-60,2650)
    
    plt.xlabel(f'{x_label}', fontsize=14)
    plt.ylabel(f'{y_label}', fontsize=14)
    # ticks
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    plt.title(f'{y} vs {x}', fontsize=12)
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(f'../output/{nombre_grafico}_dQdVvsCellV.png', dpi=300)
    plt.show()
    return


def plot_n_cycles_tvsV_continuo(indices_ciclos, dict, nombre_grafico='plot', scatter=False):
    # esta casi perfecto, no lo uso porque el tiempo acumulado no tiene sentido si yo agarro un subset (cada 3 por ej) de los ciclos totales
    # el unico error es que si yo paso indices_ciclos[algo1:algo1], el acumulado siempre arranca en cero, y no en el tiempo del índice algo1-1 
    '''
    x,y = 'Time', 'CellV'

    dict es:  
        dict_ciclos_sep = {ciclo: {'Ch': df_ciclo_ch, 'Dis': df_ciclo_dis}} 
        Uso: ciclos_sep[100]['Ch'] te da el df de carga del ciclo 100
    '''
    x = 'Time'
    y = 'CellV'

    indices_ciclos_totales = sorted(dict.keys())
     
    plt.figure(figsize=(10,4))
    # paleta completa (uno por cada ciclo real)
    colors = cm.viridis(np.linspace(0, 1, len(indices_ciclos_totales)))
    # map: ciclo_real -> color_correcto
    color_map = {c: colors[i] for i, c in enumerate(indices_ciclos_totales)}

    x_ch_acumulado = 0
    x_dis_acumulado = 0
    print(indices_ciclos)
    for i in indices_ciclos:

        color = color_map[i]

        df_ch = dict[i]['Ch']
        df_dis = dict[i]['Dis']

        x_ch = df_ch[x].values + x_ch_acumulado
        y_ch = df_ch[y].values
        x_dis = df_dis[x].values + x_dis_acumulado
        y_dis = df_dis[y].values

        x_ch_acumulado += np.max(df_dis[x].values)
        x_dis_acumulado += np.max(df_dis[x].values)

        
        # ------- Charge -------
        plt.plot(x_ch, y_ch, marker='o', linestyle='-',color=color, markersize=0.1, label=f'Ciclo {i}')
        # ------- Discharge -------
        plt.plot(x_dis, y_dis, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')

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
    
    #plt.ylim(-0.0025,0.0025) # para dV/dQ
    #plt.ylim(0,0.002) # para dV/dQ charge
    #plt.ylim(-0.002,0) # para dV/dQ discharge
    #plt.xlim(0,3000)
    plt.ylim(2.9,4.5)
    #plt.xlim(-60,2650)
    
    plt.xlabel(f'{x_label}', fontsize=16)
    plt.ylabel(f'{y_label}', fontsize=16)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)

    plt.title(f'{y} vs {x}', fontsize=12)
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(f'../output/{nombre_grafico}_{y_string}vs{x_string}.png', dpi=300)
    plt.show()
    return


def plot_n_cycles_tvsV(indices_ciclos, dict, nombre_grafico='plot', scatter=False):
    '''
    x,y = 'Time', 'CellV'

    dict es:  
        dict_ciclos_sep = {ciclo: {'Ch': df_ciclo_ch, 'Dis': df_ciclo_dis}} 
        Uso: ciclos_sep[100]['Ch'] te da el df de carga del ciclo 100
    '''
    x = 'Time'
    y = 'CellV'

    indices_ciclos_totales = sorted(dict.keys())
     
    plt.figure(figsize=(10,4))
    colors = cm.viridis(np.linspace(0, 1, len(indices_ciclos_totales))) # paleta completa (uno por cada ciclo real)
    color_map = {c: colors[i] for i, c in enumerate(indices_ciclos_totales)} # map: ciclo_real -> color_correcto

    print(indices_ciclos)
    for i in indices_ciclos:
        color = color_map[i]
        df_ch = dict[i]['Ch']
        df_dis = dict[i]['Dis']

        x_ch = df_ch[x].values
        y_ch = df_ch[y].values
        x_dis = df_dis[x].values
        y_dis = df_dis[y].values
        
        # ------- Charge -------
        plt.plot(x_ch, y_ch, marker='o', linestyle='-',color=color, markersize=0.1, label=f'Ciclo {i}')
        # ------- Discharge -------
        plt.plot(x_dis, y_dis, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')

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
    
    #plt.ylim(-0.0025,0.0025) # para dV/dQ
    #plt.ylim(0,0.002) # para dV/dQ charge
    #plt.ylim(-0.002,0) # para dV/dQ discharge
    #plt.xlim(0,3000)
    plt.ylim(2.9,4.5)
    #plt.xlim(-60,2650)
    
    plt.xlabel(f'{x_label}', fontsize=16)
    plt.ylabel(f'{y_label}', fontsize=16)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)

    plt.title(f'{y} vs {x}', fontsize=12)
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(f'../output/{nombre_grafico}_{y_string}vs{x_string}.png', dpi=300)
    plt.show()
    return


def plot_n_cycles_Vvst(indices_ciclos, dict, nombre_grafico='plot', scatter=False):
    '''
    x,y = 'CellV', 'Time'

    dict es:  
        dict_ciclos_sep = {ciclo: {'Ch': df_ciclo_ch, 'Dis': df_ciclo_dis}} 
        Uso: ciclos_sep[100]['Ch'] te da el df de carga del ciclo 100
    '''
    x = 'CellV'
    y = 'Time'

    indices_ciclos_totales = sorted(dict.keys())
     
    plt.figure(figsize=(10,4))
    colors = cm.viridis(np.linspace(0, 1, len(indices_ciclos_totales))) # paleta completa (uno por cada ciclo real)
    color_map = {c: colors[i] for i, c in enumerate(indices_ciclos_totales)} # map: ciclo_real -> color_correcto

    print(indices_ciclos)
    for i in indices_ciclos:
        color = color_map[i]
        df_ch = dict[i]['Ch']
        df_dis = dict[i]['Dis']

        x_ch = df_ch[x].values
        y_ch = df_ch[y].values
        x_dis = df_dis[x].values
        y_dis = df_dis[y].values
        
        # ------- Charge -------
        plt.plot(x_ch, y_ch, marker='o', linestyle='-',color=color, markersize=0.1, label=f'Ciclo {i}')
        # ------- Discharge -------
        plt.plot(x_dis, y_dis, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')

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
    
    #plt.ylim(-0.0025,0.0025) # para dV/dQ
    #plt.ylim(0,0.002) # para dV/dQ charge
    #plt.ylim(-0.002,0) # para dV/dQ discharge
    #plt.xlim(0,3000)
    #plt.ylim(2.9,4.5)
    #plt.xlim(-60,2650)
    
    plt.xlabel(f'{x_label}', fontsize=16)
    plt.ylabel(f'{y_label}', fontsize=16)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)

    plt.title(f'{y} vs {x}', fontsize=12)
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(f'../output/{nombre_grafico}_{y_string}vs{x_string}.png', dpi=300)
    plt.show()
    return





def plot_n_cycles(indices_ciclos, dict, x, y, nombre_grafico='plot', scatter=False):
    '''
    x,y = 'Time', 'CellV', 'dCapacity/dCellV', 'dCellV/dCapacity' 'Q'

    dict es:  
        dict_ciclos_sep = {ciclo: {'Ch': df_ciclo_ch, 'Dis': df_ciclo_dis}} 
        Uso: ciclos_sep[100]['Ch'] te da el df de carga del ciclo 100
    '''

    plt.figure(figsize=(8,5))
    #plt.rcParams.update({'font.size': 12})
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
            '''
            # ------- Charge -------
            if x == 'CellV' and y == 'dCellV/dCapacity':
                # -- para 1/dVdQ = dQdV vs CellV
                plt.plot(x_ch, 1/y_ch, marker='o', linestyle='-',color=color, markersize=0.1, label=f'Ciclo {i}')
            else:
                plt.plot(x_ch, y_ch, marker='o', linestyle='-',color=color, markersize=0.1, label=f'Ciclo {i}')
            '''
            # ------- Discharge -------
            if x == 'Time':
                # -- para cellV vs Time
                plt.plot(x_dis-np.max(x_ch), y_dis, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
            if x == 'Q':
                # -- para Q vs cellV
                # -- para Q vs dVdQ
                plt.plot(x_dis-np.min(x_dis), y_dis, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
            if y == 'Q':
                # -- para CellV vs Q
                plt.plot(x_dis, y_dis-np.min(y_dis), marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
            if x == 'CellV' and y == 'dCellV/dCapacity':
                # -- para 1/dVdQ = dQdV vs CellV
                plt.plot(x_dis, 1/y_dis, marker='o', linestyle='-',color=color,markersize=0.1)#, label=f'Ciclo {i}')
            else:
                plt.plot(x_dis, y_dis, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')

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
    
    #plt.ylim(-0.0025,0.0025) # para dV/dQ
    #plt.ylim(0,0.002) # para dV/dQ charge
    #plt.ylim(-0.002,0) # para dV/dQ discharge
    #plt.xlim(0,3000)
    #plt.ylim(2.9,4.5)
    #plt.xlim(-60,2650)
    
    plt.xlabel(f'{x_label}', fontsize=16)
    plt.ylabel(f'{y_label}', fontsize=16)
    # ticks
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(fontsize=12)

    plt.title(f'{y} vs {x}', fontsize=12)
    plt.grid(True)
    
    #plt.legend()
    plt.tight_layout()
    plt.savefig(f'../output/{nombre_grafico}_{y_string}vs{x_string}.png', dpi=300)
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
    #plt.tight_layout()
    fig.savefig(f'../output/{nombre_grafico}_{y_string}vs{x_string}.png', dpi=300)
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

