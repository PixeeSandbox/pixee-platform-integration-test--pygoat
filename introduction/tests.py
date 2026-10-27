import subprocess
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_without_shell_for_valid_hostname(self, mock_popen, mock_render):
        mock_process = Mock()
        mock_process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = mock_process
        mock_render.side_effect = lambda request, template, context: HttpResponse(context['output'])

        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(['dig', 'example.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'example output')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_shell_metacharacters_before_subprocess(self, mock_popen, mock_render):
        mock_render.side_effect = lambda request, template, context: HttpResponse(context['output'])

        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com;id', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'Something went wrong')
