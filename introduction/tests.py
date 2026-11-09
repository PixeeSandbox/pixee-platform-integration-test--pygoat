import subprocess
from django.test import TestCase, RequestFactory
from types import SimpleNamespace
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_invoking_shell(self, mock_popen):
        request = self.factory.post('/cmd_lab3', data={'domain': 'https://www.example.com;id', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen):
        process = SimpleNamespace(communicate=lambda: (b'lookup output', b''))
        mock_popen.return_value = process
        request = self.factory.post('/cmd_lab3', data={'domain': 'https://www.example.com', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(['dig', 'example.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup output')
