import csv
import tempfile
import unittest
from pathlib import Path

from src.exportify_to_txt import extraer_titulos


class TestExportifyToTxt(unittest.TestCase):
    def test_extraer_titulos_con_unicos(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / 'playlist.csv'
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Track Name', 'Artist'])
                writer.writerow(['Cancion A', 'X'])
                writer.writerow(['Cancion B', 'Y'])
                writer.writerow(['Cancion A', 'Z'])

            titulos = extraer_titulos(csv_path, columna='Track Name', unicos=True)
            self.assertEqual(titulos, ['Cancion A', 'Cancion B'])

    def test_falla_si_columna_no_existe(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / 'playlist.csv'
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Titulo'])
                writer.writerow(['Cancion A'])

            with self.assertRaises(ValueError):
                extraer_titulos(csv_path, columna='Track Name', unicos=False)


if __name__ == '__main__':
    unittest.main()
