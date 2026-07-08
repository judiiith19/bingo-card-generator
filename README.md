# Bingo Generator

Herramientas en Python para generar cartones de bingo musical y simular partidas a partir de una playlist.

## Estructura

- `src/`: lógica principal del proyecto.
- `data/inputs/`: listas TXT de canciones.
- `data/outputs/`: CSV generados o ejemplos de cartones.
- `generador_csv_cartones.py` y `simulador_partidas.py`: lanzadores en la raíz para no romper el uso actual.

## Requisitos

- Python 3.10 o superior.
- No necesita librerías externas.

## Uso rápido

Generar cartones:

```bash
python generador_csv_cartones.py --entrada data/inputs/canciones1_115.txt --salida data/outputs/cartones_optimizados1_115.csv
```

Simular una partida:

```bash
python simulador_partidas.py --cartones data/outputs/cartones_optimizados2_105.csv --playlist data/inputs/canciones2_115.txt
```

## Opciones disponibles

### Generador

```bash
python generador_csv_cartones.py --help
```

Parámetros principales:

- `--entrada`: archivo TXT con una canción por línea.
- `--salida`: archivo CSV de salida.
- `--num-cartones`: cantidad de cartones a generar.
- `--canciones-por-carton`: número de canciones por cartón.
- `--max-coincidencias`: máximo de canciones compartidas entre cartones.
- `--seed`: semilla opcional para reproducibilidad.

### Simulador

```bash
python simulador_partidas.py --help
```

Parámetros principales:

- `--cartones`: CSV con los cartones generados.
- `--playlist`: TXT con la lista de canciones.
- `--canciones-por-carton`: número de canciones esperadas por cartón.

## Flujo recomendado

1. Coloca tus playlists en `data/inputs/`.
2. Genera los cartones en `data/outputs/`.
3. Usa el CSV resultante en el simulador para probar una partida.

## Notas

- El generador intenta mantener una separación razonable entre cartones, pero si los parámetros son muy exigentes puede devolver menos cartones de los pedidos.
- Si quieres publicar esto como proyecto reutilizable, el siguiente paso lógico sería añadir una licencia abierta como MIT o Apache 2.0.
