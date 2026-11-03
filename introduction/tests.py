from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123',
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_valid_hostname_uses_argv_subprocess(self, mock_run, mock_render):
        mock_run.return_value = MagicMock()
        mock_run.return_value.stdout = 'STDOUT'
        mock_run.return_value.stderr = 'STDERR'
        mock_render.return_value = HttpResponse('ok')
        request = self.factory.post(
            '/cmd_lab3/',
            data={'domain': 'https://www.example.com', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertTrue(kwargs['capture_output'])
        self.assertTrue(kwargs['text'])
        self.assertFalse(kwargs['check'])
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'STDOUTSTDERR'},
        )

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_malicious_domain_rejects_input(self, mock_run):
        request = self.factory.post(
            '/cmd_lab3/',
            data={'domain': 'example.com; rm -rf /', 'os': 'linux'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid domain', response.content)
        mock_run.assert_not_called()
