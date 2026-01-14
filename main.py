import sys
from pathlib import Path
import yaml
from pydantic import ValidationError

from domain.domain_model import Workflow

def load_yaml(path: Path) -> dict:
    """
    Carga un archivo YAML desde disco y lo parsea a dict.
    """
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")

    if path.suffix not in {".yml", ".yaml"}:
        raise ValueError("El archivo debe ser .yml o .yaml")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    # PyYAML (YAML 1.1) interpreta 'on:' como el booleano True.
    # Si encontramos la clave True, la renombramos a "on".
    if isinstance(data, dict) and True in data:
        data["on"] = data.pop(True)
    
    return data


def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <ruta_archivo.yml>")
        sys.exit(1)

    yaml_path = Path(sys.argv[1])

    try:
        # 1. Cargar YAML
        data = load_yaml(yaml_path)
        workflow = Workflow.model_validate(data)

        # 2. Output de prueba
        print(f"\n✅ Workflow cargado: {workflow.name}")
        print(f"Trigger: {workflow.on}\n")

        for job_id, job in workflow.jobs.items():
            print(f"🧩 Job ID: {job_id}")
            runs_on_str = job.runs_on if isinstance(job.runs_on, str) else ", ".join(job.runs_on)
            print(f"   Corre en: {runs_on_str}")

            for step in job.steps:
                if step.uses:
                    print(f"   • Usa acción: {step.uses}")
                elif step.run:
                    
                    cmd = step.run.strip().split('\n')[0]
                    if len(step.run) > 50: cmd += "..."
                    print(f"   • Ejecuta: {cmd}")

            print()

    except ValidationError as e:
        
        print(f"❌ Error de Validación del Modelo:\n{e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()