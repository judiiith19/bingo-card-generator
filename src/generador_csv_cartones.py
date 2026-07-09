import argparse
import csv
import random
from pathlib import Path

from src.simulador_partidas import simular_bingo

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = PROJECT_ROOT / 'data' / 'inputs' / 'canciones1_115.txt'
DEFAULT_OUTPUT = PROJECT_ROOT / 'data' / 'outputs' / 'cartones_optimizados1_115.csv'


def cargar_canciones(archivo_txt):
    with open(archivo_txt, encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def _generar_lote_cartones(canciones, num_cartones, canciones_por_carton, max_coincidencias, rng):
    cartones = []
    cartones_como_conjunto = []

    intentos_maximos = 10000
    intentos = 0

    while len(cartones) < num_cartones and intentos < intentos_maximos:
        nuevo_carton = rng.sample(canciones, canciones_por_carton)
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

    return cartones


def _estado_para_simulacion(cartones):
    return [
        {'canciones': set(carton), 'marcadas': set(), 'linea_cantada': False, 'bingo_cantado': False}
        for carton in cartones
    ]


def puntuar_premios_simultaneos(reporte, peso_linea_simultanea=10, peso_bingo_simultaneo=1000):
    score = 0
    lineas_simultaneas = 0
    bingos_simultaneos = 0
    max_lineas_en_un_minuto = 0
    max_bingos_en_un_minuto = 0

    for evento in reporte.get('lineas', []):
        cantidad = len(evento.get('cartones', []))
        if cantidad > 1:
            lineas_simultaneas += 1
            max_lineas_en_un_minuto = max(max_lineas_en_un_minuto, cantidad)
            score += (cantidad - 1) * peso_linea_simultanea

    for evento in reporte.get('bingos', []):
        cantidad = len(evento.get('cartones', []))
        if cantidad > 1:
            bingos_simultaneos += 1
            max_bingos_en_un_minuto = max(max_bingos_en_un_minuto, cantidad)
            score += (cantidad - 1) * peso_bingo_simultaneo

    return score, {
        'lineas_simultaneas': lineas_simultaneas,
        'bingos_simultaneos': bingos_simultaneos,
        'max_lineas_en_un_minuto': max_lineas_en_un_minuto,
        'max_bingos_en_un_minuto': max_bingos_en_un_minuto,
    }


def generar_cartones_optimizados(
    canciones,
    num_cartones,
    canciones_por_carton=12,
    max_coincidencias=3,
    seed=None,
    playlist_referencia=None,
    canciones_por_linea=4,
    intentos_optimizacion=1,
    peso_linea_simultanea=10,
    peso_bingo_simultaneo=1000,
):
    if len(canciones) < canciones_por_carton:
        raise ValueError('Muy pocas canciones en la lista para generar cartones.')

    if intentos_optimizacion < 1:
        raise ValueError('intentos_optimizacion debe ser >= 1.')

    rng_base = random.Random(seed)

    # Si no hay playlist de referencia, se mantiene el comportamiento clásico.
    if not playlist_referencia:
        cartones = _generar_lote_cartones(canciones, num_cartones, canciones_por_carton, max_coincidencias, rng_base)
        if len(cartones) < num_cartones:
            print(f'Aviso: solo se pudieron generar {len(cartones)} cartones con ese nivel de separación.')
        return cartones

    mejor_cartonera = []
    mejor_score = None
    mejor_resumen = None

    for _ in range(intentos_optimizacion):
        seed_intento = rng_base.randint(0, 2**31 - 1)
        rng_intento = random.Random(seed_intento)
        cartones = _generar_lote_cartones(canciones, num_cartones, canciones_por_carton, max_coincidencias, rng_intento)
        if not cartones:
            continue

        reporte = simular_bingo(
            _estado_para_simulacion(cartones),
            playlist_referencia,
            canciones_por_carton=canciones_por_carton,
            canciones_por_linea=canciones_por_linea,
            mostrar_detalle=False,
        )
        score, resumen = puntuar_premios_simultaneos(
            reporte,
            peso_linea_simultanea=peso_linea_simultanea,
            peso_bingo_simultaneo=peso_bingo_simultaneo,
        )

        if mejor_score is None or score < mejor_score:
            mejor_score = score
            mejor_cartonera = cartones
            mejor_resumen = resumen

    if not mejor_cartonera:
        return []

    if len(mejor_cartonera) < num_cartones:
        print(f'Aviso: solo se pudieron generar {len(mejor_cartonera)} cartones con ese nivel de separación.')

    if mejor_resumen is not None and intentos_optimizacion > 1:
        print(
            'Optimizacion por simulacion: '
            f"score={mejor_score}, "
            f"lineas_simultaneas={mejor_resumen['lineas_simultaneas']}, "
            f"bingos_simultaneos={mejor_resumen['bingos_simultaneos']}, "
            f"max_lineas_minuto={mejor_resumen['max_lineas_en_un_minuto']}, "
            f"max_bingos_minuto={mejor_resumen['max_bingos_en_un_minuto']}"
        )

    return mejor_cartonera


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
    parser.add_argument('--playlist-referencia', default='', help='TXT de playlist para optimizar premios simultáneos.')
    parser.add_argument('--canciones-por-linea', type=int, default=4, help='Canciones marcadas para considerar línea.')
    parser.add_argument('--intentos-optimizacion', type=int, default=1, help='Número de intentos para elegir la mejor cartonera.')
    parser.add_argument('--peso-linea-simultanea', type=int, default=10, help='Penalización por líneas simultáneas.')
    parser.add_argument('--peso-bingo-simultaneo', type=int, default=1000, help='Penalización por bingos simultáneos.')
    return parser.parse_args()


def main():
    args = parse_args()
    canciones = cargar_canciones(Path(args.entrada))
    playlist_referencia = None
    if args.playlist_referencia:
        playlist_referencia = cargar_canciones(Path(args.playlist_referencia))

    cartones = generar_cartones_optimizados(
        canciones,
        num_cartones=args.num_cartones,
        canciones_por_carton=args.canciones_por_carton,
        max_coincidencias=args.max_coincidencias,
        seed=args.seed,
        playlist_referencia=playlist_referencia,
        canciones_por_linea=args.canciones_por_linea,
        intentos_optimizacion=args.intentos_optimizacion,
        peso_linea_simultanea=args.peso_linea_simultanea,
        peso_bingo_simultaneo=args.peso_bingo_simultaneo,
    )
    exportar_a_csv(cartones, Path(args.salida))
    print(f'Cartones guardados en {args.salida}')


if __name__ == '__main__':
    main()
