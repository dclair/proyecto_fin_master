🚀 Hubs&Clicks - Red Social de Aficionados
Hubs&Clicks es una plataforma web diseñada para conectar a personas a través de sus aficiones, permitiéndoles organizar eventos, unirse a quedadas y gestionar su comunidad de forma ágil, moderna y con una identidad visual corporativa única.

🛠️ Características Principales (Features)
1. Gestión de Eventos 360º
Creación y Edición: Los usuarios pueden proponer planes detallando lugar, fecha, hobby y límite de asistentes.

Sistema de Duplicado: Función inteligente para clonar eventos pasados y ahorrar tiempo al organizador.

Control de Asistencia: Sistema de "Me apunto/Desapuntarme" con validación de plazas en tiempo real.

Gestión de Estados: Soporte para eventos activos y finalizados.

Protocolo de Cancelación: Sistema seguro de cancelación que bloquea interacciones y notifica automáticamente a todos los asistentes.

2. Dashboard de Usuario (Perfiles Vitaminados)
Identidad Social: Perfiles con biografía, ubicación, sitio web y selección de aficiones con niveles.

Estadísticas en Tiempo Real: Contadores dinámicos de publicaciones, seguidores, siguiendo, eventos y participaciones.

Agenda Personal: Visualización de las próximas 3 citas confirmadas directamente en el perfil.

3. Sistema de Interacción y Feedback
Likes Dinámicos: Sistema de "Me gusta" con actualización asíncrona (AJAX/JS) y persistencia en base de datos.

Conversaciones Inteligentes: Hilos de comentarios tanto en publicaciones como en eventos, con lógica de detección de autor para evitar spam.

Notificaciones en Tiempo Real: Sistema de "campana" con contadores dinámicos (HTMX) para avisos de likes, comentarios, seguidores y alertas de eventos.

4. Ecosistema de Comunicación & Branding 📧
Emails HTML Corporativos: Notificaciones de sistema con diseño "Visión de Empresa", incluyendo logotipos incrustados (CID) y botones de acción.

Lógica de Notificación Dual: Cada interacción crítica genera un aviso interno (web) y, en casos de eventos o contacto, un correo electrónico profesional.

Formulario de Contacto Pro: Integración de mensajes de usuario con guardado en base de datos y aviso automático por email al administrador.

💻 Stack Tecnológico
Backend: Django 6.0 + Python 3.12.

Frontend: HTML5, CSS3, Bootstrap 5.3.

Interactividad: HTMX & JavaScript Vanilla (AJAX para sistema de Likes).

Comunicaciones: Django Mail (EmailMultiAlternatives) + MIME para incrustación de recursos.

Base de Datos: SQLite (Desarrollo) / MySQL (Producción).

🏗️ Estructura del Proyecto
Bash
aficionados_network/
├── posts/            # Gestión de Eventos, Publicaciones y Likes
├── profiles/         # Usuarios, Hobbies, Seguidores y Estadísticas
├── notifications/    # Motor de avisos internos y lógica de alertas
├── templates/        # UI Global
│   └── emails/       # Plantillas HTML corporativas para correos
└── static/           # Recursos estáticos (CSS, JS, Logo Corporativo)
⚙️ Instalación y Configuración
Sigue estos pasos para desplegar Hubs&Clicks en tu entorno local:

1. Clonar el repositorio
Bash
git clone https://github.com/tu-usuario/aficionados_network.git
cd aficionados_network
2. Configurar el entorno virtual
Se recomienda el uso de Python 3.12 para garantizar la compatibilidad con Django 6.0:

Bash
# Crear el entorno
python3 -m venv env

# Activar el entorno (Linux/macOS)
source env/bin/activate

# Activar el entorno (Windows)
env\Scripts\activate
3. Instalar dependencias
Asegúrate de tener el archivo requirements.txt actualizado:

Bash
pip install -r requirements.txt
4. Preparar la Base de Datos
Realiza las migraciones para crear la estructura de tablas (Eventos, Perfiles, Notificaciones, etc.):

Bash
python manage.py makemigrations
python manage.py migrate

### Configuración MySQL/MariaDB

Para usar MySQL o MariaDB en lugar de SQLite, crea tu `.env` a partir de `.env.example` y cambia la configuración de base de datos:

Bash
cp .env.example .env

Variables mínimas:

```env
DEBUG=True
SECRET_KEY=django-insecure-cambia-esto-en-local
DB_ENGINE=mysql
DB_NAME=aficionados_network_db
DB_USER=django_user
DB_PASSWORD=tu_password_seguro
DB_HOST=127.0.0.1
DB_PORT=3306
```

Crea la base de datos y el usuario:

```sql
CREATE DATABASE aficionados_network_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'django_user'@'127.0.0.1' IDENTIFIED BY 'tu_password_seguro';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX
  ON aficionados_network_db.*
  TO 'django_user'@'127.0.0.1';
FLUSH PRIVILEGES;
```

Después instala dependencias y aplica migraciones:

Bash
python -m pip install -r requirements.txt
python manage.py migrate

Para migrar datos desde SQLite:

Bash
DB_ENGINE=sqlite python manage.py dumpdata --natural-foreign --natural-primary --indent 2 -e sessions -e sites > db_full_backup.json
DB_ENGINE=mysql python manage.py flush --noinput
DB_ENGINE=mysql python manage.py loaddata db_full_backup.json

La migración ejecutada en este proyecto está registrada en `.sdd/changes/sqlite-to-mysql-migration/`.
La guía reutilizable para futuros proyectos está en `.sdd/knowledge/django-sqlite-to-mysql-mariadb.md`.
5. Crear superusuario (Admin)
Para gestionar las aficiones y los mensajes de contacto desde el panel:

Bash
python manage.py createsuperuser
6. Ejecutar el servidor
Bash
python manage.py runserver
La plataforma estará disponible en http://127.0.0.1:8000.

📧 Configuración de Email (Desarrollo)
Para probar el sistema de notificaciones por correo sin configurar un servidor SMTP real, el proyecto está configurado para mostrar los emails en la consola.

Si deseas cambiar a un entorno de producción, ajusta las siguientes variables en settings.py:

EMAIL_BACKEND: Define el motor de envío.

CONTACT_EMAIL: Dirección donde recibirás los mensajes del formulario de contacto.

📈 Roadmap
[x] Sistema de Notificaciones: Implementado (Likes, Comentarios, Eventos).

[x] Identidad Corporativa: Emails y diseño unificado.

[ ] Sistema de Valoraciones (Reviews): Puntuación por estrellas tras finalizar un evento (Estructura base iniciada).

[ ] Filtro de "Mis Aficiones": Acceso rápido a eventos que coinciden con los hobbies del perfil.

[ ] Chat en tiempo real: Para coordinar los detalles de cada quedada.

Hubs&Clicks - "Descubre, Comparte, Disfruta"
