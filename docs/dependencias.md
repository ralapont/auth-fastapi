# Dependencias del proyecto

1. FastAPI

FastAPI es un framework web moderno y de alto rendimiento para construir APIs en Python, diseñado para ser rápido, intuitivo y fácil de usar, aprovechando al máximo las type hints de Python para ofrecer validación automática, documentación interactiva y desarrollo acelerado.  

🔧 Características principales de FastAPI

* Moderno y muy rápido: ofrece un rendimiento comparable a Node.js y Go gracias a su base en Starlette y Pydantic.  
* Basado en anotaciones de tipos de Python: esto permite validación automática, serialización y generación de documentación sin esfuerzo.  
* Con documentación interactiva automática: genera Swagger UI y ReDoc sin configuraciones adicionales.  
* Sencillo y rápido de desarrollar: reduce “errores humanos” y duplica la velocidad de desarrollo según sus creadores.  
* Compatible con estándares: utiliza OpenAPI y JSON Schema.  

Para más información (https://fastapi.tiangolo.com [fastapi.tiangolo.com])

2. uvicorn

Uvicorn es un servidor web ASGI (Asynchronous Server Gateway Interface) para Python, ligero, rápido y optimizado para ejecutar aplicaciones asíncronas, especialmente frameworks modernos como FastAPI o Starlette.  

🔧 ¿Qué significa esto en términos prácticos?

✔ Servidor ASGI de alto rendimiento
Uvicorn implementa el estándar ASGI, que permite manejar conexiones concurrentes, WebSockets y operaciones asíncronas, superando las limitaciones del antiguo WSGI.  
✔ Soporta HTTP/1.1 y WebSockets
Esto lo convierte en un servidor ideal para APIs modernas, aplicaciones en tiempo real o servicios que requieren alta concurrencia.  
✔ Ligero, minimalista y muy rápido
Cuando instalas uvicorn[standard], Uvicorn incorpora componentes optimizados como:

* uvloop → event loop ultrarrápido
* httptools → parser HTTP eficiente
* watchfiles → recarga automática en desarrollo

✔ Integración perfecta con FastAPI  
Muchos de tus propios documentos indican que usas Uvicorn como servidor principal para ejecutar proyectos FastAPI, por ejemplo:

* En Autenticación Centralizada FastAPI.docx, se describe cómo instalar uvicorn[standard] como servidor ASGI para arrancar la API.
* En creacion de tres servicios fastapi.docx se muestra cómo lanzar la API con uvicorn app.main:app --reload

Para más información (https://uvicorn.dev [uvicorn.dev])

