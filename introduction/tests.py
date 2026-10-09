import subprocess

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_shell_free_arguments(self, popen_mock, render_mock):
        process = Mock()
        process.communicate.return_value = (b'example.com.\n', b'')
        popen_mock.return_value = process
        render_mock.side_effect = lambda request, template, context: HttpResponse(context['output'])

        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        popen_mock.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.content.decode(), 'example.com.\n')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, popen_mock, render_mock):
        render_mock.side_effect = lambda request, template, context: HttpResponse(context['output'])

        request = self.factory.post('/cmd_lab3', {'domain': 'example.com;id', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        popen_mock.assert_not_called()
        self.assertEqual(response.content.decode(), 'Something went wrong')
