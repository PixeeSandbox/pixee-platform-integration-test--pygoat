from django.contrib.auth import get_user_model
from django.test import TestCase
import subprocess
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.username = 'tester'
        self.password = 'StrongPass123!'
        user_model.objects.create_user(username=self.username, password=self.password)
        self.assertTrue(self.client.login(username=self.username, password=self.password))

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_and_shell_false(self, mock_popen):
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = (b'valid output', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'valid output')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_popen(self, mock_popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
