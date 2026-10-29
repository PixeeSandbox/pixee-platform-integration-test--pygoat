from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_without_shell_for_dig(self, mock_popen, mock_render):
        mock_popen.return_value.communicate.return_value = (b'8.8.8.8\n', b'')
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = other_views.cmd_lab3(request)

        self.assertEqual(response, mock_render.return_value)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': '8.8.8.8\n'},
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_without_shell_for_nslookup(self, mock_popen, mock_render):
        mock_popen.return_value.communicate.return_value = (b'Name: example.com\n', b'')
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = other_views.cmd_lab3(request)

        self.assertEqual(response, mock_render.return_value)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Name: example.com\n'},
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_injection_payload(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; id', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = other_views.cmd_lab3(request)

        self.assertEqual(response, mock_render.return_value)
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'},
        )
