import json
import tempfile
import unittest
from pathlib import Path

import src.menu_interactivo as menu


class TestMenuInteractivoConfig(unittest.TestCase):
    def test_cargar_config_repara_json_corrupto_y_crea_backup(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / 'bingo_config.json'
            config_path.write_text('{ json invalido', encoding='utf-8')

            config = menu._cargar_config(config_path)

            backup = Path(str(config_path) + '.bak')
            self.assertTrue(backup.exists())
            self.assertIn('exportify_input_csv', config)

            with open(config_path, 'r', encoding='utf-8') as f:
                reparado = json.load(f)
            self.assertIn('generator_output_csv', reparado)


if __name__ == '__main__':
    unittest.main()
