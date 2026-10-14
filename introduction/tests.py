import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password123')

    @patch('introduction.other_views.subprocess.Popen')
    @patch('introduction.other_views.render')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_render, mock_popen):
        mock_render.return_value = HttpResponse('Something went wrong')
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com; whoami', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Something went wrong'})
        self.assertEqual(response.content, b'Something went wrong')

    @patch('introduction.other_views.subprocess.Popen')
    @patch('introduction.other_views.render')
    def test_cmd_lab3_uses_argv_list_for_valid_domain(self, mock_render, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')
        mock_render.return_value = HttpResponse('lookup output')
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(['dig', 'example.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'lookup output'})
        self.assertEqual(response.content, b'lookup output')
