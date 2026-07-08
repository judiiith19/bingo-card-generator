import json
from pathlib import Path

from src.exportify_to_txt import (
    DEFAULT_INPUT as DEFAULT_EXPORTIFY_INPUT,
    DEFAULT_OUTPUT as DEFAULT_EXPORTIFY_OUTPUT,
    extraer_titulos,
    guardar_titulos_txt,
)
from src.generador_csv_cartones import (
    DEFAULT_INPUT as DEFAULT_CANCIONES_INPUT,
    DEFAULT_OUTPUT as DEFAULT_CARTONES_OUTPUT,
    cargar_canciones,
    exportar_a_csv,
    generar_cartones_optimizados,
)
from src.simulador_partidas import (
    DEFAULT_CARTONES as DEFAULT_SIM_CARTONES,
    DEFAULT_PLAYLIST as DEFAULT_SIM_PLAYLIST,
    cargar_cartones,
    cargar_playlist,
    simular_bingo,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / 'bingo_config.json'


def _a_ruta_relativa_proyecto(path_value):
    path_obj = Path(path_value)
    try:
        return str(path_obj.relative_to(PROJECT_ROOT)).replace('\\', '/')
    except ValueError:
        return str(path_obj).replace('\\', '/')

DEFAULT_CONFIG = {
    'exportify_input_csv': _a_ruta_relativa_proyecto(DEFAULT_EXPORTIFY_INPUT),
    'exportify_output_txt': _a_ruta_relativa_proyecto(DEFAULT_EXPORTIFY_OUTPUT),
    'exportify_column': 'Track Name',
    'exportify_unique': True,
    'generator_input_txt': _a_ruta_relativa_proyecto(DEFAULT_CANCIONES_INPUT),
    'generator_output_csv': _a_ruta_relativa_proyecto(DEFAULT_CARTONES_OUTPUT),
    'generator_num_cartones': 150,
    'generator_canciones_por_carton': 12,
    'generator_max_coincidencias': 3,
    'generator_seed': '',
    'simulator_cartones_csv': _a_ruta_relativa_proyecto(DEFAULT_SIM_CARTONES),
    'simulator_playlist_txt': _a_ruta_relativa_proyecto(DEFAULT_SIM_PLAYLIST),
    'simulator_canciones_por_carton': 12,
}


def _cargar_config():
    if not CONFIG_PATH.exists():
        _guardar_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)

    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)

    merged = dict(DEFAULT_CONFIG)
    merged.update(config)
    return merged


def _guardar_config(config):
    with open(CONFIG_PATH, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write('\n')


def _mostrar_config(config):
    print('\n=== Configuracion actual ===')
    print(json.dumps(config, indent=2, ensure_ascii=False))


def _resolver_path(valor):
    ruta = Path(valor).expanduser()
    if not ruta.is_absolute():
        ruta = PROJECT_ROOT / ruta
    return ruta


def _pedir_texto(etiqueta, default=None):
    if default is None:
        texto = input(f"{etiqueta}: ").strip()
        return texto

    texto = input(f"{etiqueta} [{default}]: ").strip()
    return texto or str(default)


def _pedir_entero(etiqueta, default, minimo=1):
    while True:
        valor = input(f"{etiqueta} [{default}]: ").strip()
        if not valor:
            return default

        try:
            numero = int(valor)
        except ValueError:
            print("Valor no valido. Debe ser un numero entero.")
            continue

        if numero < minimo:
            print(f"Valor no valido. Debe ser >= {minimo}.")
            continue

        return numero


def _pedir_bool(etiqueta, default=False):
    default_txt = "s" if default else "n"
    while True:
        valor = input(f"{etiqueta} (s/n) [{default_txt}]: ").strip().lower()
        if not valor:
            return default
        if valor in {"s", "si", "y", "yes"}:
            return True
        if valor in {"n", "no"}:
            return False
        print("Respuesta no valida. Usa s o n.")


def _pedir_seed(default=''):
    while True:
        valor = _pedir_texto('Semilla (vacio para aleatorio)', default)
        if not valor:
            return None, ''
        try:
            return int(valor), str(valor)
        except ValueError:
            print('Valor no valido. Debe ser un numero entero o vacio.')


def _confirmar_guardar_valores(config, cambios):
    if _pedir_bool('Guardar estos valores como configuracion por defecto', False):
        config.update(cambios)
        _guardar_config(config)
        print(f'Configuracion guardada en: {CONFIG_PATH}')


def _convertir_exportify_a_txt(config, interactivo=True):
    print('\n=== Convertir CSV de Exportify a TXT ===')

    if interactivo:
        entrada_txt = _pedir_texto('Ruta CSV de entrada', config['exportify_input_csv'])
        salida_txt = _pedir_texto('Ruta TXT de salida', config['exportify_output_txt'])
        columna = _pedir_texto('Nombre de columna con el titulo', config['exportify_column'])
        unicos = _pedir_bool('Eliminar titulos duplicados', bool(config['exportify_unique']))
    else:
        entrada_txt = config['exportify_input_csv']
        salida_txt = config['exportify_output_txt']
        columna = config['exportify_column']
        unicos = bool(config['exportify_unique'])

    entrada = _resolver_path(entrada_txt)
    salida = _resolver_path(salida_txt)

    if not entrada.exists():
        raise FileNotFoundError(f"No existe el archivo de entrada: {entrada}")

    titulos = extraer_titulos(entrada, columna=columna, unicos=unicos)
    salida.parent.mkdir(parents=True, exist_ok=True)
    guardar_titulos_txt(titulos, salida)
    print(f'Hecho. Se guardaron {len(titulos)} titulos en: {salida}')

    if interactivo:
        _confirmar_guardar_valores(
            config,
            {
                'exportify_input_csv': str(entrada),
                'exportify_output_txt': str(salida),
                'exportify_column': columna,
                'exportify_unique': bool(unicos),
            },
        )

    return salida


def _generar_cartones(config, interactivo=True, entrada_forzada=None):
    print('\n=== Generar cartones ===')

    if interactivo:
        entrada_txt = _pedir_texto(
            'Ruta TXT de canciones',
            str(entrada_forzada) if entrada_forzada else config['generator_input_txt'],
        )
        salida_txt = _pedir_texto('Ruta CSV de cartones', config['generator_output_csv'])
        num_cartones = _pedir_entero('Cantidad de cartones', int(config['generator_num_cartones']))
        canciones_por_carton = _pedir_entero(
            'Canciones por carton',
            int(config['generator_canciones_por_carton']),
        )
        max_coincidencias = _pedir_entero(
            'Maximo de coincidencias entre cartones',
            int(config['generator_max_coincidencias']),
        )
        seed, seed_guardar = _pedir_seed(str(config.get('generator_seed', '')))
    else:
        entrada_txt = str(entrada_forzada) if entrada_forzada else config['generator_input_txt']
        salida_txt = config['generator_output_csv']
        num_cartones = int(config['generator_num_cartones'])
        canciones_por_carton = int(config['generator_canciones_por_carton'])
        max_coincidencias = int(config['generator_max_coincidencias'])
        raw_seed = str(config.get('generator_seed', '')).strip()
        seed = int(raw_seed) if raw_seed else None
        seed_guardar = raw_seed

    entrada = _resolver_path(entrada_txt)
    salida = _resolver_path(salida_txt)

    if not entrada.exists():
        raise FileNotFoundError(f"No existe el archivo de entrada: {entrada}")

    canciones = cargar_canciones(entrada)
    cartones = generar_cartones_optimizados(
        canciones,
        num_cartones=num_cartones,
        canciones_por_carton=canciones_por_carton,
        max_coincidencias=max_coincidencias,
        seed=seed,
    )
    salida.parent.mkdir(parents=True, exist_ok=True)
    exportar_a_csv(cartones, salida)
    print(f'Hecho. Cartones guardados en: {salida}')

    if interactivo:
        _confirmar_guardar_valores(
            config,
            {
                'generator_input_txt': str(entrada),
                'generator_output_csv': str(salida),
                'generator_num_cartones': int(num_cartones),
                'generator_canciones_por_carton': int(canciones_por_carton),
                'generator_max_coincidencias': int(max_coincidencias),
                'generator_seed': seed_guardar,
            },
        )

    return salida


def _simular_partida(config, interactivo=True, cartones_forzados=None, playlist_forzada=None):
    print('\n=== Simular partida ===')

    if interactivo:
        cartones_txt = _pedir_texto(
            'Ruta CSV de cartones',
            str(cartones_forzados) if cartones_forzados else config['simulator_cartones_csv'],
        )
        playlist_txt = _pedir_texto(
            'Ruta TXT de playlist',
            str(playlist_forzada) if playlist_forzada else config['simulator_playlist_txt'],
        )
        canciones_por_carton = _pedir_entero(
            'Canciones por carton',
            int(config['simulator_canciones_por_carton']),
        )
    else:
        cartones_txt = str(cartones_forzados) if cartones_forzados else config['simulator_cartones_csv']
        playlist_txt = str(playlist_forzada) if playlist_forzada else config['simulator_playlist_txt']
        canciones_por_carton = int(config['simulator_canciones_por_carton'])

    cartones_csv = _resolver_path(cartones_txt)
    playlist_txt_path = _resolver_path(playlist_txt)

    if not cartones_csv.exists():
        raise FileNotFoundError(f"No existe el CSV de cartones: {cartones_csv}")
    if not playlist_txt_path.exists():
        raise FileNotFoundError(f"No existe el TXT de playlist: {playlist_txt_path}")

    cartones = cargar_cartones(cartones_csv)
    playlist = cargar_playlist(playlist_txt_path)
    simular_bingo(cartones, playlist, canciones_por_carton=canciones_por_carton)

    if interactivo:
        _confirmar_guardar_valores(
            config,
            {
                'simulator_cartones_csv': str(cartones_csv),
                'simulator_playlist_txt': str(playlist_txt_path),
                'simulator_canciones_por_carton': int(canciones_por_carton),
            },
        )


def _flujo_completo(config):
    print('\n=== Flujo completo: Exportify -> Cartones -> Simulacion ===')
    print('Se usara la configuracion guardada. Puedes editarla desde el menu.')
    _mostrar_config(config)

    if not _pedir_bool('Continuar con estos valores', True):
        print('Flujo cancelado.')
        return

    salida_txt = _convertir_exportify_a_txt(config, interactivo=False)
    salida_cartones = _generar_cartones(config, interactivo=False, entrada_forzada=salida_txt)
    _simular_partida(
        config,
        interactivo=False,
        cartones_forzados=salida_cartones,
        playlist_forzada=salida_txt,
    )


def _editar_configuracion(config):
    print('\n=== Editar configuracion ===')
    cambios = {}

    cambios['exportify_input_csv'] = str(_resolver_path(_pedir_texto('Exportify CSV entrada', config['exportify_input_csv'])))
    cambios['exportify_output_txt'] = str(_resolver_path(_pedir_texto('Exportify TXT salida', config['exportify_output_txt'])))
    cambios['exportify_column'] = _pedir_texto('Columna de titulo', config['exportify_column'])
    cambios['exportify_unique'] = _pedir_bool('Eliminar duplicados en Exportify', bool(config['exportify_unique']))

    cambios['generator_input_txt'] = str(_resolver_path(_pedir_texto('Generador TXT entrada', config['generator_input_txt'])))
    cambios['generator_output_csv'] = str(_resolver_path(_pedir_texto('Generador CSV salida', config['generator_output_csv'])))
    cambios['generator_num_cartones'] = _pedir_entero('Generador cantidad cartones', int(config['generator_num_cartones']))
    cambios['generator_canciones_por_carton'] = _pedir_entero(
        'Generador canciones por carton',
        int(config['generator_canciones_por_carton']),
    )
    cambios['generator_max_coincidencias'] = _pedir_entero(
        'Generador max coincidencias',
        int(config['generator_max_coincidencias']),
    )
    _, seed_guardar = _pedir_seed(str(config.get('generator_seed', '')))
    cambios['generator_seed'] = seed_guardar

    cambios['simulator_cartones_csv'] = str(_resolver_path(_pedir_texto('Simulador CSV cartones', config['simulator_cartones_csv'])))
    cambios['simulator_playlist_txt'] = str(_resolver_path(_pedir_texto('Simulador TXT playlist', config['simulator_playlist_txt'])))
    cambios['simulator_canciones_por_carton'] = _pedir_entero(
        'Simulador canciones por carton',
        int(config['simulator_canciones_por_carton']),
    )

    config.update(cambios)
    _guardar_config(config)
    print(f'Configuracion guardada en: {CONFIG_PATH}')


def _restablecer_configuracion(config):
    if _pedir_bool('Restablecer configuracion por defecto', False):
        config.clear()
        config.update(DEFAULT_CONFIG)
        _guardar_config(config)
        print(f'Configuracion restablecida en: {CONFIG_PATH}')


def _mostrar_menu():
    print("\n========================================")
    print("  Bingo Generator - Menu Pro")
    print("========================================")
    print("1) Flujo completo (Exportify -> Cartones -> Simulacion)")
    print("2) Convertir CSV de Exportify a TXT")
    print("3) Generar cartones")
    print("4) Simular partida")
    print("5) Ver configuracion")
    print("6) Editar configuracion")
    print("7) Restablecer configuracion")
    print("8) Salir")


def main():
    config = _cargar_config()

    while True:
        _mostrar_menu()
        opcion = input("Selecciona una opcion [1-8]: ").strip()

        if opcion == "1":
            try:
                _flujo_completo(config)
            except Exception as exc:
                print(f"Error: {exc}")
        elif opcion == "2":
            try:
                _convertir_exportify_a_txt(config, interactivo=True)
            except Exception as exc:
                print(f"Error: {exc}")
        elif opcion == "3":
            try:
                _generar_cartones(config, interactivo=True)
            except Exception as exc:
                print(f"Error: {exc}")
        elif opcion == "4":
            try:
                _simular_partida(config, interactivo=True)
            except Exception as exc:
                print(f"Error: {exc}")
        elif opcion == "5":
            _mostrar_config(config)
        elif opcion == "6":
            try:
                _editar_configuracion(config)
            except Exception as exc:
                print(f"Error: {exc}")
        elif opcion == "7":
            try:
                _restablecer_configuracion(config)
            except Exception as exc:
                print(f"Error: {exc}")
        elif opcion == "8":
            print("Saliendo.")
            return
        else:
            print("Opcion no valida. Elige un valor entre 1 y 8.")


if __name__ == "__main__":
    main()
