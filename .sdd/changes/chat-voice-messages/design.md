# Design: chat-voice-messages

## Data Models
No hay cambios en la base de datos. Se reutiliza la columna `attachment_type` de la tabla `chat_message` para almacenar el valor `audio`.

## API Endpoints
**Modificación:** `POST /api/chat/messages/<conversation_id>/`
- Validará el `mime_type` del archivo enviado.
- Si empieza con `audio/`, asignará `attachment_type = 'audio'`.
- Validará que `file_size <= 10 * 1024 * 1024` (10 MB).

## Frontend Components (React)

### State additions in `ChatApp.jsx`
- `isRecording`: `boolean` - Indica si se está grabando.
- `recordingTime`: `number` - Segundos transcurridos de grabación.
- `mediaRecorderRef`: `useRef` - Mantiene la instancia del `MediaRecorder`.
- `audioChunksRef`: `useRef` - Mantiene los chunks de datos de audio (`Blob[]`).

### UI Elements
- **Record Button:** Un botón con un icono de micrófono junto al input de texto y adjuntos.
- **Recording Bar:** Cuando `isRecording` es `true`, reemplaza la caja de texto. Muestra un punto rojo parpadeante, el tiempo (`00:15`), un botón de cancelar (basurero/X) y un botón de enviar.
- **Audio Message Rendering:** Dentro de la función/componente que renderiza cada mensaje, añadir una rama condicional:
  ```jsx
  if (msg.attachment_type === 'audio') {
      return <audio controls src={msg.attachment} className="max-w-full" preload="metadata" />;
  }
  ```

## Security & Permissions
- Frontend: Debe invocar `navigator.mediaDevices.getUserMedia({ audio: true })`. Si el usuario deniega, atrapar la excepción (`NotAllowedError`) y mostrar un alert o toast indicando que se requiere permiso del micrófono.
