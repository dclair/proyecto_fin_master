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
  
  # --- PANEL 0: Servidor Django ---
  tmux send-keys -t $SESSION_NAME:0.0 "cd '$PROJECT_DIR' && source env/bin/activate" C-m
  tmux send-keys -t $SESSION_NAME:0.0 "python manage.py runserver" C-m
  
  # --- PANEL 1: Vite (React Frontend) ---
  # Dividimos horizontalmente. Queda a la derecha.
  tmux split-window -h -t $SESSION_NAME:0.0 -c "$PROJECT_DIR/frontend"
  tmux send-keys -t $SESSION_NAME:0.1 "npm run dev" C-m
  
  # --- PANEL 2: Redis ---
  # Dividimos verticalmente el panel izquierdo. Queda abajo a la izquierda.
  tmux split-window -v -t $SESSION_NAME:0.0 -c "$PROJECT_DIR"
  tmux send-keys -t $SESSION_NAME:0.1 "redis-server" C-m
  
  # --- VENTANA 2 (Consola libre) ---
  tmux new-window -t $SESSION_NAME:1 -n "Terminal" -c "$PROJECT_DIR"
  tmux send-keys -t $SESSION_NAME:1.0 "cd '$PROJECT_DIR' && source env/bin/activate" C-m
  tmux send-keys -t $SESSION_NAME:1.0 "clear" C-m
  tmux send-keys -t $SESSION_NAME:1.0 "echo '⚡ Terminal libre lista para usar. Vite, Redis y Django están en la ventana 0 (Ctrl+b, 0)'" C-m
  
  # Seleccionar el panel izquierdo (Django) en la primera ventana
  tmux select-window -t $SESSION_NAME:0
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
