from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm


'''
Funciones para estudiar cosas particulares de las curvas como la resolución, etc

'''


# ----------- ESTUDIO RESOLUCION --------------------------------------
def resolucion_V(indices_ciclos,dict_ciclos_sep):
    '''
    estudio resolucion datos de voltaje y tamaño ventana de suavizado
    output: histograma de los puntos por ventana

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
    output: histograma de los puntos por ventana
    
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