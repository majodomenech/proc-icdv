import pandas as pd
import os
import numpy as np
import re
from csaps import csaps
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import seaborn as sns

plt.rcParams.update({
    'font.size': 14,
    'axes.labelsize': 16,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 12,
    'axes.titlesize': 18,
    'lines.linewidth': 2.5,
})

class arbin_data:
    def __init__(self, xls_file, masa=None):
        """
        Inicializa el objeto leyendo el archivo Excel y obteniendo la masa del electrodo.
        
        Parámetros:
        -----------
        xls_file : str
            Ruta al archivo Excel con los datos.
        masa : float o None
            Masa del electrodo. Si None, se extrae del archivo.
        """
        self.xls_file = pd.ExcelFile(xls_file)
        self.nombres_hojas = self.xls_file.sheet_names
        if not isinstance(masa, float):
            self.masa = self.xls_file.parse(self.nombres_hojas[0]).iloc[3, 4]
            self.masa = float(re.findall(r'\d+\.\d+|\d+', self.masa)[0])
        else:
            self.masa = masa

    def parse_xls(self, name, i_column, f_column):
        """
        Lee y concatena hojas del archivo Excel que contienen `name` en el título,
        seleccionando las columnas indicadas. Renombra columnas y normaliza capacidad por masa.
        
        Parámetros:
        -----------
        name : str
            Substring para filtrar hojas a leer.
        i_column, f_column : int
            Índices de columnas inicial y final a extraer.
        
        Retorna:
        --------
        pd.DataFrame
            Datos concatenados y procesados.
        """
        channel = [nombre for nombre in self.nombres_hojas if name in nombre]
        df = pd.DataFrame()

        for sheet in channel:
            df_t = self.xls_file.parse(sheet)
            df_t = df_t[df_t.columns[i_column:f_column+1]]
            df = pd.concat([df, df_t])

        names = {'Charge_Capacity(Ah)': 'deinsertion', 'Discharge_Capacity(Ah)': 'insertion'}
        df.rename(columns=names, inplace=True)
        df['insertion'] = df['insertion'] * 1e6 / self.masa
        df['deinsertion'] = df['deinsertion'] * 1e6 / self.masa

        if 'insertion' in df.columns and 'Voltage(V)' in df.columns:
            df = df.sort_values(by=['Cycle_Index', 'Step_Index'])

        return df

    @property
    def final_cap_data(self):
        """
        Propiedad que carga y calcula la eficiencia a partir de datos estadísticos.
        
        Retorna:
        --------
        pd.DataFrame
            Datos con columnas 'insertion', 'deinsertion' y 'Efficiency'.
        """
        if not hasattr(self, '_final_cap_data'):
            df = self.parse_xls('Statistics', 5, 6)
            df['Efficiency'] = df['insertion'].shift(-1) / df['deinsertion'] * 100
            self._final_cap_data = df
        return self._final_cap_data

    def cicle_cap(self):
        """
        Carga los datos de ciclados para análisis posteriores.
        """
        self.data_ciclado = self.parse_xls('Channel', 3, 9)

    def _parse_ciclos(self, ciclos):
        """
        Normaliza el input ciclos a lista de enteros.
        
        Parámetros:
        -----------
        ciclos : int o list[int]
        
        Retorna:
        --------
        list[int]
        """
        if isinstance(ciclos, int):
            return [ciclos]
        elif isinstance(ciclos, list):
            return ciclos
        else:
            raise ValueError("El parámetro 'ciclos' debe ser un entero o una lista de enteros.")

    def get_ciclado(self, data, ciclo):
        """
        Extrae curvas de carga (insertion) y descarga (deinsertion) para un ciclo dado.
        
        Parámetros:
        -----------
        data : pd.DataFrame
            Datos ciclados.
        ciclo : int
            Número de ciclo.
        
        Retorna:
        --------
        tuple: ((insertion_cap, insertion_volt), (deinsertion_cap, deinsertion_volt))
        """
        data_c = data[data['Cycle_Index'] == ciclo]

        mask1 = ~data_c.duplicated(subset='insertion', keep=False)
        ql = data_c[mask1]['insertion'].tolist()
        vl = data_c[mask1]['Voltage(V)'].tolist()

        mask2 = ~data_c.duplicated(subset='deinsertion', keep=False)
        qdl = data_c[mask2]['deinsertion'].tolist()
        vdl = data_c[mask2]['Voltage(V)'].tolist()

        return (ql, vl), (qdl, vdl)

    def final_cap_plot(self, ax=None, plt_kws=None, max_cy_number=None, max_cap=None, loc=None, max_eff=None):
        """
        Grafica capacidad de inserción y eficiencia vs número de ciclo.
        
        Parámetros:
        -----------
        ax : matplotlib.axes.Axes o None
            Eje donde graficar. Si None, crea uno nuevo.
        plt_kws : dict o None
            Parámetros para personalizar el plot.
        
        Retorna:
        --------
        tuple(matplotlib.axes.Axes, matplotlib.axes.Axes)
            Ejes de la figura (primario y secundario).
        """
        ax = plt.gca() if ax is None else ax
        plt_kws = {} if plt_kws is None else plt_kws

        cap = self.final_cap_data
        cycles = range(1, len(cap['deinsertion']) + 1)

        ax.plot(cycles, cap['deinsertion'], marker='o', label='Deinsertion Capacity', color="#14BDF0", **plt_kws)
        ax.plot(cycles, cap['insertion'], marker='o', label='Insertion Capacity', color="#1DC097F8", **plt_kws)
        ax.set_xlabel("Cycle Number")
        ax.set_ylabel(r"Capacity [mAh$g^{-1}$]", color='#1DC097F8')
        ax.tick_params(axis='y', labelcolor='#1DC097F8')
        #ax.set_xlim(cycles[0], cycles[-1])

        if max_cy_number:
            ax.set_xlim(cycles[0], max_cy_number)
        else:
            ax.set_xlim(cycles[0], cycles[-1])

        if max_cap:
            ax.set_ylim(bottom=0, top=max_cap)

        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        if not loc:
            ax.legend(loc='upper right')
        else:
            ax.legend(loc=loc)

        cycles2 = range(2, len(cap['Efficiency']) + 2)

        ax2 = ax.twinx()
        ax2.plot(cycles2, cap['Efficiency'], marker='o', label='Efficiency', color="#CA7BF8", **plt_kws)
        ax2.set_ylabel("Efficiency [%]", color='#CA7BF8')
        #ax2.set_ylim(min(80, np.min(cap['Efficiency'])), max(np.max(cap['Efficiency']), 100))
        #ax2.set_xlim(cycles[0], cycles[-1])
        ax2.tick_params(axis='y', labelcolor='#CA7BF8')

        if max_cy_number:
            ax2.set_xlim(cycles2[0], max_cy_number)
        else:
            ax2.set_xlim(cycles2[0], cycles2[-1])

        if max_eff: #para setar un maximo en el eje de eficiencia
            ax2.set_ylim(0, max_eff)

        return ax, ax2

    def capacity_lost_plot(self, ax=None, plt_kws=None, max_cy_number=None, max_cap_loss=None):
        """
        Grafica el porcentaje de pérdida de capacidad respecto al ciclo anterior.# NO! CREO QUE ES RESPECTO AL PRIMER CICLO (respecto al valor de deinsertion[0])
        
        Parámetros:
        -----------
        ax : matplotlib.axes.Axes o None
        plt_kws : dict o None
        max_cy_number : int o None
        max_cap_loss : float o None
        Retorna:
        --------
        matplotlib.axes.Axes
        """
        ax = plt.gca() if ax is None else ax
        plt_kws = {} if plt_kws is None else plt_kws

        cap = self.final_cap_data
        deinsertion = cap['deinsertion'].values
        lost = np.zeros_like(deinsertion)
        lost[1:] = (1 - deinsertion[1:] / deinsertion[3]) * 100 #ojo volver esto a cero!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1

        ax.plot(range(2, len(lost) + 1), lost[1:], marker='o', color='#C20078', label='Capacity Loss (%)', **plt_kws)
        ax.set_xlabel("Cycle Number")
        ax.set_ylabel("Capacity Loss [%]")
        #ax.set_xlim(2, len(lost) + 1)
        if max_cy_number:
            ax.set_xlim(2, max_cy_number)
        else:
            ax.set_xlim(2, len(lost) + 1)
        if max_cap_loss:
            ax.set_ylim(0, max_cap_loss)
        ax.grid(True)
        ax.legend()

        return ax

    def dqdv_heatmap(self, raleo=5, alpha=6, vmax=None, cmap='viridis', ax=None, volt_max=None, plt_kws=None):
        """
        Muestra un mapa de calor de dQ/dV normalizado a lo largo de los ciclos.
        
        Parámetros:
        -----------
        raleo : int
            Factor de muestreo para suavizar datos.
        alpha : float
            Parámetro de suavizado para la interpolación.
        vmax : float o None
            Valor máximo para la escala de color.
        cmap : str
            Colormap a usar.
        ax : matplotlib.axes.Axes o None
            Eje donde graficar.
        volt_max : float o None
            Valor máximo de potencial a mostrar.
        plt_kws : dict o None
            Parámetros extra para imshow (opcional).
        
        Retorna:
        --------
        matplotlib.axes.Axes
        """
        ax = plt.gca() if ax is None else ax
        plt_kws = {} if plt_kws is None else plt_kws

        if not hasattr(self, 'data_ciclado'):
            self.cicle_cap()

        data = self.data_ciclado
        ciclos = sorted(data['Cycle_Index'].unique())
        alpha = 0.99999 + alpha * 1e-6

        voltajes = np.linspace(0, 1.0, 5000)
        matriz = []

        for ciclo in ciclos:
            df_ciclo = data[data['Cycle_Index'] == ciclo]
            try:
                _, dq = self._procesar_curva(df_ciclo, 'insertion', raleo, alpha)
            except:
                dq = np.zeros_like(voltajes)
            matriz.append(dq)

        matriz = np.array(matriz)
        max_abs = np.abs(matriz).max()
        matriz /= max_abs if max_abs != 0 else 1

        if volt_max is None:
            volt_max = voltajes.max()

        im = ax.imshow(
            matriz,
            aspect='auto',
            extent=[voltajes.min(), volt_max, ciclos[-1]+1, ciclos[0]-1],
            cmap=cmap,
            vmax=vmax,
            **plt_kws
        )
        ax.set_xlabel('Potential / V')
        ax.set_ylabel('Cycle Index')
        ax.set_title('dQ/dV Heatmap (normalized)')
        plt.colorbar(im, ax=ax, label=r'dQ/dV (normalized)')

        return ax

    def cicle_cap_plot(self, ciclos=1, ax=None, plt_kws=None, max_potential=None, max_cap=None):
        """
        Grafica curvas capacidad vs potencial para los ciclos indicados.
        
        Parámetros:
        -----------
        ciclos : int o list[int]
            Ciclos a graficar.
        ax : matplotlib.axes.Axes o None
            Eje donde graficar.
        plt_kws : dict o None
            Parámetros extra para plot.
        
        Retorna:
        --------
        matplotlib.axes.Axes
        """
        ax = plt.gca() if ax is None else ax
        plt_kws = {} if plt_kws is None else plt_kws

        if not hasattr(self, 'data_ciclado'):
            self.cicle_cap()
        data = self.data_ciclado

        ciclos_list = self._parse_ciclos(ciclos)
        colores = sns.color_palette("husl", n_colors=len(ciclos_list))

        for ciclo, color in zip(ciclos_list, colores):
            resultado = self.get_ciclado(data, ciclo)
            ax.plot(resultado[0][0], resultado[0][1], label=f'Ciclo {ciclo}', color=color, **plt_kws)
            ax.plot(resultado[1][0], resultado[1][1], color=color, **plt_kws)

        ax.set_xlabel(r'Capacity [mAh$g^{-1}$]')
        ax.set_ylabel('Potential [V]')
        if max_cap is not None:
            ax.set_xlim(0, max_cap)
        if max_potential is not None:
            ax.set_ylim(0, max_potential)        
        ax.legend()
        ax.grid(True)

        return ax

    def _procesar_curva(self, data, columna_q, raleo, alpha):
        """
        Procesa una curva capacidad vs voltaje para calcular dQ/dV suavizado.
        
        Parámetros:
        -----------
        data : pd.DataFrame
            Datos ciclados.
        columna_q : str
            Columna a analizar ('insertion' o 'deinsertion').
        raleo : int
            Factor de muestreo para reducir puntos.
        alpha : float
            Parámetro de suavizado para interpolación.
        
        Retorna:
        --------
        tuple (v_sample, dq_dv)
            Voltajes muestreados y derivada dQ/dV.
        """
        df = data.copy()
        mask = ~df.duplicated(subset=columna_q, keep=False)
        df2 = df[mask][['Voltage(V)', columna_q]].dropna().sort_values('Voltage(V)')

        v = df2['Voltage(V)'].values[-1::-raleo][::-1]
        q = df2[columna_q].values[-1::-raleo][::-1]
        v, i_u = np.unique(v, return_index=True)
        q = q[i_u]

        v_sample = np.linspace(v.min(), v.max(), 5000)
        q_interp = csaps(v, q, v_sample, smooth=alpha)
        dq_dv = np.gradient(q_interp, v_sample)

        return v_sample, dq_dv

    def get_dqdv(self, data, ciclo, raleo, alpha):
        """
        Obtiene curvas dQ/dV para carga y descarga en un ciclo dado.
        
        Parámetros:
        -----------
        data : pd.DataFrame
            Datos ciclados.
        ciclo : int
            Número de ciclo.
        raleo : int
            Factor de muestreo.
        alpha : float
            Parámetro de suavizado.
        
        Retorna:
        --------
        tuple: ((voltajes_carga, dqdv_carga), (voltajes_descarga, dqdv_descarga))
        """
        df_ciclo = self.data_ciclado[self.data_ciclado['Cycle_Index'] == ciclo]
        try:
            vl_sample, dqdvl = self._procesar_curva(df_ciclo, 'insertion', raleo, alpha)
        except:
            vl_sample, dqdvl = np.nan, np.nan
        try:
            vdl_sample, dqdvdl = self._procesar_curva(df_ciclo, 'deinsertion', raleo, alpha)
        except:
            vdl_sample, dqdvdl = np.nan, np.nan
        return (vl_sample, dqdvl), (vdl_sample, dqdvdl)

    def dqdv_plot(self, ciclos=1, raleo=5, alpha=6, ax=None, plt_kws=None, max_plot=1.0):
        """
        Grafica curvas dQ/dV para carga y descarga de uno o varios ciclos.
        
        Parámetros:
        -----------
        ciclos : int o list[int]
            Ciclos a graficar.
        raleo : int
            Factor de muestreo para suavizado.
        alpha : float
            Parámetro de suavizado.
        ax : matplotlib.axes.Axes o None
            Eje para graficar.
        plt_kws : dict o None
            Parámetros extra para plot.
        max_plot : float
            Límite máximo en eje x (voltaje).
        
        Retorna:
        --------
        matplotlib.axes.Axes
        """
        ax = plt.gca() if ax is None else ax
        plt_kws = {} if plt_kws is None else plt_kws

        alpha = 0.99999 + alpha * 1e-6

        if not hasattr(self, 'data_ciclado'):
            self.cicle_cap()
        data = self.data_ciclado

        ciclos_list = self._parse_ciclos(ciclos)
        colores = sns.color_palette("husl", n_colors=len(ciclos_list))

        for ciclo, color in zip(ciclos_list, colores):
            resultado = self.get_dqdv(data, ciclo, raleo, alpha)
            ax.plot(resultado[0][0], resultado[0][1], label=f'Ciclo {ciclo}', color=color, **plt_kws)
            ax.plot(resultado[1][0], resultado[1][1], color=color, **plt_kws)

        ax.set_xlabel("Potential [V]")
        ax.set_ylabel(r'dQ/dV [mAh$g^{-1}$V$^{-1}$]')
        ax.set_xlim(-0.2, max_plot)
        ax.legend()
        ax.grid(True)

        return ax



def plot_multi_final_cap(datasets, labels=None, ax=None, plt_kws=None):
    """
    Grafica la capacidad de inserción y eficiencia de múltiples datasets.

    Parameters
    ----------
    datasets : list of arbin_data
        Lista de objetos arbin_data.
    labels : list of str, optional
        Lista de etiquetas para cada dataset.
    ax : matplotlib.axes._subplots.AxesSubplot, optional
        Eje donde dibujar la capacidad. Se crea uno nuevo si es None.
    plt_kws : dict, optional
        Diccionario de argumentos extra para plot.
    """
    ax = plt.gca() if ax is None else ax
    plt_kws = {} if plt_kws is None else plt_kws
    labels = labels if labels else [f"Dataset {i+1}" for i in range(len(datasets))]

    ax2 = ax.twinx()
    color_idx = 0
    colores = sns.color_palette("husl", n_colors=len(datasets))

    for data, label in zip(datasets, labels):
        cap = data.final_cap_data
        cycles = range(1, len(cap['deinsertion']) + 1)
        cycles2 = range(2, len(cap['Efficiency']) + 2)
        color = colores[color_idx % len(colores)]

        ax.plot(cycles, cap['deinsertion'], marker='o', label=f'{label} Deinsertion', color=color, **plt_kws)
        ax2.plot(cycles2, cap['Efficiency'], marker='o', label=f'{label} Efficiency', linestyle='--', color=color, **plt_kws)

        color_idx += 1

    ax.set_xlabel("Cycle Number")
    ax.set_ylabel(r"Capacity [mAh$g^{-1}$]")
    ax2.set_ylabel("Efficiency [%]")
    ax2.set_ylim(min(80, np.min(cap['Efficiency'])), 105)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(True)

    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines + lines2, labels + labels2)
    #ax.legend(loc='center right')

    return ax


def plot_multi_capacity_loss(datasets, labels=None, ax=None, plt_kws=None):
    """
    Grafica la pérdida de capacidad entre ciclos para múltiples datasets.
    """
    ax = plt.gca() if ax is None else ax
    plt_kws = {} if plt_kws is None else plt_kws
    labels = labels if labels else [f"Dataset {i+1}" for i in range(len(datasets))]

    for data, label in zip(datasets, labels):
        cap = data.final_cap_data
        deinsertion = cap['deinsertion'].values
        lost = np.zeros_like(deinsertion)
        lost[1:] = (1 - deinsertion[1:] / deinsertion[0]) * 100
        ax.plot(range(2, len(lost) + 1), lost[1:], marker='o', label=f'{label} Loss', **plt_kws)

    ax.set_xlabel("Cycle Number")
    ax.set_ylabel("Capacity Loss [%]")
    ax.grid(True)
    ax.legend()

    return ax


def plot_multi_dqdv(datasets, ciclos=1, labels=None, raleo=5, alpha=6, ax=None, plt_kws=None, max_plot=1.0):
    """
    Grafica dQ/dV para varios datasets en un mismo eje.

    Parameters
    ----------
    datasets : list of arbin_data
        Lista de objetos arbin_data.
    ciclos : int o list
        Ciclo(s) a graficar.
    labels : list of str, optional
        Etiquetas para los datasets.
    raleo : int
        Factor de reducción de puntos.
    alpha : int
        Factor de suavizado (ajustado internamente como 0.99999 + alpha * 1e-6).
    ax : matplotlib.axes._subplots.AxesSubplot, optional
        Eje sobre el que graficar.
    plt_kws : dict, optional
        Diccionario de argumentos extra para plot.
    max_plot : float
        Máximo voltaje para eje x.
    """
    ax = plt.gca() if ax is None else ax
    plt_kws = {} if plt_kws is None else plt_kws
    labels = labels if labels else [f"Dataset {i+1}" for i in range(len(datasets))]
    alpha = 0.99999 + alpha * 1e-6

    color_idx = 0
    total_curvas = sum(len(data._parse_ciclos(ciclos)) for data in datasets)
    colores = sns.color_palette("husl", n_colors=total_curvas)

    for data, label in zip(datasets, labels):
        if not hasattr(data, 'data_ciclado'):
            data.cicle_cap()

        ciclos_list = data._parse_ciclos(ciclos)
        for ciclo in ciclos_list:
            (vl_sample, dqdvl), (vdl_sample, dqdvdl) = data.get_dqdv(data.data_ciclado, ciclo, raleo, alpha)
            color = colores[color_idx % len(colores)]
            ax.plot(vl_sample, dqdvl, label=f'{label} Ciclo {ciclo}', color=color, **plt_kws)
            ax.plot(vdl_sample, dqdvdl, color=color, **plt_kws)
            color_idx += 1

    ax.set_xlabel("Potential [V]")
    ax.set_ylabel(r'dQ/dV [mAh$g^{-1}$V$^{-1}$]')
    ax.set_xlim(0, max_plot)
    ax.grid(True)
    ax.legend()

    return ax

