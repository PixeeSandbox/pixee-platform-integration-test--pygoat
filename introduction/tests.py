import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabCommandInjectionTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='cmd-test-user', password='test-password')
        self.client.force_login(user)

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_is_passed_as_separate_command_arguments(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        for os_choice, executable in (('win', 'nslookup'), ('linux', 'dig')):
            with self.subTest(os=os_choice):
                response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': os_choice})

                self.assertEqual(response.status_code, 200)
                mock_popen.assert_called_once_with(
                    [executable, 'example.com'],
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                mock_popen.reset_mock()

    @patch('introduction.views.subprocess.Popen')
    def test_domain_with_shell_metacharacters_is_rejected(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'linux'})

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
