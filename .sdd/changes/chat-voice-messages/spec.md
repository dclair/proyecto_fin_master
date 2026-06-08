# Specification: chat-voice-messages

## User Stories
1. **Grabar Audio:** Como usuario, quiero poder grabar un mensaje de voz directamente desde la interfaz del chat para no tener que escribir cuando estoy apurado.
2. **Cancelar Grabación:** Como usuario, quiero poder cancelar la grabación antes de enviarla si me equivoqué.
3. **Enviar Audio:** Como usuario, quiero que la nota de voz se envíe y aparezca en la conversación en tiempo real, igual que un mensaje de texto.
4. **Reproducir Audio:** Como usuario, quiero poder reproducir las notas de voz que me envían o que envié directamente en el chat.

## Functional Requirements
- **FR1:** El sistema debe solicitar permisos de micrófono al intentar grabar por primera vez.
- **FR2:** Durante la grabación, el input de texto normal debe ocultarse o deshabilitarse, mostrando un indicador visual de "Grabando" y un temporizador.
- **FR3:** El audio grabado debe limitarse en el backend a un máximo de 10MB.
- **FR4:** El mensaje de audio debe renderizarse usando el reproductor nativo del navegador (`<audio>`).

## Non-Functional Requirements
- **Compatibilidad:** Debe funcionar en navegadores modernos de escritorio y móviles sin necesidad de plugins externos.
- **Rendimiento:** La carga del audio debe ser asíncrona y utilizar el mismo flujo de subida multipart que las imágenes.

## Out of Scope
- Transcripción automática de audio a texto.
- Transcodificación en el servidor (se guardará el formato nativo del navegador cliente).
