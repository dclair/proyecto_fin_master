## Proposal: chat-voice-messages

### Executive Summary
Añadir soporte para notas de voz en el chat existente extendiendo el sistema de archivos adjuntos. El frontend capturará el audio mediante la `MediaRecorder API` y lo enviará al backend, donde será procesado y almacenado como un adjunto de tipo `audio`. El reproductor nativo HTML5 se encargará de la reproducción en los clientes.

### Scope & Goals
- **In-Scope**:
  - Captura de audio desde el navegador (escritorio y móvil).
  - Interfaz de usuario para grabar, detener y cancelar (con contador de tiempo).
  - Envío del audio al endpoint de subida existente.
  - Reproducción de mensajes de audio en la UI del chat.
- **Out-of-Scope**:
  - Transcodificación de audio en el backend (ej. convertir WebM a MP3).
  - Transcripción de voz a texto.
  - Envío de audio mientras la app está en segundo plano (requerimientos nativos).

### Technical Architecture

#### Backend
- **Endpoint `MessageUploadView`**: Modificar la validación de `mime_type` para interceptar `audio/*`.
  - Asignar `attachment_type = 'audio'`.
  - Establecer un límite máximo razonable de tamaño (ej. 10MB, suficiente para ~10 minutos de voz).
- **Modelo `Message`**: No requiere migración, la columna `attachment_type` ya es un `CharField`.

#### Frontend
- **Captura (`MediaRecorder`)**:
  - Solicitar permisos de `navigator.mediaDevices.getUserMedia({ audio: true })`.
  - Mantener estado de grabación (`isRecording`, `recordingTime`, `audioBlob`).
  - Al detener, empaquetar el `audioBlob` en un objeto `File` con extensión `.webm` o `.mp4` según el `mimeType` del recorder.
- **UI de Envío (`ChatApp.jsx`)**:
  - Reemplazar/añadir al botón de adjuntos un icono de micrófono.
  - Mientras se graba, ocultar el input de texto y mostrar un contador parpadeante.
- **UI de Recepción**:
  - En la renderización de mensajes, si `msg.attachment_type === 'audio'`, renderizar `<audio controls src={msg.attachment} className="chat-audio-player" preload="metadata" />`.

### Tradeoffs & Risks
1. **Quirks de Formatos de Audio**: Chrome graba en `audio/webm;codecs=opus`, Safari en `audio/mp4`. Afortunadamente, iOS Safari 15+ ya soporta reproducción de WebM, por lo que las notas grabadas en Android/Desktop se escucharán en iOS y viceversa.
2. **Permisos de UI**: Es fundamental manejar el caso en que el usuario deniegue el permiso de micrófono (ej. mostrando un toast/alerta y desactivando el botón de grabar).

### Effort Estimate
**Low-Medium**. Todo el sistema de mensajería (WebSockets, almacenamiento S3/local, DB) ya está hecho, solo se añade un nuevo tipo de carga útil y una nueva interfaz de entrada en el cliente React.
