from django.test import RequestFactory, TestCase
from django.contrib.auth.models import User
from django.http import HttpResponse
from unittest.mock import Mock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.other_views.subprocess.Popen')
    @patch('introduction.other_views.render')
    def test_cmd_lab3_rejects_malicious_domain_without_subprocess(self, mock_render, mock_popen):
        mock_render.return_value = HttpResponse('ok')
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content, b'ok')
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Something went wrong'})

    @patch('introduction.other_views.subprocess.Popen')
    @patch('introduction.other_views.render')
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_render, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse('ok')
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.content, b'ok')
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=-1,
            stderr=-1,
        )
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'lookup output'})
