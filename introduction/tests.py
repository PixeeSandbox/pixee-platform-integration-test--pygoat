from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass')

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('Something went wrong')
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com; rm -rf /', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_render.call_args[0][2]['output'], 'Something went wrong')

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b'answer', b'')
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse('ok')
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args[0][0], ['dig', 'example.com'])
        self.assertFalse(mock_popen.call_args.kwargs['shell'])
        self.assertEqual(mock_render.call_args[0][2]['output'], 'answer')
        self.assertEqual(response.status_code, 200)
