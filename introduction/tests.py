from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_posts_argv_to_subprocess(self, mock_run, mock_render):
        mock_run.return_value = SimpleNamespace(stdout='resolved', stderr='')
        mock_render.return_value = HttpResponse('rendered')

        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        mock_run.assert_called_once_with(
            ['nslookup', 'example.com'],
            capture_output=True,
            text=True,
            check=False,
        )
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[1], 'Lab/CMD/cmd_lab.html')
        self.assertEqual(mock_render.call_args.args[2]['output'], 'resolved')
        self.assertEqual(response.content, b'rendered')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_shell_metacharacters_before_subprocess(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse('rendered')

        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        mock_run.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[1], 'Lab/CMD/cmd_lab.html')
        self.assertEqual(mock_render.call_args.args[2]['output'], 'Something went wrong')
        self.assertEqual(response.content, b'rendered')
