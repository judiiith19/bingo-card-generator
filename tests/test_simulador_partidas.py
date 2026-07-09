import unittest

from src.simulador_partidas import contar_cartones_a_linea, contar_cartones_a_punto, simular_bingo


class TestSimuladorPartidas(unittest.TestCase):
    def test_contador_usa_tamano_real_del_carton(self):
        cartones = [
            {'canciones': {'A', 'B', 'C', 'D'}, 'marcadas': {'A'}},
            {'canciones': {'E', 'F', 'G', 'H', 'I'}, 'marcadas': {'E', 'F', 'G'}},
            {'canciones': {'J', 'K', 'L', 'M', 'N', 'O'}, 'marcadas': {'J', 'K', 'L', 'M', 'N'}},
        ]

        a_3, a_2, a_1 = contar_cartones_a_punto(cartones, canciones_por_carton=12)

        self.assertEqual(a_3, 1)
        self.assertEqual(a_2, 1)
        self.assertEqual(a_1, 1)

    def test_contador_de_linea_usa_umbral(self):
        cartones = [
            {'canciones': {'A', 'B', 'C', 'D'}, 'marcadas': {'A'}, 'linea_cantada': False},
            {'canciones': {'E', 'F', 'G', 'H', 'I'}, 'marcadas': {'E', 'F'}, 'linea_cantada': False},
            {'canciones': {'J', 'K', 'L', 'M', 'N', 'O'}, 'marcadas': {'J', 'K', 'L'}, 'linea_cantada': False},
        ]

        a_3, a_2, a_1 = contar_cartones_a_linea(cartones, canciones_por_linea=4)

        self.assertEqual(a_3, 1)
        self.assertEqual(a_2, 1)
        self.assertEqual(a_1, 1)

    def test_simulacion_detecta_lineas_simultaneas(self):
        cartones = [
            {'canciones': {'A', 'B', 'C', 'D'}, 'marcadas': set(), 'linea_cantada': False, 'bingo_cantado': False},
            {'canciones': {'A', 'B', 'C', 'E'}, 'marcadas': set(), 'linea_cantada': False, 'bingo_cantado': False},
        ]

        reporte = simular_bingo(cartones, ['A', 'B', 'C', 'D'], canciones_por_carton=4, canciones_por_linea=3)

        self.assertEqual(len(reporte['lineas']), 1)
        self.assertEqual(reporte['lineas'][0]['cartones'], [1, 2])
        self.assertEqual(len(reporte['bingos']), 1)
        self.assertEqual(reporte['bingos'][0]['cartones'], [1])


if __name__ == '__main__':
    unittest.main()
