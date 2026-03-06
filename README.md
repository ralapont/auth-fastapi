# Servicio de Autenticación y Autorización centralizada en FastAPI

Un sistema de autenticación y autorización centralizada es un modelo en el que un único servicio se encarga de gestionar:

Autenticación (AuthN) → verificar quién eres
Autorización (AuthZ) → verificar qué puedes hacer

En lugar de que cada aplicación implemente su propio mecanismo de login, roles o permisos, todas delegan estas funciones en un servicio central, como:

Un Auth Service (microservicios)
Un Identity Provider (IdP) como Keycloak, Auth0, Azure AD, etc.
Un API Gateway que valida tokens y controla accesos

Esto permite que todas las aplicaciones y microservicios compartan un único modelo de identidad y acceso.

El Auth Service:

Gestiona el login
Emite y valida tokens JWT
Mantiene usuarios, roles, políticas de acceso

🎯 Beneficios principales

✔️ Consistencia:  
    Todos los sistemas aplican la misma política de acceso.  
✔️ Seguridad mejorada:  
    Control centralizado de:

* contraseñas
* roles
* permisos
* tokens
* políticas de bloqueo

✔️ Escalabilidad  
Nuevos servicios pueden conectarse fácilmente sin reimplementar autenticación.  
✔️ Mantenimiento más simple  
Cambio de reglas, roles o métodos de autenticación → un único lugar.  

🏗️ Componentes típicos

1. Identity Provider (IdP) / Auth Service

* Login, logout
* Gestión de usuarios y roles
* Emisión de tokens JWT/u otros

2. Aplicaciones / Microservicios

* Reciben peticiones ya autenticadas
* Se limitan a comprobar claims del token (si es necesario)

3. Base de datos central

* Usuarios, roles, intentos fallidos, lockouts

Para la implantación del servicio vamos a segir lo siguiente:

* [Creación del proyecto con poetry](docs/creacionProyecto.md)
* [Añadir las dependencias del proyecto](docs/dependencias.md)
* [Diseño datos](docs/diseño_datos.md)
* [Diseño físico de datos](docs/diseño_fisico.md)