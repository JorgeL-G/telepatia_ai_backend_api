# telepatia_ai_backend_api
Telepatía backend API - API para captura, validación, almacenamiento, transcripción y estructuración de información clínica a partir de audio o texto. Diseñada para MVPs rápidos con FastAPI (Python)

## Despliegue Local

### Prerrequisitos
- Conda instalado
- Python 3.11

### Pasos para ejecutar localmente

1. **Crear ambiente virtual con conda**
   ```bash
   conda create -n telepatia_ai python=3.11
   conda activate telepatia_ai
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones de MongoDB
   ```

4. **Ejecutar la aplicación**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Verificar funcionamiento**
   - Abrir http://localhost:8000/docs para ver la documentación interactiva
   - Probar endpoint de health: http://localhost:8000/health

### Estructura del Proyecto
```
telepatia_ai_backend_api/
├── app/
│   ├── __init__.py
│   ├── main.py              # Punto de entrada de FastAPI
│   ├── config.py            # Configuración y variables de entorno
│   ├── database.py          # Conexión a MongoDB
│   └── routers/
│       ├── __init__.py
│       └── health.py        # Endpoint de health check
├── requirements.txt         # Dependencias de Python
├── .env.example            # Plantilla de variables de entorno
└── .gitignore              # Archivos a ignorar en git
```
