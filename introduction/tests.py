from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from unittest.mock import patch

from .other_views import cmd_lab3


class TestCmdLab3(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_without_shell(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})
        request.user = type('User', (), {'is_authenticated': True})()
        process = mock_popen.return_value
        process.communicate.return_value = (b'output', b'')
        mock_render.return_value = HttpResponse('ok')

        response = cmd_lab3(request)

        self.assertEqual(mock_popen.call_args.args[0], ['dig', 'example.com'])
        self.assertFalse(mock_popen.call_args.kwargs['shell'])
        self.assertEqual(response.content, b'ok')
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'output'})

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = type('User', (), {'is_authenticated': True})()
        mock_render.return_value = HttpResponse('Something went wrong')

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.content, b'Something went wrong')
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Something went wrong'})
