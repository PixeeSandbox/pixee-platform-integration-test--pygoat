from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.http import HttpResponse
from unittest.mock import MagicMock, patch
import subprocess

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_without_shell_for_valid_domain(self, popen_mock, render_mock):
        process_mock = MagicMock()
        process_mock.communicate.return_value = (b'valid output', b'')
        popen_mock.return_value = process_mock
        render_mock.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        popen_mock.assert_called_once()
        self.assertEqual(popen_mock.call_args.args[0], ['nslookup', 'example.com'])
        self.assertFalse(popen_mock.call_args.kwargs.get('shell', False))
        self.assertEqual(popen_mock.call_args.kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(popen_mock.call_args.kwargs['stderr'], subprocess.PIPE)
        render_mock.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'valid output'})

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, popen_mock, render_mock):
        render_mock.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; id', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        popen_mock.assert_not_called()
        render_mock.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Invalid domain'})
