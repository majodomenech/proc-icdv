
from scipy.special import erfc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
from scipy.optimize import curve_fit
import pandas as pd
from pathlib import Path


'''
Funciones para realizar ajustes.

'''

# ============== Funciones de ajuste ==============

# Exponentially Modified Gaussian (EMG)

def emg(x, a, mu, sigma, lambd):
    """
    Exponentially Modified Gaussian (EMG)
    
    x: array de valores
    a: amplitud
    mu: media de la gaussiana
    sigma: desviación estándar
    lambd: parámetro de decaimiento exponencial (1/tau)
    """
    return (a * (lambd/2) *
            np.exp((lambd/2)*(2*mu + lambd*sigma**2 - 2*x)) *
            erfc((mu + lambd*sigma**2 - x) / (np.sqrt(2)*sigma)))


def multi_emg(x, *params):
    """
    params: [a1, mu1, sigma1, lambda1, a2, mu2, sigma2, lambda2, ...]
    """
    y = np.zeros_like(x)
    for i in range(0, len(params), 4):
        a, mu, sigma, lambd = params[i:i+4]
        y += (a * (lambd/2) *
              np.exp((lambd/2)*(2*mu + lambd*sigma**2 - 2*x)) *
              erfc((mu + lambd*sigma**2 - x) / (np.sqrt(2)*sigma)))
    return y


def multi_emg_lamfijo(V, *params, lambdas_fijo):
    y = 0
    n_peaks = len(params)//3
    for i in range(n_peaks):
        a, mu, sigma = params[3*i:3*i+3]
        y += emg(V, a, mu, sigma, lambdas_fijo[i])
    return y

# ============== Funciones de uso ==============

# --- guardado de datos ---
def guardar_parametros_emg(resultados, ciclos, nombre, output_dir="../output"):
    """
    Crea un DataFrame con los parámetros ajustados de los ciclos y lo guarda como CSV.
    
    Parámetros
    ----------
    resultados : list
        Lista (o array) con los parámetros ajustados por ciclo, 
        donde cada elemento corresponde a un ciclo.
    ciclos : list
        Lista con los números de ciclo correspondientes a los resultados.
    nombre : str
        Nombre base del archivo CSV de salida.
    output_dir : str o Path
        Carpeta donde guardar el archivo. Por defecto "../output".
    """
    n_peaks = len(resultados[0]) // 4

    # Crear nombres de columnas (a, mu, sigma, lambda) por pico
    cols = [f"{param}{i+1}" for i in range(n_peaks) for param in ["a", "mu", "sigma", "lambda"]]

    # Crear DataFrame con los resultados
    df_params = pd.DataFrame(resultados, index=ciclos, columns=cols)

    # Definir ruta de salida
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"parametros_ajustes_{nombre}.csv"

    # Guardar CSV
    df_params.to_csv(output_path)

    print(f"✅ Ajustes terminados. Resultados guardados en '{output_path}'")

    return df_params


# --- plots ---
def plot_emg_guess(df_ciclo, param_list, x_range=(3.3,4.45), n_points=500, legend=True):
    
    """
    Grafica los datos de dQ/dV de un ciclo junto con EMG iniciales para testear el guess,
    mostrando picos individuales y la suma total usando multi_emg.
    
    df_ciclo: DataFrame con columnas 'dqdv_ch_calc' y 'V_ch_savgol'
    param_list: lista de tuplas [(a, mu, sigma, lambd), ...]
    x_range: tupla (min, max) del rango de x para graficar EMG
    n_points: número de puntos de la curva EMG
    """
    V = df_ciclo['V_ch_savgol']
    dqdv = df_ciclo['dqdv_ch_calc']

    x = np.linspace(x_range[0], x_range[1], n_points)
    colors = cm.tab10.colors

    plt.figure(figsize=(7,5))
    plt.plot(V, dqdv, color='black', label='Datos', linewidth=1)

    # Dibujar cada EMG individual
    for i, (a, mu, sigma, lambd) in enumerate(param_list):
        y = emg(x, a, mu, sigma, lambd)
        plt.plot(x, y, '--', label=f"Pico {i+1}: μ={mu}, λ={lambd}", color=colors[i % len(colors)])

    # Dibujar la suma total usando multi_emg
    # Convertir param_list a lista plana
    p_ini_emg = [val for tup in param_list for val in tup]
    y_total = multi_emg(V, *p_ini_emg)
    plt.plot(V, y_total, 'r-', label="Multi EMG")

    plt.xlabel("Voltaje (V)")
    plt.ylabel("dQ/dV (mAh/V)")
    plt.title("EMG iniciales vs datos del ciclo")
    if legend:
        plt.legend()
    plt.grid(True)
    plt.show()


def plot_emg_fit(df_ch, popt, nombre_ciclo=None, ylim=(-300, 8500), save_path=None):
    """
    Grafica datos del ciclo, ajuste total y cada pico individual.
    """
    V = df_ch['V_ch_savgol'].values
    dqdv = df_ch['dqdv_ch_calc'].values
    colors = cm.tab10.colors

    plt.figure(figsize=(7,5))
    plt.plot(V, dqdv, label="Datos", color='black')

    # Curva total
    y_fit = multi_emg(V, *popt)
    plt.plot(V, y_fit, 'r-', label="Ajuste total")

    # Picos individuales
    n_peaks = len(popt)//4
    for i in range(n_peaks):
        a, mu, sigma, lam = popt[4*i:4*i+4]
        plt.plot(V, emg(V, a, mu, sigma, lam), '--', color=colors[i % len(colors)], label=f"Pico {i+1}")

    plt.xlabel("Voltaje (V)")
    plt.ylabel("dQ/dV (mAh/Vg)")
    plt.title(f"Ajuste ciclo {nombre_ciclo}" if nombre_ciclo else "Ajuste EMG")
    plt.ylim(ylim)
    plt.legend()
    plt.grid(True)

    if save_path:
        plt.savefig(save_path, dpi=300)
        plt.show()
        plt.close()
    else:
        plt.show()


def plot_emg_fit_poster(df_ch, popt, nombre_ciclo=None, ylim=(-300, 8500), save_path=None):
    """
    Gráfico para póster científico: muestra los datos experimentales,
    el ajuste total y los picos individuales (EMG).
    """
    # --- Estilo general ---
    mpl.rcParams.update({
        "font.size": 14,
        "axes.labelsize": 16,
        "axes.titlesize": 16,
        "legend.fontsize": 13,
        "xtick.labelsize": 13,
        "ytick.labelsize": 13,
        "axes.linewidth": 1.2,
    })

    V = df_ch['V_ch_savgol'].values
    dqdv = df_ch['dqdv_ch_calc'].values
    colors = cm.tab10.colors

    plt.figure(figsize=(7, 5), dpi=300)
    
    # --- Datos experimentales ---
    plt.plot(V, dqdv, color='black', linewidth=2.2, label="Datos")

    # --- Ajuste total ---
    y_fit = multi_emg(V, *popt)
    plt.plot(V, y_fit, color='crimson', linewidth=2.5, label="Ajuste total")

    # --- Picos individuales ---
    n_peaks = len(popt)//4
    for i in range(n_peaks):
        a, mu, sigma, lam = popt[4*i:4*i+4]
        plt.plot(
            V, emg(V, a, mu, sigma, lam),
            '--', color=colors[i % len(colors)],
            linewidth=1.6, alpha=0.9, label=f"Pico {i+1}"
        )

    plt.xlabel("Voltaje (V)")
    plt.ylabel("dQ/dV (mAh/Vg)")
    if nombre_ciclo:
        plt.title(f"Ciclo {nombre_ciclo}", pad=10)
    plt.ylim(ylim)

    plt.grid(True, alpha=0.3, linewidth=0.8)
    plt.legend(frameon=False, loc='best')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


# --- fiteos ---
def recalcular_bounds(popt, n_peaks, cfg_bounds):
    """
    Recalcula los bounds (límites) de los parámetros de ajuste.

    Parámetros:
    ------------
    popt : list or np.array
        Últimos parámetros ajustados (sin lambdas).
    n_peaks : int
        Número de picos.
    cfg_bounds : dict
        Configuración de bounds, con posibles claves:
            - 'perc_a', 'perc_mu', 'perc_sigma' : floats (porcentajes)
            - 'restricciones_mu' : dict {i: (mu_min, mu_max)}
            - 'min_amp' / 'max_amp' : valores absolutos opcionales
            - etc.

    Retorna:
    ---------
    (lb, ub) : tuple of np.ndarray
        Límite inferior y superior.
    """
    perc_a = cfg_bounds.get('perc_a', 0.1)
    perc_mu = cfg_bounds.get('perc_mu', 0.1)
    perc_sigma = cfg_bounds.get('perc_sigma', 0.1)
    restricciones_mu = cfg_bounds.get('restricciones_mu', None)
    restricciones_sigma = cfg_bounds.get('restricciones_sigma', None)

    lb, ub = [], []

    for i in range(n_peaks):
        a0, mu0, sigma0 = popt[3*i:3*i+3]

        # Límites relativos
        lb_a, ub_a = (1 - perc_a) * a0, (1 + perc_a) * a0
        lb_mu, ub_mu = (1 - perc_mu) * mu0, (1 + perc_mu) * mu0
        lb_s, ub_s = (1 - perc_sigma) * sigma0, (1 + perc_sigma) * sigma0

        # Restricciones opcionales por pico
        if restricciones_mu and i in restricciones_mu:
            mu_min, mu_max = restricciones_mu[i]
            lb_mu = max(lb_mu, mu_min)
            ub_mu = min(ub_mu, mu_max)

        if restricciones_sigma and i in restricciones_sigma:
            s_min, s_max = restricciones_sigma[i]
            lb_s = max(lb_s, s_min)
            ub_s = min(ub_s, s_max)

    lb = np.array(lb, dtype=float)
    ub = np.array(ub, dtype=float)
    lb[~np.isfinite(lb)] = 0
    ub[~np.isfinite(ub)] = 1e6
    return (lb, ub)


def fit_emg_ciclo(df_ch, p0, bounds, maxfev=20000):
    """
    Ajusta un solo ciclo usando multi_emg con lambda variable.
    Devuelve popt y pcov.
    """
    V = df_ch['V_ch_savgol'].values
    dqdv = df_ch['dqdv_ch_calc'].values
    popt, pcov = curve_fit(multi_emg, V, dqdv, p0=p0, bounds=bounds, maxfev=maxfev)
    return popt, pcov


def fit_emg_ciclo_lamfijo(df_ch, p0, lambdas_fijo, bounds, maxfev=20000):
    """
    Ajusta un solo ciclo usando multi_emg_lamfijo (lambdas fijos).
    Devuelve popt completo incluyendo los lambdas.
    """
    V = df_ch['V_ch_savgol'].values
    dqdv = df_ch['dqdv_ch_calc'].values
    
    f = lambda V, *params: multi_emg_lamfijo(V, *params, lambdas_fijo=lambdas_fijo)
    popt, pcov = curve_fit(f, V, dqdv, p0=p0, bounds=bounds, maxfev=maxfev)

    # Construir popt completo
    n_peaks = len(lambdas_fijo)
    popt_completo = []
    for i in range(n_peaks):
        popt_completo.extend(popt[3*i:3*i+3])
        popt_completo.append(lambdas_fijo[i])

    # Ajustar matriz de covarianza para tamaño completo
    pcov_completo = np.full((4*n_peaks, 4*n_peaks), np.nan)
    for i in range(3*n_peaks):
        for j in range(3*n_peaks):
            pcov_completo[i, j] = pcov[i, j]

    return popt_completo, pcov_completo



def fitloop_emg_lamfijo(diccio, ciclos, p_ini_emg, bounds_ini_emg, ciclos_grafico=None, cfg_bounds=None):
    """
    Ajuste encadenado de varios ciclos. Primer ciclo ajusta lambda,
    ciclos siguientes mantienen lambda fijo.
    Devuelve resultados y covs.
    """
    if cfg_bounds is None:
        cfg_bounds = {}

    resultados = []
    covs = []
    colores = cm.tab10.colors
    p0_actual = p_ini_emg
    bounds_actual = bounds_ini_emg
    n_peaks = len(p_ini_emg)//4

    # --- Ajuste primer ciclo (lambda variable) ---
    df_ch = diccio[ciclos[0]]['Ch']
    print(f'Ajustando ciclo {ciclos[0]}...')
    popt, pcov = fit_emg_ciclo(df_ch, p0_actual, bounds_actual)
    resultados.append(popt)
    covs.append(pcov)

    # Extraer lambdas para ciclos siguientes
    lambdas_fijo = [popt[i] for i in range(len(popt)) if (i+1) % 4 == 0]
    popt_sin_lambda = [popt[i] for i in range(len(popt)) if (i+1) % 4 != 0]
    
    # Actualizar p0 sin lambdas
    p0_actual = [popt[i] for i in range(len(popt)) if (i+1) % 4 != 0]

    # Recalcular bounds para el próximo ciclo
    bounds_actual = recalcular_bounds(p0_actual, n_peaks, cfg_bounds)

    # Graficar primer ciclo si corresponde
    if ciclos_grafico and ciclos[0] in ciclos_grafico:
        plot_emg_fit(df_ch, popt, nombre_ciclo=ciclos[0],
                     save_path=f'../output/ajuste_C{ciclos[0]}.png')

    # Ajuste ciclos restantes
    for ciclo in ciclos[1:]:
        try:
            df_ch = diccio[ciclo]['Ch']
            print(f'Ajustando ciclo {ciclo}...')
            popt_completo, pcov_completo = fit_emg_ciclo_lamfijo(df_ch, p0_actual, lambdas_fijo, bounds_actual)
            resultados.append(popt_completo)
            covs.append(pcov_completo)
            p0_actual = [popt_completo[i] for i in range(len(popt_completo)) if (i+1) % 4 != 0] # vuelvo a actualizar p0 sin lambdas

            if ciclos_grafico and ciclo in ciclos_grafico:
                plot_emg_fit(df_ch, popt_completo, nombre_ciclo=ciclo,
                            save_path=f'../output/ajuste_C{ciclo}.png')

            # Recalcular bounds para el próximo ciclo
            bounds_actual = recalcular_bounds(p0_actual, n_peaks, cfg_bounds)

        except Exception as e:
            print(f"⚠️ Ajuste del ciclo {ciclo} fallido: {e}")
            # Agregar NaNs en caso de fallo
            resultados.append([np.nan]*(4*n_peaks))
            covs.append(np.full((4*n_peaks, 4*n_peaks), np.nan))

    return resultados, covs