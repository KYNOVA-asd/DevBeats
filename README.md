# DevBeats

DevBeats es una herramienta de **musica como codigo** para crear canciones de
cuna en MIDI y continuar su produccion en LMMS. Su arquitectura separa la CLI,
el nucleo musical y los adaptadores de salida.

## Instalacion

```powershell
python -m pip install -e ".[dev]"
```

## Primer uso

Desde la raiz del repositorio:

```powershell
python -m devbeats.main new "CancionBebe"
python -m devbeats.main build
```

El primer comando crea `CancionBebe/song.yaml` y registra ese directorio como
proyecto activo. `build` genera `CancionBebe/output.mid` y
`CancionBebe/output.mmp`. Tambien se puede indicar un proyecto explicitamente:

```powershell
python -m devbeats.main build --project canciones/mi-cancion
python -m devbeats.main status
python -m devbeats.main export --format midi
```

Abre LMMS y usa **Proyecto > Importar** para cargar `output.mid`. El archivo
`output.mmp` es una representacion XML experimental y deliberadamente sencilla.

## Arquitectura

```text
devbeats.main / devbeats.cli  ->  devbeats.core  ->  devbeats.adapters
```

- `cli`: experiencia de terminal y resolucion del proyecto activo.
- `core`: modelos, teoria musical y generacion; no conoce MIDI ni LMMS.
- `adapters`: traduce el modelo de dominio a formatos externos.

