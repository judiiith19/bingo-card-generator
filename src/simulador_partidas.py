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
            cartones.append({'canciones': canciones, 'marcadas': set()})
    return cartones


def cargar_playlist(archivo_txt):
    with open(archivo_txt, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def contar_cartones_a_punto(cartones, canciones_por_carton=12):
    a_3 = a_2 = a_1 = 0
    for carton in cartones:
        faltan = canciones_por_carton - len(carton['marcadas'])
        if faltan == 3:
            a_3 += 1
        elif faltan == 2:
            a_2 += 1
        elif faltan == 1:
            a_1 += 1
    return a_3, a_2, a_1


def comprobar_bingo(cartones, i, cancion):
    ganadores = []
    for idx, carton in enumerate(cartones):
        if len(carton['marcadas']) == len(carton['canciones']):
            ganadores.append(idx + 1)

    if ganadores:
        print(f"\nBINGO: {len(ganadores)} cartón(es) han cantado bingo en el minuto {i} con '{cancion}'")
        print(f"Cartones ganadores: {', '.join(map(str, ganadores))}")
        return True
    return False


def simular_bingo(cartones, playlist, canciones_por_carton=12):
    for i, cancion in enumerate(playlist, start=1):
        cartones_con_cancion = []
        for idx, carton in enumerate(cartones):
            if cancion in carton['canciones']:
                carton['marcadas'].add(cancion)
                cartones_con_cancion.append(idx + 1)

        print(f"\nMinuto {i} - Suena: '{cancion}'")
        if cartones_con_cancion:
            print(f"Marcado en cartón(es): {', '.join(map(str, cartones_con_cancion))}")
        else:
            print('Ningún cartón la tenía')

        a_3, a_2, a_1 = contar_cartones_a_punto(cartones, canciones_por_carton=canciones_por_carton)
        print(f"A 3 del bingo: {a_3} | A 2: {a_2} | A 1: {a_1}")

        if comprobar_bingo(cartones, i, cancion):
            return

    print('\nFinal de playlist: no se ha cantado bingo.')


def parse_args():
    parser = argparse.ArgumentParser(description='Simula una partida de bingo musical.')
    parser.add_argument('--cartones', default=str(DEFAULT_CARTONES), help='CSV con los cartones generados.')
    parser.add_argument('--playlist', default=str(DEFAULT_PLAYLIST), help='TXT con la lista de canciones.')
    parser.add_argument('--canciones-por-carton', type=int, default=12, help='Número de canciones por cartón.')
    return parser.parse_args()


def main():
    args = parse_args()
    cartones = cargar_cartones(Path(args.cartones))
    playlist = cargar_playlist(Path(args.playlist))
    simular_bingo(cartones, playlist, canciones_por_carton=args.canciones_por_carton)


if __name__ == '__main__':
    main()
