import argparse
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CARTONES = PROJECT_ROOT / 'data' / 'outputs' / 'cartones_optimizados2_105.csv'
DEFAULT_PLAYLIST = PROJECT_ROOT / 'data' / 'inputs' / 'canciones2_115.txt'


def cargar_cartones(archivo_csv):
    cartones = []
    with open(archivo_csv, 'r', encoding='utf-8') as f:
        lector = csv.reader(f)
        next(lector)
        for fila in lector:
            canciones = {c.strip() for c in fila if c.strip()}
            cartones.append({'canciones': canciones, 'marcadas': set(), 'linea_cantada': False, 'bingo_cantado': False})
    return cartones


def cargar_playlist(archivo_txt):
    with open(archivo_txt, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def contar_cartones_a_punto(cartones, canciones_por_carton=12):
    a_3 = a_2 = a_1 = 0
    for carton in cartones:
        objetivo = len(carton['canciones']) if carton.get('canciones') else canciones_por_carton
        faltan = objetivo - len(carton['marcadas'])
        if faltan == 3:
            a_3 += 1
        elif faltan == 2:
            a_2 += 1
        elif faltan == 1:
            a_1 += 1
    return a_3, a_2, a_1
def contar_cartones_a_linea(cartones, canciones_por_linea=4):
    a_3 = a_2 = a_1 = 0
    for carton in cartones:
        if carton.get('linea_cantada'):
            continue

        faltan = canciones_por_linea - len(carton['marcadas'])
        if faltan == 3:
            a_3 += 1
        elif faltan == 2:
            a_2 += 1
        elif faltan == 1:
            a_1 += 1
    return a_3, a_2, a_1


def _normalizar_canciones_por_linea(canciones_por_linea, canciones_por_carton):
    if canciones_por_linea is None:
        return max(1, canciones_por_carton // 3)

    if canciones_por_linea < 1:
        raise ValueError('El numero de canciones por linea debe ser al menos 1.')
    if canciones_por_linea > canciones_por_carton:
        raise ValueError('El numero de canciones por linea no puede superar el tamano del carton.')
    return canciones_por_linea


def simular_bingo(cartones, playlist, canciones_por_carton=12, canciones_por_linea=None, mostrar_detalle=True):
    canciones_por_linea = _normalizar_canciones_por_linea(canciones_por_linea, canciones_por_carton)
    reporte = {'lineas': [], 'bingos': [], 'canciones_por_linea': canciones_por_linea}

    for i, cancion in enumerate(playlist, start=1):
        cartones_con_cancion = []
        cartones_con_linea = []
        cartones_con_bingo = []

        for idx, carton in enumerate(cartones):
            if cancion in carton['canciones']:
                carton['marcadas'].add(cancion)
                cartones_con_cancion.append(idx + 1)

        for idx, carton in enumerate(cartones):
            marcadas = len(carton['marcadas'])
            total_canciones = len(carton['canciones'])

            if not carton.get('linea_cantada') and marcadas >= canciones_por_linea:
                carton['linea_cantada'] = True
                cartones_con_linea.append(idx + 1)

            if not carton.get('bingo_cantado') and marcadas == total_canciones:
                carton['bingo_cantado'] = True
                cartones_con_bingo.append(idx + 1)

        if mostrar_detalle:
            print(f"\nMinuto {i} - Suena: '{cancion}'")
            if cartones_con_cancion:
                print(f"Marcado en cartón(es): {', '.join(map(str, cartones_con_cancion))}")
            else:
                print('Ningún cartón la tenía')

        a_3_linea, a_2_linea, a_1_linea = contar_cartones_a_linea(cartones, canciones_por_linea=canciones_por_linea)
        if mostrar_detalle:
            print(f"A 3 de línea: {a_3_linea} | A 2: {a_2_linea} | A 1: {a_1_linea}")

        a_3_bingo, a_2_bingo, a_1_bingo = contar_cartones_a_punto(cartones, canciones_por_carton=canciones_por_carton)
        if mostrar_detalle:
            print(f"A 3 del bingo: {a_3_bingo} | A 2: {a_2_bingo} | A 1: {a_1_bingo}")

        if cartones_con_linea:
            if mostrar_detalle:
                print(f"LINEA: {len(cartones_con_linea)} cartón(es) han cantado linea en el minuto {i} con '{cancion}'")
                print(f"Cartones con linea: {', '.join(map(str, cartones_con_linea))}")
            reporte['lineas'].append({'minuto': i, 'cancion': cancion, 'cartones': cartones_con_linea})

        if cartones_con_bingo:
            if mostrar_detalle:
                print(f"BINGO: {len(cartones_con_bingo)} cartón(es) han cantado bingo en el minuto {i} con '{cancion}'")
                print(f"Cartones ganadores: {', '.join(map(str, cartones_con_bingo))}")
            reporte['bingos'].append({'minuto': i, 'cancion': cancion, 'cartones': cartones_con_bingo})
            return reporte

    if mostrar_detalle:
        print('\nFinal de playlist: no se ha cantado bingo.')
    return reporte


def parse_args():
    parser = argparse.ArgumentParser(description='Simula una partida de bingo musical.')
    parser.add_argument('--cartones', default=str(DEFAULT_CARTONES), help='CSV con los cartones generados.')
    parser.add_argument('--playlist', default=str(DEFAULT_PLAYLIST), help='TXT con la lista de canciones.')
    parser.add_argument('--canciones-por-carton', type=int, default=12, help='Número de canciones por cartón.')
    parser.add_argument('--canciones-por-linea', type=int, default=None, help='Número de canciones marcadas para cantar línea.')
    return parser.parse_args()


def main():
    args = parse_args()
    cartones = cargar_cartones(Path(args.cartones))
    playlist = cargar_playlist(Path(args.playlist))
    canciones_por_linea = args.canciones_por_linea
    if canciones_por_linea is None:
        canciones_por_linea = int(input('Canciones necesarias para linea [4]: ').strip() or '4')
    simular_bingo(
        cartones,
        playlist,
        canciones_por_carton=args.canciones_por_carton,
        canciones_por_linea=canciones_por_linea,
    )


if __name__ == '__main__':
    main()
