import unittest

from src.simulador_partidas import contar_cartones_a_punto


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


if __name__ == '__main__':
    unittest.main()
