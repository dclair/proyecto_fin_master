import asyncio
import os
import sys

# Script para instanciar un sub-agente y correr la fase sdd-explore.
# Asegurate de tener instalada la librería: pip install google-antigravity
# Y de tener seteada la variable de entorno GEMINI_API_KEY

try:
    from google.antigravity import Agent, LocalAgentConfig
except ImportError:
    print("Error: No se encontró la librería google-antigravity.")
    print("Instalala corriendo: pip install google-antigravity")
    sys.exit(1)

async def main():
    print("🚀 Levantando sub-agente para auditoría de producción (sdd-explore)...")
    
    # Directorio donde creamos la skill sdd-explore
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    skills_directory = os.path.join(project_root, ".agent", "skills")
    
    # Verificamos que exista la carpeta
    if not os.path.exists(skills_directory):
        print(f"Error: No se encontró el directorio de skills en {skills_directory}")
        sys.exit(1)

    # Configuramos el agente para que cargue la skill desde el file system
    config = LocalAgentConfig(
        skills_paths=[skills_directory],
        # Activamos sub-agentes por las dudas, aunque este agente es en sí el sub-agente de análisis
        # capabilities=types.CapabilitiesConfig(enable_subagents=True)
    )

    try:
        async with Agent(config) as agent:
            print("🧠 Sub-agente instanciado. Iniciando exploración y lectura del workspace...")
            prompt = (
                "Por favor, utilizá la skill 'sdd-explore' para hacer una auditoría de producción de este proyecto. "
                "Leé los archivos necesarios, identificá riesgos (por ejemplo, base de datos SQLite, variables de entorno, seguridad) "
                "y escribí el reporte final en '.sdd/changes/auditoria-produccion/explore.md'."
            )
            response = await agent.chat(prompt)
            print("\n✅ Sub-agente terminó la tarea. Respuesta final:")
            print("-" * 50)
            print(await response.text())
            print("-" * 50)
    except Exception as e:
        print(f"❌ Error durante la ejecución del agente: {e}")
        if "API_KEY" in str(e).upper() or "CREDENTIALS" in str(e).upper():
            print("Recordatorio: Necesitás configurar la variable de entorno GEMINI_API_KEY.")

if __name__ == "__main__":
    asyncio.run(main())
