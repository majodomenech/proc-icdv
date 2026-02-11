import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from scipy.special import wofz

# Función Voigt
def voigt(x, sigma, gamma):
    z = (x + 1j*gamma) / (sigma * np.sqrt(2))
    return np.real(wofz(z)) / (sigma * np.sqrt(2*np.pi))

# Función triple Voigt ajustada con gamma1, gamma2, gamma3 y ratio como parámetros
def triple_voigt(x, cen, amp1, sigma, delta1, delta2, gamma1, gamma2, gamma3, ratio1, ratio2,m,b):
    amp2 = amp1 * ratio1  # Amplitud del segundo pico (Ka2)
    amp3 = amp1 * ratio2  # Amplitud del tercer pico
    fondo= m*x+b
    return (amp1 * voigt(x - cen, sigma, gamma1) +
            amp2 * voigt(x - cen + delta1, sigma, gamma2) +
            amp3 * voigt(x - cen + delta2, sigma, gamma3)+ fondo)



# Lee los datos del archivo
file_path = r"C:\Users\guadi\OneDrive\Escritorio\UNI\5to año\trabajo final\azufre\datos Ka\SKa_3.dat"
data = pd.read_csv(file_path, skiprows=2, delim_whitespace=True)

# Extrae las columnas por índice
motor1 = data.iloc[:, 0]  # Primera columna
cuentas = data.iloc[:, 2]  # Tercera columna

# Parámetros del silicio
d_si = 3.1355  # Espaciado interplanar para Si(111) en Ångstroms

# Valores de referencia para la calibración en energía
motor1_0 = 10  # Posición en pasos de la Ka1
theta_0 = 58.99 # Ángulo de Bragg de la Ka1

# Convierte motor1 a theta (en grados)
theta_bragg = theta_0 - (motor1 - motor1_0) / 200.0

# Convierte theta a longitud de onda usando la ley de Bragg
lambda_m = 2 * d_si * np.sin(np.radians(theta_bragg))

# Convierte longitud de onda a energía en eV
E = 12398.42 / lambda_m

# Define los errores en las cuentas como la raíz cuadrada de las cuentas
sigma_cuentas = np.sqrt(cuentas)
# Maneja posibles valores de sqrt(0) asignando un mínimo error
sigma_cuentas[sigma_cuentas == 0] = 1.0

# Crear un DataFrame con los datos de energía y cuentas medidas
data_output = pd.DataFrame({'Energía (eV)': E, 'Cuentas medidas': cuentas})

# Guardar el archivo con el nombre file_path sin la extensión y agregando '_calib.dat'
output_file = file_path.replace('.dat', '') + '_calib.dat'
data_output.to_csv(output_file, sep='\t', index=False)

print(f"Archivo guardado como: {output_file}")


# Valores iniciales para el ajuste de tres Voigt
# [cen, amp1, sigma, delta1, delta2, gamma1, gamma2, gamma3, ratio1, ratio2]
initial_guess = [2306.64, 500, 2, 1.2, -5.0, 0.325, 0.32, 0.3, 0.5, 0.3,0,0]

# Establece los límites para los parámetros de ajuste
bounds = (
    [2200, 10, 0.1, 1.1, -7, 0.3, 0.3, 0.29, 0.49, 0.2,-1,-np.inf],  # Límites inferiores
    [2400, 100000, 6, 1.3, -3, 0.35, 0.34, 0.32, 0.51, 0.4,1,np.inf]  # Límites superiores
)

# Realiza el ajuste con restricciones y pesos
popt, pcov = curve_fit(
    triple_voigt, E, cuentas, p0=initial_guess, bounds=bounds, sigma=sigma_cuentas, absolute_sigma=True
)

# Genera datos ajustados
E_fit = np.linspace(min(E), max(E), 1000)
cuentas_fit = triple_voigt(E_fit, *popt)

# Calcula las tres funciones Voigt por separado
cen, amp1, sigma, delta1, delta2, gamma1, gamma2, gamma3, ratio1, ratio2 ,m,b= popt
amp2 = amp1 * ratio1
amp3 = amp1 * ratio2
voigt1 = amp1 * voigt(E_fit - cen, sigma, gamma1)
voigt2 = amp2 * voigt(E_fit - cen + delta1, sigma, gamma2)
voigt3 = amp3 * voigt(E_fit - cen + delta2, sigma, gamma3)
fondo= m * E_fit + b

# Calcula la relación de amplitudes
fwhm = 2 * sigma * np.sqrt(2 * np.log(2))

# Calcula las incertidumbres de los parámetros ajustados
perr = np.sqrt(np.diag(pcov))
fwhmerr = 2 * perr[2] * np.sqrt(2 * np.log(2))

# Calcula el chi cuadrado reducido
residuos = cuentas - triple_voigt(E, *popt)
chi2 = np.sum((residuos / sigma_cuentas) ** 2)
chi2_reducido = chi2 / (len(cuentas) - len(popt))

# Preparar los textos a mostrar en el gráfico
param_text = (f"Centro (Ka1): {cen:.2f} ± {perr[0]:.2f} eV\n"
              f"Amplitud 1 (amp1): {amp1:.2f} ± {perr[1]:.2f}\n"
              f"Sigma: {sigma:.2f} ± {perr[2]:.2f}\n"
              f"Resolucion (FWHM): {fwhm:.2f} ± {fwhmerr:.2f} eV\n"
              f"Amplitud 2 (amp2): {amp2:.2f} ± {amp1 * perr[8] / (ratio1**2):.2f}\n"
              f"Amplitud 3 (amp3): {amp3:.2f} ± {amp1 * perr[9] / (ratio2**2):.2f}\n"
              f"Delta Ka1-Ka2: {delta1:.2f} ± {perr[3]:.2f} eV\n"
              f"Delta Ka1-Ka3: {delta2:.2f} ± {perr[4]:.2f} eV\n"
              f"Gamma1: {gamma1:.2f} ± {perr[5]:.2f} eV\n"
              f"Gamma2: {gamma2:.2f} ± {perr[6]:.2f} eV\n"
              f"Gamma3: {gamma3:.2f} ± {perr[7]:.2f} eV\n"
              f"Ratio 1 (Ka2/Ka1): {ratio1:.2f} ± {perr[8]:.2f}\n"
              f"Ratio 2 (Ka3/Ka1): {ratio2:.2f} ± {perr[9]:.2f}\n"
              f"Chi cuadrado reducido: {chi2_reducido:.2f}")

# Crear un gráfico con dos subgráficos apilados verticalmente
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10),  height_ratios=[2,1])

# Primer gráfico (ajuste)
ax1.errorbar(E, cuentas, yerr=sigma_cuentas, fmt='o', label='Datos experimentales', markersize=4, capsize=2)
ax1.plot(E_fit, cuentas_fit, 'r--', label='Ajuste Voigt Total')
ax1.plot(E_fit, voigt1, 'g--', label='Voigt Ka1')
ax1.plot(E_fit, voigt2, 'm--', label='Voigt Ka2')
ax1.plot(E_fit, voigt3, 'y--', label='Voigt asimetría')
ax1.plot(E_fit, fondo, 'b--', label='Fondo lineal')  # Añadir el fondo al gráfico
ax1.set_ylabel('Cuentas')
ax1.legend()
ax1.grid(True)
ax1.set_title(file_path)

# Agregar el cuadro de texto con los parámetros
ax1.text(0.05, 0.95, param_text, transform=ax1.transAxes, fontsize=11,
         verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", edgecolor='black', facecolor='white'))

# Segundo gráfico (residuos)
ax2.errorbar(E, residuos, yerr=sigma_cuentas, fmt='o', markersize=4, capsize=2, label='Residuos')
ax2.axhline(0, color='gray', linestyle='--')
# Añadir bandas de incertidumbre
ax2.fill_between(E, -3*sigma_cuentas, 3*sigma_cuentas, color='yellow', alpha=0.3, label='±3σ')
ax2.set_xlabel('Energía (eV)')
ax2.set_ylabel('Residuos')
ax2.legend()
ax2.grid(True)
ax2.set_title('Residuos del ajuste')

# Ajustar el layout para mejor visualización
plt.tight_layout()

# Mostrar el gráfico
plt.show()

# Guardar archivo de salida
data_output = pd.DataFrame({'Energía (eV)': E, 'Cuentas medidas': cuentas})
output_file = file_path.replace('.dat', '') + '_calib.dat'
data_output.to_csv(output_file, sep='\t', index=False)

print(f"Archivo guardado como: {output_file}")






