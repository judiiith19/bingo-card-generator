import csv
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from src.exportify_to_txt import extraer_titulos, guardar_titulos_txt
from src.generador_csv_cartones import cargar_canciones, exportar_a_csv, generar_cartones_optimizados
from src.simulador_partidas import cargar_cartones, cargar_playlist, simular_bingo


class TestIntegrationFlow(unittest.TestCase):
    def test_end_to_end_exportify_to_simulation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)

            exportify_csv = tmp / 'playlist.csv'
            songs_txt = tmp / 'songs.txt'
            cartones_csv = tmp / 'cartones.csv'

            songs = [f'Song {i}' for i in range(1, 31)]

            with open(exportify_csv, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Track Name', 'Artist'])
                for s in songs:
                    writer.writerow([s, 'Artist'])

            titulos = extraer_titulos(exportify_csv, columna='Track Name', unicos=True)
            guardar_titulos_txt(titulos, songs_txt)

            canciones = cargar_canciones(songs_txt)
            cartones = generar_cartones_optimizados(
                canciones,
                num_cartones=5,
                canciones_por_carton=12,
                max_coincidencias=8,
                seed=42,
            )
            exportar_a_csv(cartones, cartones_csv)

            cartones_cargados = cargar_cartones(cartones_csv)
            playlist = cargar_playlist(songs_txt)

            sink = io.StringIO()
            with redirect_stdout(sink):
                simular_bingo(cartones_cargados, playlist, canciones_por_carton=12)

            output = sink.getvalue()
            self.assertTrue('BINGO' in output or 'Final de playlist' in output)


if __name__ == '__main__':
    unittest.main()
