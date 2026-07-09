import argparse
import csv
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = PROJECT_ROOT / 'data' / 'inputs' / 'exportify_playlist.csv'
DEFAULT_OUTPUT = PROJECT_ROOT / 'data' / 'inputs' / 'canciones_desde_exportify.txt'

METADATA_KEYWORDS = (
    'feat',
    'ft',
    'featuring',
    'from',
    'version',
    'remaster',
    'remastered',
    'live',
    'official',
    'audio',
    'video',
    'lyric',
    'soundtrack',
    'original motion picture soundtrack',
)

METADATA_PATTERN = re.compile('|'.join(re.escape(k) for k in METADATA_KEYWORDS), re.IGNORECASE)
BRACKETED_METADATA_PATTERN = re.compile(r'\s*[\[(]([^\])]+)[\])]')
FEAT_INLINE_PATTERN = re.compile(r'\s+(?:feat\.?|ft\.?)\s+.+$', re.IGNORECASE)
SEPARATOR_METADATA_PATTERN = re.compile(r'\s*[-–|:]\s*(.+)$')


def limpiar_titulo(titulo):
    limpio = titulo.strip()
    if not limpio:
        return ''

    # Elimina metadatos entre parentesis/corchetes solo cuando son de version/feat/live/etc.
    while True:
        match = BRACKETED_METADATA_PATTERN.search(limpio)
        if not match:
            break

        contenido = match.group(1)
        if METADATA_PATTERN.search(contenido):
            limpio = (limpio[:match.start()] + limpio[match.end():]).strip()
        else:
            break

    # Elimina "feat" en linea: "Cancion feat. Artista".
    limpio = FEAT_INLINE_PATTERN.sub('', limpio).strip()

    # Elimina sufijos despues de guion/separador solo si son metadatos.
    match = SEPARATOR_METADATA_PATTERN.search(limpio)
    if match and METADATA_PATTERN.search(match.group(1)):
        limpio = limpio[:match.start()].strip()

    limpio = re.sub(r'\s{2,}', ' ', limpio).strip(' -–|:')
    return limpio


def extraer_titulos(archivo_csv, columna='Track Name', unicos=False, limpiar=True):
    titulos = []
    vistos = set()

    with open(archivo_csv, 'r', encoding='utf-8-sig', newline='') as f:
        lector = csv.DictReader(f)

        if lector.fieldnames is None:
            raise ValueError('El CSV no contiene cabeceras.')

        if columna not in lector.fieldnames:
            disponibles = ', '.join(lector.fieldnames)
            raise ValueError(
                f"No se encontró la columna '{columna}'. Columnas disponibles: {disponibles}"
            )

        for fila in lector:
            titulo = (fila.get(columna) or '').strip()
            if not titulo:
                continue

            if limpiar:
                titulo = limpiar_titulo(titulo)
                if not titulo:
                    continue

            if unicos:
                if titulo in vistos:
                    continue
                vistos.add(titulo)

            titulos.append(titulo)

    return titulos


def guardar_titulos_txt(titulos, archivo_txt):
    with open(archivo_txt, 'w', encoding='utf-8', newline='\n') as f:
        for titulo in titulos:
            f.write(f'{titulo}\n')


def parse_args():
    parser = argparse.ArgumentParser(
        description='Convierte un CSV de Exportify en un TXT con un título por línea.'
    )
    parser.add_argument('--entrada-csv', default=str(DEFAULT_INPUT), help='Ruta al CSV exportado.')
    parser.add_argument('--salida-txt', default=str(DEFAULT_OUTPUT), help='Ruta del TXT de salida.')
    parser.add_argument(
        '--columna',
        default='Track Name',
        help='Nombre de la columna del título de canción en el CSV.',
    )
    parser.add_argument(
        '--unicos',
        action='store_true',
        help='Si se indica, elimina títulos repetidos manteniendo el primer orden.',
    )
    parser.add_argument(
        '--no-limpiar',
        action='store_true',
        help='Si se indica, no limpia metadatos del titulo (feat/version/live/oficial).',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    titulos = extraer_titulos(
        Path(args.entrada_csv),
        columna=args.columna,
        unicos=args.unicos,
        limpiar=not args.no_limpiar,
    )
    guardar_titulos_txt(titulos, Path(args.salida_txt))
    print(f'Se guardaron {len(titulos)} títulos en {args.salida_txt}')


if __name__ == '__main__':
    main()
