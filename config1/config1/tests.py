import unittest
from unittest.mock import MagicMock, patch
import os
import tarfile
import json
import toml


from imshell import Emulator

class TestEmulator(unittest.TestCase):

    def setUp(self):
        # Создание фиктивной конфигурации для тестов
        self.config = {
            'username': 'testuser',
            'hostname': 'localhost',
            'filesystem_path': 'test.tar',
            'log_path': 'test_log.json'
        }

        # Создание экземпляра Emulator
        self.emulator = Emulator(config_path='config.toml')

        # Подмена метода загрузки конфигурации
        self.emulator.load_config = MagicMock(side_effect=self.mock_load_config)
        self.emulator.load_virtual_file_system = MagicMock(return_value=None)

        # Эмуляция файла в Tar
        self.emulator.file_system = ['Home/file1.txt', 'Home/file2.txt', 'Home/subdir/file3.txt']
        self.emulator.current_directory = 'Home'

    def mock_load_config(self, config_path):
        # Подмена логики загрузки конфигурации для теста
        self.emulator.username = self.config['username']
        self.emulator.hostname = self.config['hostname']
        self.emulator.filesystem_path = self.config['filesystem_path']
        self.emulator.log_path = self.config['log_path']

    def test_cmd_ls(self):
        # Тестирование команды ls
        output = self.emulator.cmd_ls()
        self.assertIn('file1.txt', output)
        self.assertIn('file2.txt', output)
        self.assertNotIn('file3.txt', output)  # Не должно быть в текущем каталоге

    def test_cmd_cd(self):
        # Тестирование команды cd (позитивный)
        curdir=self.emulator.current_directory
        result = self.emulator.cmd_cd('file1.txt')
        self.assertEqual(self.emulator.current_directory, curdir + '/file1.txt')
        self.assertEqual(result, "Changed directory to file1.txt")

        # Тестирование команды cd (негативный)
        result = self.emulator.cmd_cd('non_existing_dir')
        self.assertEqual(result, "Directory not found.")

    def test_cmd_echo(self):
        # Тестирование команды echo
        result = self.emulator.cmd_echo(['Hello', 'World'])
        self.assertEqual(result, 'Hello World')

    def test_cmd_tail(self):
        # Подмена метода tarfile
        with patch('tarfile.open') as mock_tarfile:
            mock_tar = MagicMock()
            mock_tar.__enter__.return_value = mock_tar
            mock_tar.getmember.return_value = 'file1.txt'
            mock_tar.extractfile.return_value = MagicMock(readlines=MagicMock(return_value=[b"Line 1\n", b"Line 2\n", b"Line 3\n"]))

            mock_tarfile.return_value = mock_tar

            result = self.emulator.cmd_tail('file1.txt')
            self.assertEqual(result, 'Line 1\nLine 2\nLine 3\n')  # Здесь нужно настроить на других условиях

    def tearDown(self):
        # Удаление фиктивных файлов или очистка если необходимо
        if os.path.exists('test_log.json'):
            os.remove('test_log.json')


if __name__ == '__main__':
    unittest.main()