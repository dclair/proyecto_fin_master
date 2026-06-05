# Arquitectura del Sistema de Chat en Aficionados Network

Este documento registra el diseño, componentes y reglas de negocio del sistema de mensajería (1-a-1 y Grupos) implementado en el proyecto. **Los agentes deben leer esto antes de modificar la aplicación de chat.**

## 1. Modelos de Datos (`chat/models.py`)
- **`Conversation`**:
  - `is_group` (Booleano): Diferencia entre chat privado (1-a-1) y grupo.
  - `name` (String): Nombre del grupo (solo aplica si `is_group=True`).
  - `admin` (ForeignKey a User): El creador del grupo. Solo el admin tiene ciertos privilegios.
- **`ConversationParticipant`**:
  - Relación entre `Conversation` y `User`.
  - `last_read_timestamp`: Marca de tiempo que registra cuándo el usuario entró por última vez al chat. Usado para calcular mensajes no leídos.
- **`Message`**:
  - Pertenece a una `Conversation` y tiene un `sender` (User).
- **`GroupJoinRequest`**:
  - `user`, `conversation`, `status` ('pending', 'accepted', 'rejected').
  - Gestiona las solicitudes de los usuarios para unirse a grupos públicos.

## 2. Lógica de Seguridad y Permisos
- **Creación de chats privados**: Al intentar crear un chat con un usuario, el backend verifica si ya existe una conversación 1-a-1 entre ambos. Si existe, la devuelve; si no, la crea. No se permiten chats consigo mismo.
- **Invitación a Grupos**: Solo el `admin` del grupo puede invitar o añadir usuarios directamente (`/api/chat/groups/<id>/add_users/`).
- **Exploración y Solicitudes**: Los usuarios pueden explorar grupos (`/api/chat/groups/discover/`) a los que NO pertenecen y enviar una `GroupJoinRequest`.
- **Aceptación de Solicitudes**: Solo el `admin` recibe notificaciones de solicitudes pendientes y puede aceptar o rechazar (`ManageJoinRequestView`).
- **Eliminación de Conversaciones** (`ConversationDeleteView`):
  - **1-a-1**: Cualquiera de los 2 participantes puede borrarlo. El borrado es en cascada y se elimina de la base de datos para ambos.
  - **Grupos**: SOLO el `admin` puede borrar el grupo.

## 3. Frontend (React)
- **Estado Global (`ChatApp.jsx`)**: 
  - Maneja las listas de conversaciones, sondeos (polling cada 15s) para recargar chats y contador de mensajes no leídos.
  - Componentes inyectados: `ConversationList`, `MessageArea`, `GroupCreator`, `GroupExplorer`, `UserExplorer`.
- **Notificaciones de "No leídos"**:
  - `ChatApp` ordena la lista priorizando los chats con `unread_count > 0` y luego por fecha del último mensaje.
  - `ConversationList` muestra un "badge" rojo con el conteo numérico de `unread_count`.
- **UI del Admin en Grupos (`MessageArea.jsx`)**:
  - Se valida con `isAdmin = isGroup && me && activeConversation.admin === me.id`.
  - Muestra un panel de solicitudes pendientes (icono de campana/usuario rojo).
  - Muestra un panel para añadir usuarios (buscador en vivo contra `/api/chat/users/`).
  - Muestra el botón de Papelera (`Trash2`) para eliminar el grupo.

## 4. Tecnologías y Tráfico
- **REST API**: Django REST Framework. Protegido por autenticación basada en sesiones de Django (CSRF Token presente en cookies).
- **Tiempo Real**: Django Channels (WebSockets) implementado en el hook `useWebSocket.js`.
- **Seguridad en Producción**: Todo el tráfico viaja encriptado por HTTPS y WSS. Los mensajes NO están encriptados de extremo a extremo (E2EE) ni en reposo en la BD, modelo clásico tipo red social.

*Nota de actualización: Junio 2026. Implementación base, grupos, búsqueda de usuarios, indicadores de no leídos y limpieza de chats finalizada.*
