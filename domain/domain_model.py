from __future__ import annotations
from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field, ConfigDict

# ---------------------------------------------------------
# 1. Definición de Pasos (Steps)
# ---------------------------------------------------------
class Step(BaseModel):
    """
    Representa una tarea individual secuencial dentro de un Job.
    Según la doc: Un step puede ejecutar comandos, tareas de configuración
    o una acción de su repositorio, un repositorio público o una imagen Docker.
    """
    model_config = ConfigDict(populate_by_name=True)

    # El nombre que se muestra en la interfaz de usuario de GitHub Actions para este paso.
    name: Optional[str] = None
    
    # Un identificador único para el paso. Permite referenciarlo en contextos 
    # (ej: steps.<id>.outputs).
    id: Optional[str] = None
    
    # Expresión condicional. El paso solo se ejecutará si esta condición se evalúa como verdadera.
    # Docs: "You can use the if conditional to prevent a step from running unless a condition is met."
    if_condition: Optional[str] = Field(default=None, alias="if") 
    
    # Selecciona una acción para ejecutar como parte de un paso en su trabajo. 
    # Es mutuamente excluyente con 'run'.
    # Ejemplo: actions/checkout@v4
    uses: Optional[str] = None
    
    # Ejecuta programas de línea de comandos usando el shell del sistema operativo.
    # Es mutuamente excluyente con 'uses'.
    run: Optional[str] = None
    
    # Especifica el directorio de trabajo donde se ejecutará el comando 'run'.
    # Si no se define, usa el default del job.
    working_directory: Optional[str] = Field(default=None, alias="working-directory")
    
    # Permite anular la configuración de shell predeterminada en el sistema operativo del ejecutor.
    # Ejemplo: 'bash', 'pwsh', 'python'.
    shell: Optional[str] = None
    
    # Un mapa de parámetros de entrada exigidos por la acción definida en 'uses'.
    # Docs: "A map of the input parameters defined by the action."
    with_args: Optional[Dict[str, Any]] = Field(default=None, alias="with") 
    
    # Establece variables de entorno disponibles solo para este paso.
    env: Optional[Dict[str, Union[str, int, bool]]] = None
    
    # Evita que el trabajo falle si este paso falla. 
    # Si es true, el trabajo continúa al siguiente paso incluso si este devuelve error.
    continue_on_error: Optional[bool] = Field(default=False, alias="continue-on-error")
    
    # El número máximo de minutos para ejecutar el paso antes de matar el proceso.
    timeout_minutes: Optional[int] = Field(default=None, alias="timeout-minutes")


# ---------------------------------------------------------
# 2. Definición de Trabajos (Jobs)
# ---------------------------------------------------------
class Job(BaseModel):
    """
    Representa un conjunto de pasos que se ejecutan en el mismo ejecutor (runner).
    Los jobs se ejecutan en paralelo por defecto, a menos que se use 'needs'.
    """
    model_config = ConfigDict(populate_by_name=True)

    # El nombre del trabajo que se muestra en la interfaz de GitHub.
    name: Optional[str] = None
    
    # Identifica cualquier trabajo que deba completarse satisfactoriamente antes de que este trabajo se ejecute.
    # Crea dependencias secuenciales entre jobs.
    needs: Optional[Union[str, List[str]]] = None 
    
    # Define el tipo de máquina en la que se ejecutará el trabajo.
    # Ejemplo: "ubuntu-latest", "windows-2019", o etiquetas de self-hosted.
    runs_on: Union[str, List[str]] = Field(alias="runs-on")
    
    # Modifica los permisos predeterminados otorgados al GITHUB_TOKEN para este trabajo.
    # Puede ser 'read-all', 'write-all' o un diccionario específico.
    permissions: Optional[Union[str, Dict[str, str]]] = None
    
    # Define el nombre del entorno (environment) al que hace referencia el trabajo.
    # Se usa para reglas de protección y secretos específicos de entorno (ej: 'production').
    environment: Optional[Union[str, Dict[str, Any]]] = None
    
    # Un mapa de salidas (outputs) generadas por este job que estarán disponibles para 
    # otros jobs que dependan de este.
    outputs: Optional[Dict[str, str]] = None
    
    # Variables de entorno disponibles para todos los pasos del trabajo.
    env: Optional[Dict[str, Union[str, int, bool]]] = None
    
    # Configuración predeterminada que se aplicará a todos los pasos del trabajo.
    # Comúnmente usado para definir un 'shell' o 'working-directory' global para el job.
    defaults: Optional[Dict[str, Any]] = None
    
    # Condicional para evitar que el trabajo se ejecute a menos que se cumpla la condición.
    if_condition: Optional[str] = Field(default=None, alias="if")
    
    # La lista de pasos (tareas) que componen el trabajo.
    steps: List[Step] = []
    
    # Crea una matriz de compilación para ejecutar trabajos en múltiples variaciones simultáneamente.
    # (Ej: ejecutar tests en node 14, 16 y 18).
    strategy: Optional[Dict[str, Any]] = None 
    
    # Asegura que solo se ejecute un trabajo o flujo de trabajo a la vez en el mismo grupo de concurrencia.
    # Útil para evitar condiciones de carrera o despliegues solapados.
    concurrency: Optional[Union[str, Dict[str, Any]]] = None
    
    # Contenedores de servicios (como Redis, Postgres) para alojar servicios necesarios para el trabajo.
    # GitHub crea una red Docker bridge para comunicar el runner con estos servicios.
    services: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------
# 3. Definición de Triggers (On)
# ---------------------------------------------------------
# El atributo 'on' define qué eventos activan el flujo de trabajo.
# Docs: "To automatically trigger a workflow, use on to define which events cause the workflow to run."
WorkflowTrigger = Union[str, List[str], Dict[str, Any]]


# ---------------------------------------------------------
# 4. Definición del Workflow (Raíz)
# ---------------------------------------------------------
class Workflow(BaseModel):
    """
    Modelo raíz que representa el archivo .yaml completo de configuración de GitHub Actions.
    Un workflow es un proceso automatizado configurable compuesto por uno o más jobs.
    """
    model_config = ConfigDict(populate_by_name=True)

    # El nombre del flujo de trabajo. GitHub muestra este nombre en la pestaña "Actions".
    name: Optional[str] = None
    
    # El nombre para las ejecuciones de flujo de trabajo generadas desde el flujo de trabajo.
    # Permite nombres dinámicos usando contextos (ej: 'Deploy to production by @user').
    run_name: Optional[str] = Field(default=None, alias="run-name")
    
    # Evento o eventos que desencadenan el flujo de trabajo. OBLIGATORIO.
    on: WorkflowTrigger
    
    # Modifica los permisos predeterminados del GITHUB_TOKEN para todo el flujo de trabajo.
    permissions: Optional[Union[str, Dict[str, str]]] = None
    
    # Variables de entorno disponibles para todos los jobs y steps en el flujo de trabajo.
    env: Optional[Dict[str, Union[str, int, bool]]] = None
    
    # Un conjunto de trabajos que ejecuta el flujo de trabajo. OBLIGATORIO.
    # Se define como diccionario porque en YAML las claves son los IDs de los jobs.
    jobs: Dict[str, Job]

    # Gestión de concurrencia a nivel global del workflow.
    # Si se define aquí, afecta a todas las ejecuciones de este workflow.
    concurrency: Optional[Union[str, Dict[str, Any]]] = None