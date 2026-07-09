# Bingo Generator

Proyecto para preparar bingos musicales de principio a fin:

1. Exportar una playlist de Spotify en CSV (Exportify).
2. Convertir ese CSV a TXT con un titulo por linea.
3. Generar cartones optimizados en CSV.
4. Simular partidas en consola.
5. Renderizar cartones visuales en Google Sheets para imprimir.

## Estructura

- [src/](src/): logica principal en Python.
- [data/inputs/](data/inputs/): playlists en TXT y CSV de entrada.
- [data/outputs/](data/outputs/): cartones generados en CSV.
- [google-sheets/generadorCartonesBingo.gs](google-sheets/generadorCartonesBingo.gs): script de Apps Script para dibujar cartones visuales.
- [menu_bingo.py](menu_bingo.py): menu interactivo para gestionar todo el flujo Python.
- [bingo_config.example.json](bingo_config.example.json): plantilla de configuracion del menu interactivo.
- [exportify_to_txt.py](exportify_to_txt.py), [generador_csv_cartones.py](generador_csv_cartones.py), [simulador_partidas.py](simulador_partidas.py): lanzadores directos en la raiz.

## Requisitos

- Python 3.10 o superior.
- Sin dependencias externas.

## Flujo Completo

### Opcion recomendada: menu interactivo

```bash
python menu_bingo.py
```

Tambien puedes usar el lanzador con flags:

```bash
python menu_bingo.py --help
python menu_bingo.py --version
python menu_bingo.py --config bingo_config.json
python menu_bingo.py --run-full
```

Desde ahi puedes:

1. Ejecutar flujo completo (Exportify -> Cartones -> Simulacion).
2. Convertir CSV de Exportify a TXT.
3. Generar cartones.
4. Simular partida.
5. Ver/editar/restablecer configuracion.

El menu guarda tu configuracion local en `bingo_config.json` (archivo ignorado por Git).
La plantilla versionada del repo esta en [bingo_config.example.json](bingo_config.example.json).

Si el `bingo_config.json` se corrompe, el menu crea un backup `.bak` automaticamente y regenera configuracion valida.

### 1) Exportar playlist desde Spotify

Usa Exportify: [https://exportify.net/](https://exportify.net/)

Guarda el CSV en [data/inputs/](data/inputs/) por ejemplo como `BINGO_RONDA_1.csv`.

### 2) Convertir CSV de Exportify a TXT

Comando recomendado:

```bash
python exportify_to_txt.py --entrada-csv "data/inputs/BINGO_RONDA_1.csv" --salida-txt "data/inputs/canciones_ronda_1.txt" --unicos
```

Este script extrae la columna `Track Name` y genera un TXT con un titulo por linea.

### 3) Generar cartones optimizados

```bash
python generador_csv_cartones.py --entrada data/inputs/canciones_ronda_1.txt --salida data/outputs/cartones_ronda_1.csv --num-cartones 100 --canciones-por-carton 12 --max-coincidencias 3
```

### 4) Simular la partida

```bash
python simulador_partidas.py --cartones data/outputs/cartones_ronda_1.csv --playlist data/inputs/canciones_ronda_1.txt --canciones-por-carton 12
```

### 5) Pasar los cartones a formato visual (Google Sheets)

Puedes usar la siguiente plantilla de Google Sheets:
👉 [CONSEGUIR PLANTILLA DE GOOGLE SHEETS](https://docs.google.com/spreadsheets/d/1ieuiieDqshKL-2PPijxsN29i8oCbGnWKbDt6Y-lMgmg/copy)

Pasos:

1. Abre tu copia de la plantilla.
2. Ve a la hoja Cartones texto.
3. Importa el CSV generado en Python (Archivo > Importar) y elige Reemplazar hoja actual.
4. Ejecuta el menu Gestion Cartones Bingo > Generar Cartones Visuales.

Si quieres mantener el script tambien versionado localmente, esta en [google-sheets/generadorCartonesBingo.gs](google-sheets/generadorCartonesBingo.gs).

Si en tu copia no aparece el menu:

1. Abre Extensiones > Apps Script.
2. Pega el contenido de [google-sheets/generadorCartonesBingo.gs](google-sheets/generadorCartonesBingo.gs) en el editor.
3. Guarda, recarga la hoja y vuelve a ejecutar desde el menu.

## Comandos Rapidos

```bash
python menu_bingo.py
python exportify_to_txt.py --help
python generador_csv_cartones.py --help
python simulador_partidas.py --help
python -m unittest discover -s tests -p "test_*.py" -v
```

## Calidad

- El repo incluye tests unitarios en [tests/](tests/).
- CI en GitHub Actions: [.github/workflows/ci.yml](.github/workflows/ci.yml).
- Verificacion local recomendada:

```bash
python -m py_compile menu_bingo.py src/exportify_to_txt.py src/generador_csv_cartones.py src/simulador_partidas.py src/menu_interactivo.py
python -m unittest discover -s tests -p "test_*.py" -v
```

## Opciones Principales

### exportify_to_txt.py

- `--entrada-csv`: ruta del CSV exportado.
- `--salida-txt`: ruta del TXT de salida.
- `--columna`: columna de donde leer el titulo (por defecto `Track Name`).
- `--unicos`: elimina repetidos conservando orden.

### generador_csv_cartones.py

- `--entrada`: TXT con una cancion por linea.
- `--salida`: CSV de cartones.
- `--num-cartones`: cantidad de cartones.
- `--canciones-por-carton`: canciones por carton.
- `--max-coincidencias`: limite de coincidencias entre cartones.
- `--seed`: semilla opcional para reproducibilidad.

### simulador_partidas.py

- `--cartones`: CSV con cartones.
- `--playlist`: TXT con canciones a sonar.
- `--canciones-por-carton`: canciones esperadas por carton.

## Notas

- Si la config del generador es muy exigente, puede devolver menos cartones de los pedidos.
- Recomendacion para publicar el repo: anadir licencia MIT o Apache-2.0.

## Presets Recomendados

Usa estos presets como punto de partida segun el tipo de evento:

- Rapido: `--canciones-por-carton 10 --max-coincidencias 4`
- Equilibrado: `--canciones-por-carton 12 --max-coincidencias 3`
- Conservador: `--canciones-por-carton 13 --max-coincidencias 2`

Para rondas grandes (150 cartones o mas), empieza por el preset conservador.

## Troubleshooting

- Error `No se pudo exportar porque no se generó ningún cartón`:
	- Reduce `--num-cartones`.
	- Sube `--max-coincidencias`.
	- Usa una playlist con mas canciones unicas.
- El menu no arranca por `bingo_config.json` invalido:
	- Se crea un backup `.bak` automatico.
	- Revisa el backup y vuelve a lanzar `python menu_bingo.py`.
- `menu_bingo.py --help` no funciona:
	- Verifica que ejecutas desde la raiz del repo.
	- Comprueba sintaxis con `python -m py_compile menu_bingo.py src/menu_interactivo.py`.
- El simulador termina demasiado pronto:
	- Incrementa `--canciones-por-carton`.
	- Reduce `--max-coincidencias` al generar cartones.
