# Implementación test unitarios

## ¿que se necesita?

✔ pytest  
✔ pytest-asyncio  
✔ httpx (para tests del router, opcional)  
✔ una BBDD SQLite en memoria para los tests  
✔ crear y dropear tablas por test (fixture)  

## Estructura propuesta para los test

tests/
  conftest.py
  user/
    test_user_service.py
    test_user_router.py   (opcional, httpx)

## Dependencias

| Paquete | Para qué sirve                                        |
| ------- | ----------------------------------------------------- |
| pytest  | Framework principal de testing                        |
| pytest-asyncio | Ejecutar async def test...                     |
| httpx | Cliente HTTP async para testear FastAPI con AsyncClient |
| anyio | Backend async de FastAPI, httpx y pytest                |
| aiosqlite | Base de datos SQLite async en memoria para tests    |

En pyproject.toml:

```yml
[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
pytest-asyncio = "^0.23"
httpx = "^0.27"
anyio = "^4.0"
aiosqlite = "^0.19"
```

## ¿Qué cubre esto?

| Capa                | Testeado                           | Tipo        |
| ------------------- | ---------------------------------- | ----------- |
| UserService         | create, get, update, delete, roles | Unitario    | 
| Router/v1/user      | register/get/delete                | Itegración  |
| Base async SQLModel | Probado con SQLite                 | Infra       |

## Ejecutar los tests

```bash
poetry run pytest -v
```

Si quieres mostrar prints y logs:

```bash
poetry run pytest -v -s
```

Si quieres ejecutar solo tests del servicio:

```bash
poetry run pytest tests/user/test_user_service.py -v
```

Para ejecutar solo un test dentro del archivo.

```bash
poetry run pytest tests/user/test_user_router.py::test_router_register -v
```
