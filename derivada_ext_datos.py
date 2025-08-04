




# Plot derivada con filtro

windowlength = 153  # Longitud de la ventana del filtro
polyorder = 3 # Orden del polinomio del filtro

def extend_and_smooth(y, window_length, polyorder):
    '''
    Extiendo datos para evitar artefacto del borde del suavizado
    '''
    factor = 2
    n = factor * (window_length - 1) // 2  # cantidad extendida (mitad de un wl)
    y_ext = np.concatenate([np.full(n, y[0]), y, np.full(n, y[-1])])
    y_smooth_ext = savgol_filter(y_ext, window_length=window_length, polyorder=polyorder)
    return y_smooth_ext[n:-n]

# Graficar dQ/dV calculado
plt.figure(figsize=(8,5))
colors = cm.viridis(np.linspace(0, 1, len(indices_ciclos)))

factor = 2
n = factor * (windowlength - 1) // 2  # cantidad extendida (mitad de un wl)

for i, color in zip(indices_ciclos, colors):
    df_ch = dict_ciclos_sep[i]['Ch']
    df_dis = dict_ciclos_sep[i]['Dis']

    Q_ch = df_ch['Q'].values
    V_ch = df_ch['CellV'].values
    Q_dis = df_dis['Q'].values
    V_dis = df_dis['CellV'].values

    # Extensión en Q: constante en los bordes
    Q_ch_ext = np.concatenate([np.full(n, Q_ch[0]), Q_ch, np.full(n, Q_ch[-1])])

    # Extensión en voltaje
    dV_mean = np.mean(np.diff(V_ch)) # Promedio del paso de voltaje
    V_start = V_ch[0] - dV_mean * np.arange(n, 0, -1)
    V_end = V_ch[-1] + dV_mean * np.arange(1, n + 1)
    V_ch_ext = np.concatenate([V_start, V_ch, V_end])
    
    print(n)
    #print(Q_ch_ext.shape)
    #print(Q_ch.shape)


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

    plt.plot(V_ch_ext,Q_ch_ext, marker='o', linestyle='-',color='red',markersize=0.1)
    plt.plot(V_ch,Q_ch, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')

    #plt.plot(V_dis_savgol,Q_dis_savgol-Q_dis_min, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
    
    dqdv_dis_calc = np.gradient(Q_dis_savgol, V_dis_savgol)
    dqdv_dis = dqdv_dis_calc

    #plt.plot(V_ch, dqdv_ch, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
    #plt.plot(V_dis, dqdv_dis, marker='o', linestyle='-',color=color,markersize=0.1, label=f'Ciclo {i}')
    
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