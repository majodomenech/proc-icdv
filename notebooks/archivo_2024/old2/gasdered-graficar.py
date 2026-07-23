import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# Cargar datos (ignora líneas que comienzan con #)
Eads_lista = [-2.0,-1.0,0,1.0,2.0]
pot_quimicos = []
cubrimientos =[]

J=0
T=4000

for i in Eads_lista:
    data_i = np.loadtxt(f'datos/isoterma-L040-Eads{i}-J{J}-T0{T}K.dat', comments='#')
    pot_quimicos.append(data_i[:,0])
    cubrimientos.append(data_i[:,1])


# Graficar isotermas
plt.figure(figsize=(8,5))

colors = cm.viridis(np.linspace(0, 1, len(Eads_lista)))

for i, (Eads,color) in enumerate(zip(Eads_lista, colors)):
    plt.plot(pot_quimicos[i], cubrimientos[i], label=f'Eads={Eads}', marker='o', linestyle='-', markersize=3, color=color)

plt.xlabel('Potencial químico (eV)')
plt.ylabel('Cubrimiento (fracción)')
plt.title(f'Isotermas de adsorción T={T}K')
plt.grid(True)
plt.legend()
plt.savefig(f'datos/isoterma_Eads{Eads}_T{T}.png', dpi=300)
plt.show()