# Manual de operación: librería local + PyPI interno (devpi)

Flujo en serie para: iniciar el servidor de paquetes, publicar la librería,
y consumirla desde proyectos independientes. Sin Docker ni PyPI real.

```
lib repo ──devpi upload──▶ devpi-server ──pip install──▶ proyectos consumidores
```

---

## 0. PREREQUISITOS (una sola vez por máquina)

```bash
pip install devpi-server devpi-client
python -m build --version || pip install build
```

---

## 1. INICIAR EL SERVIDOR (una sola vez si es primera vez)

### 1a. Inicializar el almacenamiento (solo la primera vez)
```bash
devpi-init --serverdir C:/Development/devpi-home
```
Crea usuario `root` y el índice `root/pypi`. No se repite nunca sobre el
mismo `serverdir` (fallaría: "already initialized").

### 1b. Arrancar el servidor
```bash
devpi-server --serverdir C:/Development/devpi-home > devpi.log 2>&1 &
```
SMaria o background. Verificar:
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:3141/   # → 200
```

---

## 2. CREAR USUARIO E ÍNDICE (una sola vez por serverdir)

```bash
devpi use http://localhost:3141
devpi user -c team password=team123 email=team@local
devpi login team --password=team123
devpi index -c team/staging bases= volatile=True
```

**Importantísimo — `bases=` vacío:** si se agrega `bases=root/pypi`
devpi mirroriza pypi.org completo y los timeouts rompen la resolución.

---

## 3. PUBLICAR LA LIBRERÍA (cada release)

EN: repo `app-common-library`.

```bash
devpi use http://localhost:3141
devpi login team --password=team123
devpi use team/staging

# 1. subir versión en pyproject.toml (MAJOR.MINOR.PATCH)
# 2. limpiar artefactos viejos (subiría las dos versiones si no)
rm -rf dist build src/*.egg-info

# 3. construir + publicar
python -m build --wheel
devpi upload --from-dir dist

# 4. firmar el release en git
git tag vX.Y.Z -m "Release X.Y.Z"
git push origin main vX.Y.Z
```

Verificación: `curl http://localhost:3141/team/staging/+simple/app-common-library/`

---

## 4. CONSUMIR Y PROBAR (por proyecto, cuando se quiera actualizar)

EN: repo `web-consumer` (o el proyecto que sea).

```bash
cd web-consumer
python -m venv .venv
.venv\Scripts\Activate.ps1          # Unix: . en .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Cuando salga una versión nueva:
- siempre: `pip install --upgrade app-common-library`
- reproducible: bump del piso de versión en requirements.txt
  (`app-common-library>=1.0.3`) + commit.

---

## 5. CICLO PARA UN NUEVO CONSUMIDOR (un proyecto más)

```bash
cd al-nuevo-proyecto
python -m venv .venv && .venv\Scripts\Activate.ps1

# requirements.txt:
# --extra-index-url http://localhost:3141/team/staging/+simple/
# app-common-library>=1.0.2

pip install -r requirements.txt
```
No necesita clonar la librería ni acceso de escritura al servidor.

---

## 6. TROUBLESHOOTING

| Síntoma | Causa / solución |
|---|---|
| `WARNING: Location '.../requests/' is ignored` | **Normal.** devpi no tiene esos paquetes; pip los baja de PyPI real |
| `from versions: none` sin más info | Índice sin wheel publicado o wheel no publicado. Correr `curl` del paso 3 |
| `devpi-server: already initialized` | Reuso de serverdir; solo ejecutar `devpi-init` en dir nuevo |
| Puerto 3141 ocupado | Matar proceso viejo: `taskkill /F /IM devpi-server*` o usar `--port` |
| Server caído después de reiniciar PC | Repetir **solo paso 1b** (el estado persiste en `devpi-home`) |
| Resolución lentísima en install | El índice quedó con `bases=root/pypi`: `devpi index team/staging bases=` |
| Re-subida de misma versión | devpi la rechaza (hash distinto). Bump de versión SIEMPRE |

---

## 7. MEJORAS FUTURAS

- serverdir en ruta fija (no temp) + correr como servicio / autoarranque
- rotar password (hoy: `team123`)
- CI (`.github/workflows/publish.yml`): se activa al definir
  `gh variable set DEVPI_URL --body "https://host:3141/team/staging/"` + secrets
