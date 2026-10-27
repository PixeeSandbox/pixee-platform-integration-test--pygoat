import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmduser', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_spawning_process(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'https://www.example.com;whoami', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_popen.called)
        self.assertEqual(response.context['output'], 'Something went wrong')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'valid output', b'')

        for os_value, expected_command in (
            ('win', ['nslookup', 'example.com']),
            ('linux', ['dig', 'example.com']),
        ):
            with self.subTest(os_value=os_value):
                mock_popen.reset_mock()
                process.communicate.return_value = (b'valid output', b'')

                response = self.client.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': os_value})

                self.assertEqual(response.status_code, 200)
                mock_popen.assert_called_with(
                    expected_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.assertEqual(response.context['output'], 'valid output')
