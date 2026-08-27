# Decisión 002 — La ubicación del corpus se recibe por configuración, no por código

**Fecha:** 26 de agosto de 2026
**Estado:** vigente
**Afecta a:** Etapa 0 · Etapa 1 (ingesta) · todo el motor · pruebas

---

## El problema

El motor tiene que leer archivos de video que viven **fuera del repositorio** (regla de
higiene 0.4 del plan: los videos no van a git). Hoy están en `~/kinetiq-data/`, pero:

- esa carpeta puede mudarse de lugar,
- otra persona que clone el repo la va a tener en otra ruta,
- en la máquina de CI no va a existir en absoluto.

Si la ruta queda escrita en el código, el motor solo funciona en la máquina donde se
escribió. Cualquier cambio de ubicación obliga a tocar y volver a commitear código.

---

## Alternativas consideradas

| Opción | Por qué no |
| --- | --- |
| Ruta fija en el código (`Path.home() / "kinetiq-data"`) | Rompe apenas la carpeta se mueve o se clona el repo en otro lado. Es exactamente lo que hay que evitar. |
| Pasar la ruta como argumento obligatorio a cada función del motor | Ensucia todas las firmas y traslada el problema a quien llama. Útil más adelante para tests puntuales, no como mecanismo principal. |
| Un `config.py` con la ruta escrita, ignorado por git | Funciona, pero no deja rastro de qué se espera configurar: quien clona no sabe que ese archivo tiene que existir. |
| **Variable de entorno + archivo `.env` de ejemplo versionado** | Estándar, explícito, y el `.env.example` documenta el contrato. Elegida. |

---

## Decisión

La ubicación del corpus se resuelve en `backend/app/config.py`, función `get_data_dir()`:

1. Lee la variable de entorno **`KINETIQ_DATA_DIR`**.
2. Si no está en el entorno del proceso, intenta leerla de `backend/.env`
   (con `python-dotenv`). `backend/.env` **no se versiona**.
3. Si no aparece por ninguna vía, **lanza `ConfigError` con un mensaje que dice cómo
   configurarla**. No hay valor por defecto.
4. La ruta obtenida se expande (`~`), se resuelve a absoluta y se verifica que exista
   antes de devolverla.

Se versiona `backend/.env.example` con la clave y un valor de muestra, como referencia
de qué hay que configurar.

**El motor recibe rutas de archivo ya resueltas.** `config.py` es la única pieza que sabe
de `KINETIQ_DATA_DIR`; las funciones de `engine/` siguen recibiendo un `Path` y
devolviendo estructuras de datos, sin leer configuración. Así el motor se puede ejercitar
desde un cuaderno pasándole cualquier ruta.

---

## Consecuencias

- El mismo código corre en cualquier máquina cambiando una línea de `backend/.env`.
- `kinetiq-data/` se puede mover sin tocar código.
- En CI se define la variable de entorno apuntando a un directorio de *fixtures*.
- Si falta la configuración, el sistema **falla de entrada y con un mensaje claro**, en
  lugar de adivinar una ruta y fallar más adentro con un error confuso. Es la lógica de la
  regla R3 del `CLAUDE.md` ("un dato faltante es mejor que un dato equivocado") aplicada a
  la configuración.
- La misma idea se reutiliza para futuras opciones dependientes de la máquina (rutas de
  modelos de pose, carpeta de salida de artefactos): todas por `config.py`.
