from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

import introduction.views as views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_windows_uses_argument_list(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'windows-output', b'')
        mock_render.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab/', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        mock_render.assert_called_once()
        self.assertEqual(response.status_code, 200)

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_non_windows_uses_argument_list(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'linux-output', b'')
        mock_render.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab/', {'domain': 'https://www.example.com', 'os': 'linux'})
        request.user = self.user

        response = views.cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        mock_render.assert_called_once()
        self.assertEqual(response.status_code, 200)
