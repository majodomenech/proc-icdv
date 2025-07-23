#!/bin/bash
# ------------------------------------------------------------
# 1. Crea el entorno virtual de Python para el repositorio local
# 2. Instala los requerimentos del archivo requirements.txt
# ------------------------------------------------------------

set -e  # hace que el script falle si algún comando falla

# Si ocurre un error, se elimina el .venv
trap 'echo "Error detectado. Eliminando .venv..."; rm -rf .venv' ERR

python3 -m venv ../.venv             # si .venv ya existe, no hace nada. Si queres borrarlo ejecutar: # rm -rf .venv
source ../.venv/bin/activate

pip install --upgrade pip

if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo "No se encontró requirements.txt"
fi

# Si todo fue bien, se desactiva el trap
trap - ERR

echo .venv creado y activado con las librerías especificadas en requirements.txt !!
echo
echo "Para activar el entorno virtual, ejecutá:"
echo "    source ../.venv/bin/activate"

exit 0