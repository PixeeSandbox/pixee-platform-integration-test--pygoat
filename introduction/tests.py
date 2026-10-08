from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )

    @patch('introduction.views.render', return_value=HttpResponse('ok'))
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_executes_safe_command_for_valid_domain(self, mock_popen, mock_render):
        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'https://www.example.com', 'os': 'win'},
        )
        request.user = self.user
        mock_popen.return_value.communicate.return_value = (b'lookupsuccess', b'')

        response = cmd_lab(request)

        self.assertEqual(response.content, b'ok')
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args[0][0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'lookupsuccess'},
        )

    @patch('introduction.views.render', return_value=HttpResponse('rejected'))
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen, mock_render):
        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'example.com; rm -rf /', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.content, b'rejected')
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'},
        )
