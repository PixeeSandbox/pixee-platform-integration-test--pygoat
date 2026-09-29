from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password',
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_run, mock_render):
        mock_run.return_value = type('Process', (), {'stdout': 'out', 'stderr': 'err'})()
        mock_render.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content, b'ok')
        mock_run.assert_called_once_with(
            ['nslookup', 'example.com'],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotIn('shell', mock_run.call_args.kwargs)

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_shell_metacharacters_before_execution(self, mock_run, mock_render):
        mock_render.return_value = HttpResponse('rejected')

        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com;id', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content, b'rejected')
        mock_run.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'},
        )
