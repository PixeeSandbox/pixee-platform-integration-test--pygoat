from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password')

    def test_cmd_lab3_rejects_malicious_domain(self):
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com;id', 'os': 'win'})
        request.user = self.user

        with patch('introduction.other_views.subprocess.run') as mock_run, patch('introduction.other_views.render') as mock_render:
            mock_render.return_value = HttpResponse('rendered')
            response = cmd_lab3(request)

        mock_run.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args[0][2]['output'], 'Something went wrong')
        self.assertEqual(response.content, b'rendered')

    def test_cmd_lab3_uses_subprocess_run_with_argv_list(self):
        request = self.factory.post('/cmd_lab3/', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = self.user

        with patch('introduction.other_views.subprocess.run') as mock_run, patch('introduction.other_views.render') as mock_render:
            mock_run.return_value.stdout = 'resolver output'
            mock_run.return_value.stderr = 'warnings'
            mock_render.return_value = HttpResponse('rendered')
            response = cmd_lab3(request)

        mock_run.assert_called_once_with(['nslookup', 'example.com'], capture_output=True, text=True, check=False)
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args[0][2]['output'], 'resolver outputwarnings')
        self.assertEqual(response.content, b'rendered')
