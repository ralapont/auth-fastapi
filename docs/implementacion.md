# Implementación del Servicio de Gestion de usuarios

Lo que hemos dejado funcionando

GET / y GET /{id} con carga eager (roles → scopes) evitando MissingGreenlet.
POST /register devolviendo el usuario creado con get_user_by_id.
PUT /users/{id} sin tocar contraseña, con semántica:

roles omitido → no tocar,
roles: [] → vaciar,
roles: ["…"] → reemplazar (delete+insert en UserRole).


DELETE /users/{id} con limpieza automática (vía cascade o borrado explícito de UserRole).

Pequeño checklist para mantenerlo estable

En modelos:

User.user_roles: cascade="all, delete-orphan", lazy="selectin".
User.roles y Role.scopes: lazy="selectin" (o joinedload en consultas puntuales).


En servicio:

Tras escribir, reconsulta con eager y devuelve UserOut ya construido (Pydantic v2 con from_attributes=True).
Si no tienes middleware de UoW, recuerda await session.commit() donde corresponda.


En esquemas Pydantic:

UserOut, RoleOut, RoleScopeOut con model_config = ConfigDict(from_attributes=True).



Cuando quieras, otro día preparamos los tests unitarios/funcionales (pytest + httpx):

Casos PUT (roles omitido / vacío / reemplazo),
DELETE 204 y cascada,
Validaciones 404/409,
Y algún happy path de creación y lectura.