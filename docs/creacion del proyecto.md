# Creación del Proyecto con Poetry

Poetry es una herramienta moderna de gestión de dependencias y empaquetado para Python, diseñada para simplificar y unificar todo el ciclo de vida de un proyecto Python.

📝 ¿Qué es Poetry?  

Poetry es una herramienta para gestionar dependencias y empaquetar proyectos en Python, que permite declarar las librerías que necesita un proyecto y se encarga de instalarlas, actualizarlas y asegurar que las versiones sean reproducibles.  
Además de gestionar dependencias, Poetry también crea y administra entornos virtuales, construye paquetes para distribución y permite publicarlos en PyPI, integrando en un solo flujo lo que antes requería varias herramientas separadas.  

🔧 ¿Qué problemas resuelve?

Poetry aporta:  

✔ Gestión de dependencias confiable

* Instala y resuelve dependencias manteniendo la compatibilidad entre versiones.
* Usa un archivo de bloqueo (poetry.lock) para garantizar instalaciones idénticas en distintos entornos.  

✔ Entornos virtuales automáticos

Crea y gestiona un entorno virtual por proyecto sin necesidad de venv o virtualenv.  

✔ Configuración centralizada con pyproject.toml

Toda la configuración del proyecto (metadatos, dependencias, versión, etc.) se define en un único archivo estándar.  

✔ Herramienta unificada

Reemplaza el uso conjunto de pip, requirements.txt, setup.py, virtualenv y parte de setuptools.  

✔ Empaquetado y publicación

Permite construir distribuciones y publicarlas fácilmente en PyPI.  

La web principal de Poetry ( https://python-poetry.org [python-poetry.org])

## Para crear el proyecto procedemos:

1. Iniciar proyecto

```shell
poetry init
```
El comando poetry init sirve para inicializar un proyecto Poetry dentro de un directorio existente, creando de forma interactiva el archivo pyproject.toml, que es el corazón de un proyecto gestionado con Poetry.

🧩 ¿Qué hace poetry init?

✔ Crea un archivo pyproject.toml
El comando pide datos como:

* nombre del paquete
* versión
* descripción
* autor
* licencia
* dependencias

2. Creamos y nos movemos al directorio auth-fastapi 

```shell
mkdir auth-fastapi && cd auth-fastapi 
```

3. Activar entorno virtual

A partir de la versión 2.0 de Poetry la gestión de entornos virtuales se hace con poetry env 

```shell
poetry env use python3.12
```

Para obtener la ruta del virtualenv

```shell
poetry env info –path
Using virtualenv: /home/rafael/.cache/pypoetry/virtualenvs/auth-fastapi-65J-kXEr-py3.12 es el path del virtualenv 
```

4. Para eliminar un virtualenv 

Listar los virtualenv

```shell
poetry env list 
```

Eliminar los virtualenv

```shell
poetry env remove <virtualenv> 
```


