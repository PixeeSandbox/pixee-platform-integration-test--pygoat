from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_cmd_lab3_uses_argument_list_for_windows(self):
        with patch('introduction.other_views.render') as mock_render, patch('introduction.other_views.subprocess.Popen') as mock_popen:
            process = Mock()
            process.communicate.return_value = (b'win-output', b'')
            mock_popen.return_value = process
            mock_render.return_value = HttpResponse('ok')

            request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})
            request.user = self.user

            response = cmd_lab3(request)

            self.assertEqual(response.status_code, 200)
            mock_popen.assert_called_once()
            self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
            self.assertFalse(mock_popen.call_args.kwargs['shell'])

    def test_cmd_lab3_uses_argument_list_for_linux(self):
        with patch('introduction.other_views.render') as mock_render, patch('introduction.other_views.subprocess.Popen') as mock_popen:
            process = Mock()
            process.communicate.return_value = (b'linux-output', b'')
            mock_popen.return_value = process
            mock_render.return_value = HttpResponse('ok')

            request = self.factory.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})
            request.user = self.user

            response = cmd_lab3(request)

            self.assertEqual(response.status_code, 200)
            mock_popen.assert_called_once()
            self.assertEqual(mock_popen.call_args.args[0], ['dig', 'example.com'])
            self.assertFalse(mock_popen.call_args.kwargs['shell'])

    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self):
        with patch('introduction.other_views.render') as mock_render, patch('introduction.other_views.subprocess.Popen') as mock_popen:
            mock_render.return_value = HttpResponse('invalid')

            request = self.factory.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
            request.user = self.user

            response = cmd_lab3(request)

            self.assertEqual(response.status_code, 200)
            mock_popen.assert_not_called()
            mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Something went wrong'})
