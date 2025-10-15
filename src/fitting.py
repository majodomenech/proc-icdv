
from scipy.special import erfc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.optimize import curve_fit


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

# --- plots ---
def plot_emg_guess(df_ciclo, param_list, x_range=(3.3,4.45), n_points=500):
    
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
        plt.close()
    else:
        plt.show()


# --- fiteos ---
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



def fitloop_emg_lamfijo(diccio, ciclos, p_ini_emg, bounds_emg, ciclos_grafico=None):
    """
    Ajuste encadenado de varios ciclos. Primer ciclo ajusta lambda,
    ciclos siguientes mantienen lambda fijo.
    Devuelve resultados y covs.
    """
    resultados = []
    covs = []
    colores = cm.tab10.colors
    p0_actual = p_ini_emg

    # Ajuste primer ciclo (lambda variable)
    df_ch = diccio[ciclos[0]]['Ch']
    print(f'Ajustando ciclo {ciclos[0]}...')
    popt, pcov = fit_emg_ciclo(df_ch, p0_actual, bounds_emg)
    resultados.append(popt)
    covs.append(pcov)

    # Extraer lambdas para ciclos siguientes
    lambdas_fijo = [popt[i] for i in range(len(popt)) if (i+1) % 4 == 0]
    # Actualizar p0 sin lambdas
    p0_actual = [popt[i] for i in range(len(popt)) if (i+1) % 4 != 0]

    # Graficar primer ciclo si corresponde
    if ciclos_grafico and ciclos[0] in ciclos_grafico:
        plot_emg_fit(df_ch, popt, nombre_ciclo=ciclos[0],
                     save_path=f'./output/ajuste_picos_ciclo{ciclos[0]}.png')

    # Ajuste ciclos restantes
    for ciclo in ciclos[1:]:
        df_ch = diccio[ciclo]['Ch']
        print(f'Ajustando ciclo {ciclo}...')
        popt_completo, pcov_completo = fit_emg_ciclo_lamfijo(df_ch, p0_actual, lambdas_fijo, bounds_emg)
        resultados.append(popt_completo)
        covs.append(pcov_completo)
        p0_actual = [popt_completo[i] for i in range(len(popt_completo)) if (i+1) % 4 != 0]

        if ciclos_grafico and ciclo in ciclos_grafico:
            plot_emg_fit(df_ch, popt_completo, nombre_ciclo=ciclo,
                         save_path=f'./output/ajuste_picos_ciclo{ciclo}.png')

    return resultados, covs