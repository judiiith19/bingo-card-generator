import argparse

from src.menu_interactivo import main

VERSION = '0.2.0'


def parse_args():
    parser = argparse.ArgumentParser(
        description='Bingo Generator - menú interactivo y flujo automatizado.'
    )
    parser.add_argument(
        '--config',
        default='bingo_config.json',
        help='Ruta al archivo de configuración JSON (relativa al proyecto o absoluta).',
    )
    parser.add_argument(
        '--run-full',
        action='store_true',
        help='Ejecuta flujo completo no interactivo usando la configuración guardada.',
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {VERSION}',
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(config_path=args.config, run_full=args.run_full)
