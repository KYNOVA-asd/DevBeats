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

En Windows tambien se puede abrir `DevBeats-Prueba-1.bat` con doble clic. El
archivo prepara el entorno cuando sea necesario y muestra un menu para crear,
revisar y construir canciones.

`abrir_app.bat` es el acceso directo de la prueba local. La opcion **Buscar
musica con Google IA** entrega una consulta al modo IA de Google en Edge. Su
comportamiento se configura en `devbeats.profile.yaml`; DevBeats solo abre la
busqueda y no extrae automaticamente contenido de la pagina.

Para cerrar el ciclo de investigacion y composicion se puede usar:

```powershell
python -m devbeats.main ai-plan "cancion de cuna espacial, muy tranquila"
```

Este comando utiliza la herramienta oficial Google Search de Gemini, valida el
plan recibido y genera `song.yaml`, `ai-plan.json`, `output.mid` y `output.mmp`.

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

