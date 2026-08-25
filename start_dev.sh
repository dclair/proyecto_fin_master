#!/bin/bash

# ==============================================================================
# SCRIPT DE INICIO - PROYECTO FIN DE MASTER (VERSIÓN TMUX)
# ==============================================================================
# Calculamos la ruta absoluta resolviendo el acceso directo (symlink)
SCRIPT_PATH="$(realpath "${BASH_SOURCE[0]}")"
PROJECT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
SESSION_NAME="TFM_Dev"

cd "$PROJECT_DIR" || { echo "Error: No se encontró el directorio del proyecto"; exit 1; }

echo "🏗️  Preparando el entorno..."

# 1. Levantando Base de Datos
echo "🗄️  Levantando MySQL/MariaDB..."
sudo systemctl start mysql 2>/dev/null
sudo systemctl start mariadb 2>/dev/null

echo "🚀 Iniciando sesión Tmux..."

# 2. Configurar Tmux
tmux has-session -t $SESSION_NAME 2>/dev/null

if [ $? != 0 ]; then
  # Crear nueva sesión en background (desatachada) con la primera ventana llamada "Servicios"
  tmux new-session -d -s $SESSION_NAME -n "Servicios" -c "$PROJECT_DIR"
  
  # --- PANEL IZQUIERDO: Servidor Django ---
  tmux send-keys -t $SESSION_NAME:0 "cd '$PROJECT_DIR' && source env/bin/activate" C-m
  tmux send-keys -t $SESSION_NAME:0 "python manage.py runserver" C-m
  
  # Dividir la ventana horizontalmente (50/50)
  tmux split-window -h -t $SESSION_NAME:0 -c "$PROJECT_DIR"
  
  # --- PANEL DERECHO (Arriba): Consola libre para git, tests o comandos ---
  tmux send-keys -t $SESSION_NAME:0.1 "cd '$PROJECT_DIR' && source env/bin/activate" C-m
  tmux send-keys -t $SESSION_NAME:0.1 "clear" C-m
  tmux send-keys -t $SESSION_NAME:0.1 "echo '⚡ Terminal libre con entorno virtual activado. ¡A codear!'" C-m
  
  # Dividir el panel derecho verticalmente (si tenés Redis, Celery, o querés ver logs de BD, lo hacés acá)
  tmux split-window -v -t $SESSION_NAME:0.1 -c "$PROJECT_DIR"
  
  # --- PANEL DERECHO (Abajo): Log de base de datos o consola extra ---
  tmux send-keys -t $SESSION_NAME:0.2 "cd '$PROJECT_DIR'" C-m
  tmux send-keys -t $SESSION_NAME:0.2 "clear" C-m
  tmux send-keys -t $SESSION_NAME:0.2 "echo '⚡ Acá podés levantar Redis, Celery, o usarlo para ver logs de base de datos.'" C-m
  
  # Seleccionar el panel izquierdo (Django) como el principal activo
  tmux select-pane -t $SESSION_NAME:0.0
fi

# 3. Lanzar la interfaz para conectarse a la sesión
# Verifica si se ejecutó desde una terminal existente o con doble clic
if [ -t 1 ]; then
  # Si estás en consola normal, simplemente atacha
  tmux attach -t $SESSION_NAME
else
  # Si hiciste doble clic en el acceso directo del escritorio, abre una terminal que se atacha
  if command -v gnome-terminal &> /dev/null; then
      gnome-terminal --maximize --title="TFM Dev Environment" -- tmux attach -t $SESSION_NAME
  else
      xterm -maximized -e "tmux attach -t $SESSION_NAME" &
  fi
fi
