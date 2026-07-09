import json
from json import JSONDecodeError
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
DEFAULT_CONFIG_PATH = PROJECT_ROOT / 'bingo_config.json'


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
    'generator_playlist_referencia_txt': '',
    'generator_canciones_por_linea': 4,
    'generator_intentos_optimizacion': 1,
    'generator_peso_linea_simultanea': 10,
    'generator_peso_bingo_simultaneo': 1000,
    'simulator_cartones_csv': _a_ruta_relativa_proyecto(DEFAULT_SIM_CARTONES),
    'simulator_playlist_txt': _a_ruta_relativa_proyecto(DEFAULT_SIM_PLAYLIST),
    'simulator_canciones_por_carton': 12,
    'simulator_canciones_por_linea': 4,
}


def _ruta_relativa(path_value):
    path_obj = Path(path_value)
    if not path_obj.is_absolute():
        return str(path_obj).replace('\\', '/')

    try:
        return str(path_obj.relative_to(PROJECT_ROOT)).replace('\\', '/')
    except ValueError:
        return str(path_obj).replace('\\', '/')


def _normalizar_config(config):
    normalizada = dict(DEFAULT_CONFIG)
    normalizada.update(config)

    for key in (
        'exportify_input_csv',
        'exportify_output_txt',
        'generator_input_txt',
        'generator_output_csv',
        'generator_playlist_referencia_txt',
        'simulator_cartones_csv',
        'simulator_playlist_txt',
    ):
        normalizada[key] = _ruta_relativa(normalizada[key]) if normalizada[key] else ''

    return normalizada


def _cargar_config(config_path):
    if not config_path.exists():
        _guardar_config(DEFAULT_CONFIG, config_path)
        return dict(DEFAULT_CONFIG)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except JSONDecodeError:
        backup_path = config_path.with_suffix(config_path.suffix + '.bak')
        config_path.replace(backup_path)
        _guardar_config(DEFAULT_CONFIG, config_path)
        print(f'Configuración inválida. Se creó backup en: {backup_path}')
        return dict(DEFAULT_CONFIG)

    return _normalizar_config(config)


def _guardar_config(config, config_path):
    with open(config_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(_normalizar_config(config), f, indent=2, ensure_ascii=False)
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


def _confirmar_guardar_valores(config, cambios, config_path):
    if _pedir_bool('Guardar estos valores como configuracion por defecto', False):
        config.update(cambios)
        _guardar_config(config, config_path)
        print(f'Configuracion guardada en: {config_path}')


def _convertir_exportify_a_txt(config, config_path, interactivo=True):
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
                'exportify_input_csv': _ruta_relativa(entrada),
                'exportify_output_txt': _ruta_relativa(salida),
                'exportify_column': columna,
                'exportify_unique': bool(unicos),
            },
            config_path,
        )

    return salida


def _generar_cartones(config, config_path, interactivo=True, entrada_forzada=None):
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
        playlist_referencia_txt = _pedir_texto(
            'Ruta TXT playlist referencia (vacio para desactivar optimizacion)',
            config.get('generator_playlist_referencia_txt', ''),
        )
        canciones_por_linea = _pedir_entero(
            'Canciones para linea (optimizacion)',
            int(config.get('generator_canciones_por_linea', 4)),
        )
        intentos_optimizacion = _pedir_entero(
            'Intentos de optimizacion',
            int(config.get('generator_intentos_optimizacion', 1)),
        )
        peso_linea_simultanea = _pedir_entero(
            'Peso linea simultanea',
            int(config.get('generator_peso_linea_simultanea', 10)),
            minimo=0,
        )
        peso_bingo_simultaneo = _pedir_entero(
            'Peso bingo simultaneo',
            int(config.get('generator_peso_bingo_simultaneo', 1000)),
            minimo=0,
        )
    else:
        entrada_txt = str(entrada_forzada) if entrada_forzada else config['generator_input_txt']
        salida_txt = config['generator_output_csv']
        num_cartones = int(config['generator_num_cartones'])
        canciones_por_carton = int(config['generator_canciones_por_carton'])
        max_coincidencias = int(config['generator_max_coincidencias'])
        raw_seed = str(config.get('generator_seed', '')).strip()
        seed = int(raw_seed) if raw_seed else None
        seed_guardar = raw_seed
        playlist_referencia_txt = str(config.get('generator_playlist_referencia_txt', '')).strip()
        canciones_por_linea = int(config.get('generator_canciones_por_linea', 4))
        intentos_optimizacion = int(config.get('generator_intentos_optimizacion', 1))
        peso_linea_simultanea = int(config.get('generator_peso_linea_simultanea', 10))
        peso_bingo_simultaneo = int(config.get('generator_peso_bingo_simultaneo', 1000))

    entrada = _resolver_path(entrada_txt)
    salida = _resolver_path(salida_txt)
    playlist_referencia_path = _resolver_path(playlist_referencia_txt) if playlist_referencia_txt else None

    if not entrada.exists():
        raise FileNotFoundError(f"No existe el archivo de entrada: {entrada}")
    if playlist_referencia_path and not playlist_referencia_path.exists():
        raise FileNotFoundError(f"No existe la playlist de referencia: {playlist_referencia_path}")

    canciones = cargar_canciones(entrada)
    playlist_referencia = cargar_canciones(playlist_referencia_path) if playlist_referencia_path else None
    cartones = generar_cartones_optimizados(
        canciones,
        num_cartones=num_cartones,
        canciones_por_carton=canciones_por_carton,
        max_coincidencias=max_coincidencias,
        seed=seed,
        playlist_referencia=playlist_referencia,
        canciones_por_linea=canciones_por_linea,
        intentos_optimizacion=intentos_optimizacion,
        peso_linea_simultanea=peso_linea_simultanea,
        peso_bingo_simultaneo=peso_bingo_simultaneo,
    )
    salida.parent.mkdir(parents=True, exist_ok=True)
    exportar_a_csv(cartones, salida)
    print(f'Hecho. Cartones guardados en: {salida}')

    if interactivo:
        _confirmar_guardar_valores(
            config,
            {
                'generator_input_txt': _ruta_relativa(entrada),
                'generator_output_csv': _ruta_relativa(salida),
                'generator_num_cartones': int(num_cartones),
                'generator_canciones_por_carton': int(canciones_por_carton),
                'generator_max_coincidencias': int(max_coincidencias),
                'generator_seed': seed_guardar,
                'generator_playlist_referencia_txt': _ruta_relativa(playlist_referencia_path) if playlist_referencia_path else '',
                'generator_canciones_por_linea': int(canciones_por_linea),
                'generator_intentos_optimizacion': int(intentos_optimizacion),
                'generator_peso_linea_simultanea': int(peso_linea_simultanea),
                'generator_peso_bingo_simultaneo': int(peso_bingo_simultaneo),
            },
            config_path,
        )

    return salida


def _simular_partida(config, config_path, interactivo=True, cartones_forzados=None, playlist_forzada=None):
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
        canciones_por_linea = _pedir_entero(
            'Canciones para linea',
            int(config['simulator_canciones_por_linea']),
        )
    else:
        cartones_txt = str(cartones_forzados) if cartones_forzados else config['simulator_cartones_csv']
        playlist_txt = str(playlist_forzada) if playlist_forzada else config['simulator_playlist_txt']
        canciones_por_carton = int(config['simulator_canciones_por_carton'])
        canciones_por_linea = int(config['simulator_canciones_por_linea'])

    cartones_csv = _resolver_path(cartones_txt)
    playlist_txt_path = _resolver_path(playlist_txt)

    if not cartones_csv.exists():
        raise FileNotFoundError(f"No existe el CSV de cartones: {cartones_csv}")
    if not playlist_txt_path.exists():
        raise FileNotFoundError(f"No existe el TXT de playlist: {playlist_txt_path}")

    cartones = cargar_cartones(cartones_csv)
    playlist = cargar_playlist(playlist_txt_path)
    simular_bingo(
        cartones,
        playlist,
        canciones_por_carton=canciones_por_carton,
        canciones_por_linea=canciones_por_linea,
    )

    if interactivo:
        _confirmar_guardar_valores(
            config,
            {
                'simulator_cartones_csv': _ruta_relativa(cartones_csv),
                'simulator_playlist_txt': _ruta_relativa(playlist_txt_path),
                'simulator_canciones_por_carton': int(canciones_por_carton),
                'simulator_canciones_por_linea': int(canciones_por_linea),
            },
            config_path,
        )


def _flujo_completo(config, config_path):
    print('\n=== Flujo completo: Exportify -> Cartones -> Simulacion ===')
    print('Se usara la configuracion guardada. Puedes editarla desde el menu.')
    _mostrar_config(config)

    if not _pedir_bool('Continuar con estos valores', True):
        print('Flujo cancelado.')
        return

    salida_txt = _convertir_exportify_a_txt(config, config_path, interactivo=False)
    salida_cartones = _generar_cartones(config, config_path, interactivo=False, entrada_forzada=salida_txt)
    _simular_partida(
        config,
        config_path,
        interactivo=False,
        cartones_forzados=salida_cartones,
        playlist_forzada=salida_txt,
    )


def _editar_configuracion(config, config_path):
    print('\n=== Editar configuracion ===')
    cambios = {}

    cambios['exportify_input_csv'] = _ruta_relativa(_resolver_path(_pedir_texto('Exportify CSV entrada', config['exportify_input_csv'])))
    cambios['exportify_output_txt'] = _ruta_relativa(_resolver_path(_pedir_texto('Exportify TXT salida', config['exportify_output_txt'])))
    cambios['exportify_column'] = _pedir_texto('Columna de titulo', config['exportify_column'])
    cambios['exportify_unique'] = _pedir_bool('Eliminar duplicados en Exportify', bool(config['exportify_unique']))

    cambios['generator_input_txt'] = _ruta_relativa(_resolver_path(_pedir_texto('Generador TXT entrada', config['generator_input_txt'])))
    cambios['generator_output_csv'] = _ruta_relativa(_resolver_path(_pedir_texto('Generador CSV salida', config['generator_output_csv'])))
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
    playlist_referencia_edit = _pedir_texto('Generador playlist referencia (vacio=off)', config.get('generator_playlist_referencia_txt', ''))
    cambios['generator_playlist_referencia_txt'] = _ruta_relativa(_resolver_path(playlist_referencia_edit)) if playlist_referencia_edit else ''
    cambios['generator_canciones_por_linea'] = _pedir_entero(
        'Generador canciones para linea (optimizacion)',
        int(config.get('generator_canciones_por_linea', 4)),
    )
    cambios['generator_intentos_optimizacion'] = _pedir_entero(
        'Generador intentos de optimizacion',
        int(config.get('generator_intentos_optimizacion', 1)),
    )
    cambios['generator_peso_linea_simultanea'] = _pedir_entero(
        'Generador peso linea simultanea',
        int(config.get('generator_peso_linea_simultanea', 10)),
        minimo=0,
    )
    cambios['generator_peso_bingo_simultaneo'] = _pedir_entero(
        'Generador peso bingo simultaneo',
        int(config.get('generator_peso_bingo_simultaneo', 1000)),
        minimo=0,
    )

    cambios['simulator_cartones_csv'] = _ruta_relativa(_resolver_path(_pedir_texto('Simulador CSV cartones', config['simulator_cartones_csv'])))
    cambios['simulator_playlist_txt'] = _ruta_relativa(_resolver_path(_pedir_texto('Simulador TXT playlist', config['simulator_playlist_txt'])))
    cambios['simulator_canciones_por_carton'] = _pedir_entero(
        'Simulador canciones por carton',
        int(config['simulator_canciones_por_carton']),
    )
    cambios['simulator_canciones_por_linea'] = _pedir_entero(
        'Simulador canciones para linea',
        int(config['simulator_canciones_por_linea']),
    )

    config.update(cambios)
    _guardar_config(config, config_path)
    print(f'Configuracion guardada en: {config_path}')


def _restablecer_configuracion(config, config_path):
    if _pedir_bool('Restablecer configuracion por defecto', False):
        config.clear()
        config.update(DEFAULT_CONFIG)
        _guardar_config(config, config_path)
        print(f'Configuracion restablecida en: {config_path}')


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


def main(config_path=None, run_full=False):
    resolved_config_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not resolved_config_path.is_absolute():
        resolved_config_path = PROJECT_ROOT / resolved_config_path

    config = _cargar_config(resolved_config_path)

    if run_full:
        _flujo_completo(config, resolved_config_path)
        return

    while True:
        _mostrar_menu()
        opcion = input("Selecciona una opcion [1-8]: ").strip()

        if opcion == "1":
            try:
                _flujo_completo(config, resolved_config_path)
            except Exception as exc:
                print(f"Error: {exc}")
        elif opcion == "2":
            try:
                _convertir_exportify_a_txt(config, resolved_config_path, interactivo=True)
            except Exception as exc:
                print(f"Error: {exc}")
        elif opcion == "3":
            try:
                _generar_cartones(config, resolved_config_path, interactivo=True)
            except Exception as exc:
                print(f"Error: {exc}")
        elif opcion == "4":
            try:
                _simular_partida(config, resolved_config_path, interactivo=True)
            except Exception as exc:
                print(f"Error: {exc}")
        elif opcion == "5":
            _mostrar_config(config)
        elif opcion == "6":
            try:
                _editar_configuracion(config, resolved_config_path)
            except Exception as exc:
                print(f"Error: {exc}")
        elif opcion == "7":
            try:
                _restablecer_configuracion(config, resolved_config_path)
            except Exception as exc:
                print(f"Error: {exc}")
        elif opcion == "8":
            print("Saliendo.")
            return
        else:
            print("Opcion no valida. Elige un valor entre 1 y 8.")


if __name__ == "__main__":
    main()
