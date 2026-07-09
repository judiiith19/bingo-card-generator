import argparse
import csv
import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = PROJECT_ROOT / 'data' / 'inputs' / 'canciones1_115.txt'
DEFAULT_OUTPUT = PROJECT_ROOT / 'data' / 'outputs' / 'cartones_optimizados1_115.csv'


def cargar_canciones(archivo_txt):
    with open(archivo_txt, encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def generar_cartones_optimizados(canciones, num_cartones, canciones_por_carton=12, max_coincidencias=3, seed=None):
    if len(canciones) < canciones_por_carton:
        raise ValueError('Muy pocas canciones en la lista para generar cartones.')

    if seed is not None:
        random.seed(seed)

    cartones = []
    cartones_como_conjunto = []

    intentos_maximos = 10000
    intentos = 0

    while len(cartones) < num_cartones and intentos < intentos_maximos:
        nuevo_carton = random.sample(canciones, canciones_por_carton)
        nuevo_carton_set = set(nuevo_carton)

        if any(nuevo_carton_set == carton_set for carton_set in cartones_como_conjunto):
            intentos += 1
            continue

        coincidencias = [len(nuevo_carton_set & carton_set) for carton_set in cartones_como_conjunto]
        if all(coincidencia <= max_coincidencias for coincidencia in coincidencias):
            cartones.append(nuevo_carton)
            cartones_como_conjunto.append(nuevo_carton_set)
            intentos = 0
        else:
            intentos += 1

    if len(cartones) < num_cartones:
        print(f'Aviso: solo se pudieron generar {len(cartones)} cartones con ese nivel de separación.')

    return cartones


def exportar_a_csv(cartones, archivo):
    if not cartones:
        raise ValueError(
            'No se pudo exportar porque no se generó ningún cartón. '
            'Prueba con menos cartones, más canciones por playlist o mayor max_coincidencias.'
        )

    with open(archivo, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([f'Canción {i + 1}' for i in range(len(cartones[0]))])
        writer.writerows(cartones)


def parse_args():
    parser = argparse.ArgumentParser(description='Genera cartones de bingo musical en CSV.')
    parser.add_argument('--entrada', default=str(DEFAULT_INPUT), help='Archivo TXT con una canción por línea.')
    parser.add_argument('--salida', default=str(DEFAULT_OUTPUT), help='Archivo CSV de salida.')
    parser.add_argument('--num-cartones', type=int, default=150, help='Cantidad de cartones a generar.')
    parser.add_argument('--canciones-por-carton', type=int, default=12, help='Número de canciones por cartón.')
    parser.add_argument('--max-coincidencias', type=int, default=3, help='Máximo de canciones compartidas entre cartones.')
    parser.add_argument('--seed', type=int, default=None, help='Semilla opcional para reproducibilidad.')
    return parser.parse_args()


def main():
    args = parse_args()
    canciones = cargar_canciones(Path(args.entrada))
    cartones = generar_cartones_optimizados(
        canciones,
        num_cartones=args.num_cartones,
        canciones_por_carton=args.canciones_por_carton,
        max_coincidencias=args.max_coincidencias,
        seed=args.seed,
    )
    exportar_a_csv(cartones, Path(args.salida))
    print(f'Cartones guardados en {args.salida}')


if __name__ == '__main__':
    main()
