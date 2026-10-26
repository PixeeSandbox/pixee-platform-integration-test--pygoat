from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.http import HttpResponse
from unittest.mock import Mock, patch
import subprocess

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_cmd_lab3_valid_post_uses_safe_argument_list(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'linux'})
        request.user = self.user
        process = Mock()
        process.communicate.return_value = (b'lookup-ok', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=process) as popen_mock:
            with patch('introduction.other_views.render', return_value=HttpResponse('rendered output')) as render_mock:
                response = cmd_lab3(request)

        self.assertEqual(response.content, b'rendered output')
        popen_mock.assert_called_once_with(['dig', 'example.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        render_mock.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'lookup-ok'})

    def test_cmd_lab3_rejects_injected_domain_before_popen(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; id', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as popen_mock:
            with patch('introduction.other_views.render', return_value=HttpResponse('invalid input')) as render_mock:
                response = cmd_lab3(request)

        self.assertEqual(response.content, b'invalid input')
        popen_mock.assert_not_called()
        render_mock.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Invalid input'})
