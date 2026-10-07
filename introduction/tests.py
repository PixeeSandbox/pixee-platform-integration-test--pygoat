import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_popen, mock_render):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'example output', b'')
        mock_render.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_invalid_domain_before_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('bad')

        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; id', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Something went wrong'})
