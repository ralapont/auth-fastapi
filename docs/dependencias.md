# Dependencias del proyecto

## Instalación de las dependencias con Poetry

Para instalar las dependencias necesarias con Poetry es necesario ejecutar los siguientes comandos:

```shell

poetry add fastapi uvicorn[standard] 
poetry add pydantic sqlmodel passlib[bcrypt] python-jose[cryptography] 
poetry add pymysql 
poetry add redis
poetry add aioredis
```
## FastAPI

FastAPI es un framework web moderno y de alto rendimiento para construir APIs en Python, diseñado para ser rápido, intuitivo y fácil de usar, aprovechando al máximo las type hints de Python para ofrecer validación automática, documentación interactiva y desarrollo acelerado.  

🔧 Características principales de FastAPI

* Moderno y muy rápido: ofrece un rendimiento comparable a Node.js y Go gracias a su base en Starlette y Pydantic.  
* Basado en anotaciones de tipos de Python: esto permite validación automática, serialización y generación de documentación sin esfuerzo.  
* Con documentación interactiva automática: genera Swagger UI y ReDoc sin configuraciones adicionales.  
* Sencillo y rápido de desarrollar: reduce “errores humanos” y duplica la velocidad de desarrollo según sus creadores.  
* Compatible con estándares: utiliza OpenAPI y JSON Schema.  

Para más información (https://fastapi.tiangolo.com [fastapi.tiangolo.com])

## uvicorn

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

## pydantic  

Pydantic es una librería de Python que permite definir modelos de datos usando clases y anotaciones de tipo, y validar automáticamente que los datos cumplan esa estructura.  
En otras palabras: tú describes cómo deben ser tus datos, y Pydantic se asegura de que cualquier valor recibido coincida con ese esquema —corrigiendo tipos cuando puede o lanzando errores claros cuando no.

✨ Sus ideas clave


Validación automática basada en type hints de Python.
(Ej.: si un campo debe ser int y llega "3", lo convertirá a entero si es posible).  

Modelos como contratos de datos: defines clases heredando de BaseModel para describir entradas y salidas.

Conversión y parsing inteligente de datos provenientes de JSON, APIs u otras fuentes.

Muy usado en FastAPI, que lo integra nativamente para definir request/response models.

Rápido y robusto: su core está escrito en Rust, lo que lo hace una de las librerías de validación más veloces.

Para más información [Pydantic](https://docs.pydantic.dev/latest/)

## SQLModel

SQLModel es una librería de Python que permite definir modelos de base de datos usando clases tipadas, unificando en un solo lugar los conceptos de Pydantic y SQLAlchemy.  
Dicho de otra forma:  
👉 un mismo modelo sirve tanto para validar datos (Pydantic) como para mapear tablas de base de datos (ORM).

🔑 Ideas clave

1. Modelos únicos: una sola clase define:

    * la estructura de la tabla
    * la validación de datos
    * los esquemas de entrada/salida de la API

2. Basado en Pydantic
    * Hereda toda la validación, conversión de tipos y serialización de Pydantic.

3. Basado en SQLAlchemy  
    Usa SQLAlchemy por debajo para:

    - crear tablas
    - ejecutar consultas
    - manejar relaciones

4. Pensado para FastAPI  
    Es el ORM “natural” cuando quieres:

    - menos duplicación de código
    - modelos claros y tipados
    - APIs limpias y mantenibles

Para más información [SQLModel](https://sqlmodel.tiangolo.com/)


## passlib[bcrypt]

passlib[bcrypt] es una instalación de Passlib que incluye el soporte para el algoritmo de hashing BCrypt, uno de los métodos más seguros y recomendados para almacenar contraseñas en aplicaciones modernas.  
Passlib, por sí mismo, es una biblioteca de Python especializada en hashing de contraseñas, diseñada para gestionar de forma segura su generación, verificación y actualización. [certidevs.com]  
El extra [bcrypt] instala automáticamente las dependencias necesarias para utilizar BCrypt, un algoritmo robusto, lento a propósito y basado en Blowfish, pensado para resistir ataques de fuerza bruta. [passlib.re...thedocs.io]

🧩 ¿Qué aporta exactamente el extra [bcrypt]?

Soporte completo para BCrypt, uno de los algoritmos recomendados por Passlib para nuevas aplicaciones.  
Dependencias externas necesarias para que BCrypt funcione correctamente.  
La posibilidad de usar Passlib con un contexto de hashing configurado específicamente para BCrypt (como se muestra en guías reales de FastAPI).

## python-jose[cryptography] 

ython-jose[cryptography] es una librería de Python para crear, firmar, verificar y decodificar tokens JWT y otros objetos JOSE, utilizando primitivas criptográficas seguras.  
Se usa principalmente para autenticación y autorización, especialmente en APIs (por ejemplo con FastAPI).  

🧩 Desglose del nombre

* python-jose  
    Implementa los estándares JOSE:

    - JWT (JSON Web Token)
    - JWS (JSON Web Signature)
    - JWE (JSON Web Encryption)


[cryptography]  
    Instala el backend criptográfico basado en la librería cryptography, que aporta:  

    * algoritmos modernos y seguros
    * mejor rendimiento
    * soporte robusto para RSA, EC, HMAC, etc.

👉 Sin este extra, python-jose usa implementaciones más limitadas.

🔑 ¿Para qué se usa en la práctica?

Firmar tokens JWT al hacer login
Verificar tokens JWT en cada request
Gestionar expiración (exp), emisor (iss), audiencia (aud)
Implementar autenticación stateless en APIs

Es el complemento natural de passlib[bcrypt]:

* passlib[bcrypt] → protege contraseñas
* python-jose[cryptography] → protege tokens

## pymysql

PyMySQL es una librería escrita completamente en Python que permite conectarse y trabajar con bases de datos MySQL y MariaDB.  
Es un driver puro de Python, lo que significa que no necesita extensiones en C, a diferencia de MySQLdb, y por eso es más fácil de instalar y compatible con entornos como CPython, PyPy e IronPython.  

🔑 Características clave  

* Cliente MySQL/MariaDB 100% Python, basado en el estándar DB‑API 2.0 (PEP 249). [pypi.org]
* Compatible con versiones modernas de Python (3.x). [recursospython.com]

Permite:

* Conectarse a un servidor MySQL/MariaDB
* Ejecutar consultas SQL (SELECT, INSERT, UPDATE, etc.)
* Crear cursores y manejar resultados (fetchone, fetchall)
* Manejar transacciones (commit, rollback)

## redis

Redis es una base de datos en memoria, de tipo clave‑valor, extremadamente rápida, diseñada para almacenar y acceder a datos temporales con latencias muy bajas.  
Se utiliza principalmente como caché, almacén de sesiones, sistema de colas y motor de datos en tiempo real, complementando a bases de datos tradicionales como MySQL o PostgreSQL.  

🔑 Ideas clave en una frase

* Vive en RAM → muy rápido
* Modelo clave‑valor
* Ideal para datos temporales o de acceso frecuente
* No reemplaza a la base de datos principal, la complementa


## aioredis

aioredis es un cliente asíncrono de Redis para Python que permite interactuar con Redis de forma no bloqueante usando async/await.  
Está diseñado para integrarse perfectamente con frameworks asíncronos como FastAPI, aprovechando el event loop para manejar muchas operaciones Redis concurrentes sin bloquear la aplicación.  

🔑 Ideas clave

- Cliente Redis asíncrono
- Basado en asyncio
- Usa async / await
- Ideal para FastAPI y aplicaciones de alta concurrencia
- Permite operaciones Redis sin bloquear el servidor
