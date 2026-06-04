# Requisitos Universitarios del Proyecto Final de Máster (PFM)

Este documento contiene las reglas y restricciones inamovibles impuestas por la universidad para la aprobación del Proyecto Final de Máster en Desarrollo Full Stack. Todo agente que trabaje en este repositorio DEBE acatar estos requisitos.

## 1. Stack Tecnológico Obligatorio
- **Backend (30% de la nota final):** DEBE ser desarrollado íntegramente en Django. Debe incluir modelos, vistas, plantillas, autenticación y persistencia de datos.
- **Frontend (15% de la nota final):** Es OBLIGATORIO incluir al menos una o dos vistas integradas con **React**. Estas vistas en React deben consumir datos reales del backend (Django). El proyecto principal se basa en Django, pero la integración de React es un requisito estricto para aprobar.

## 2. Calidad, Arquitectura y Seguridad
- **Arquitectura y buenas prácticas (15%):** El código debe tener una estructura limpia y coherente. Priorizar el concepto de MVP funcional y bien estructurado por sobre la cantidad de funcionalidades.
- **Seguridad (15%):** Debe contar con protección contra CSRF/XSS, validación de datos, autenticación segura, hashing de contraseñas y estar preparado para HTTPS.

## 3. Despliegue y Control de Versiones
- **Repositorio (GitHub):** Debe incluir un `README.md` detallado (con instrucciones de instalación, configuración y uso) y un historial de commits claro y progresivo.
- **Despliegue:** La aplicación tiene que estar subida y funcional en una URL pública (VPS, Render, Railway, AWS, etc.).

## 4. Documentación y Presentación
- Se requiere redactar un documento (PDF/Word) que actúe como memoria técnica detallando: definición del problema, reflexión del valor aportado, stack utilizado, tipos de usuarios, casos de uso y medidas de seguridad.
- Se debe grabar un video explicativo de máximo 5 minutos demostrando la funcionalidad, incluyendo obligatoriamente la vista en React consumiendo datos.

## INSTRUCCIONES PARA AGENTES DE IA
1. **NO sugieras reescribir todo el frontend en React.** La universidad exige que el backend y la base de la app sea Django, con solo *algunas* vistas (mínimo 1 o 2) en React.
2. Asegúrate de documentar bien el código y mantener un historial de commits limpio para ayudar al alumno en su evaluación.
3. Al implementar el frontend (como el chat), ten en cuenta que implementar una de estas vistas en React puede ser la oportunidad perfecta para cumplir con el requisito de "consumo de datos desde el backend en React".
