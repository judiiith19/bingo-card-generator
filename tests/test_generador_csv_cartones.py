import tempfile
import unittest
from pathlib import Path

from src.generador_csv_cartones import exportar_a_csv, generar_cartones_optimizados, puntuar_premios_simultaneos


class TestGeneradorCartones(unittest.TestCase):
    def test_genera_numero_esperado_de_cartones(self):
        canciones = [f'Cancion {i}' for i in range(40)]
        cartones = generar_cartones_optimizados(
            canciones,
            num_cartones=10,
            canciones_por_carton=12,
            max_coincidencias=6,
            seed=123,
        )
        self.assertEqual(len(cartones), 10)
        self.assertTrue(all(len(c) == 12 for c in cartones))

    def test_exportar_falla_si_no_hay_cartones(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            salida = Path(tmp_dir) / 'cartones.csv'
            with self.assertRaises(ValueError):
                exportar_a_csv([], salida)

    def test_puntuar_premios_simultaneos_penaliza_linea_y_bingo(self):
        reporte = {
            'lineas': [
                {'minuto': 10, 'cartones': [1, 2]},
                {'minuto': 12, 'cartones': [3]},
                {'minuto': 15, 'cartones': [4, 5, 6]},
            ],
            'bingos': [
                {'minuto': 50, 'cartones': [7, 8]},
            ],
        }

        score, resumen = puntuar_premios_simultaneos(
            reporte,
            peso_linea_simultanea=10,
            peso_bingo_simultaneo=1000,
        )

        self.assertEqual(score, 1030)
        self.assertEqual(resumen['lineas_simultaneas'], 2)
        self.assertEqual(resumen['bingos_simultaneos'], 1)
        self.assertEqual(resumen['max_lineas_en_un_minuto'], 3)
        self.assertEqual(resumen['max_bingos_en_un_minuto'], 2)

    def test_falla_si_intentos_optimizacion_menor_que_uno(self):
        canciones = [f'Cancion {i}' for i in range(20)]
        with self.assertRaises(ValueError):
            generar_cartones_optimizados(
                canciones,
                num_cartones=5,
                canciones_por_carton=12,
                max_coincidencias=6,
                intentos_optimizacion=0,
            )


if __name__ == '__main__':
    unittest.main()
