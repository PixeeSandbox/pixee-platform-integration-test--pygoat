from types import SimpleNamespace
from unittest.mock import patch

import subprocess

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'linux'})
        request.user = self.user
        mock_render.return_value = SimpleNamespace()

        response = cmd_lab(request)

        self.assertFalse(mock_popen.called)
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Invalid domain'})
        self.assertIsInstance(response, SimpleNamespace)

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_uses_argument_list_and_shell_false_for_valid_hostname(self, mock_popen, mock_render):
        process = SimpleNamespace()
        process.communicate = lambda: (b'lookup output', b'')
        mock_popen.return_value = process
        mock_render.return_value = SimpleNamespace()
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once_with(['dig', 'example.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'lookup output'})
        self.assertIsInstance(response, SimpleNamespace)
