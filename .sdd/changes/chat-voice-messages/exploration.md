## Exploration: chat-voice-messages

### Current State

El backend ya cuenta con un modelo de `Message` que soporta archivos adjuntos (`attachment` y `attachment_type`).
El endpoint `MessageUploadView` (`chat/api_views.py`) maneja la subida de archivos multipart y clasifica el `attachment_type` analizando el `mime_type` (soporta 'image', 'video' o fallback a 'document'). Los mensajes se envían luego por websockets a través de Channels.
En el frontend (`ChatApp.jsx`), actualmente solo hay lógica para adjuntar archivos tradicionales desde el sistema de archivos, sin captura de dispositivos de entrada (micrófono).

### Affected Areas

- `chat/api_views.py` — Se debe modificar `MessageUploadView` para reconocer el MIME type `audio/*` y asignar `attachment_type = 'audio'`, idealmente con un límite de tamaño específico (ej. 10MB).
- `frontend/src/components/ChatApp.jsx` — Hay que implementar:
  1. Uso de `navigator.mediaDevices.getUserMedia` y `MediaRecorder` para grabar audio.
  2. UI: botones para empezar a grabar, detener, cancelar y visualizar el tiempo de grabación.
  3. Lógica para encapsular el `Blob` resultante de la grabación en un objeto File y enviarlo vía `FormData` a la API existente.
  4. Renderizado: si el mensaje recibido tiene `attachment_type === 'audio'`, renderizar un reproductor `<audio controls src={url}></audio>`.
- `frontend/src/components/ChatApp.css` — Estilos para el estado "grabando" y para los controles del reproductor nativo.

### Approaches

1. **Extensión del Attachment System Existente (Lo que más me han Recomendado)**
   - Consiste en tratar la nota de voz exactamente igual que un adjunto normal en el backend, añadiendo `audio` a los tipos permitidos. El frontend se encarga de la interfaz de grabación y genera un archivo `Blob` para subir.
   - Pros: Cero cambios en los modelos de base de datos (`models.py`), reutilización del endpoint de subida, fácil sincronización con websockets.
   - Cons: Hay que gestionar bien los permisos del navegador en el frontend y lidiar con los formatos en los que graba nativamente cada navegador (Safari graba mp4/aac, Chrome webm/opus).
   - Effort: Low-Medium.

2. **Transcodificación en Backend con FFmpeg (no lo vamos a realizar)**
   - Recibir cualquier formato de audio desde el frontend y convertirlo a un formato estándar (ej. mp3) usando Celery + FFmpeg antes de servirlo.
   - Pros: Máxima compatibilidad asegurada en todos los dispositivos.
   - Cons: Introduce dependencias pesadas (FFmpeg en el servidor), requiere workers asíncronos para no bloquear la subida, esfuerzo enorme e innecesario para un MVP.
   - Effort: High.

### Recommendation

**Extensión del Attachment System Existente.** Los navegadores modernos hoy en día son lo suficientemente compatibles con HTML5 `<audio>` para reproducir lo que graban los demás. Simplemente capturamos el blob y lo subimos usando la misma infraestructura que ya armamos para las imágenes y documentos.

### Risks

- **Permisos de Micrófono:** Si el navegador rechaza el acceso, hay que manejar el error gracefulmente en la UI.
- **Compatibilidad de Formatos iOS/Safari:** Safari (especialmente en iOS viejo) puede tener quirks para reproducir WebM (creado por Chrome). Puede requerir que el MIME type se asigne correctamente en base a lo que se graba.

### Ready for Proposal

Yes. Todo el contexto técnico está claro y no se requieren cambios en los modelos de BD.
