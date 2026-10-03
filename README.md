# app-common-library

Librería de utilidades comunes, mantenida por un equipo y consumida por varios proyectos independientes.

## Instalación

```bash
pip install app-common-library
```

## Uso

```python
from app_common_library.utils import obtener_status_red

print(obtener_status_red())
```

## Desarrollo

```bash
python -m build
devpi upload  # o twine upload dist/...
```
