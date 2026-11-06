import subprocess
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'example.com; rm -rf /', 'os': 'win'}
        )
        self.request.user = MagicMock(is_authenticated=True)

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_win_branch(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b'output', b'')
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse('ok')

        response = cmd_lab(self.request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com; rm -rf /'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        mock_render.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'ok')

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_non_win_branch(self, mock_popen, mock_render):
        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'example.com; rm -rf /', 'os': 'linux'}
        )
        request.user = MagicMock(is_authenticated=True)
        process = MagicMock()
        process.communicate.return_value = (b'output', b'')
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse('ok')

        response = cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['dig', 'example.com; rm -rf /'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        mock_render.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'ok')
