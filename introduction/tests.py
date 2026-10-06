from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='StrongPass123!'
        )

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('ok')
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'example output', b'')

        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'https://www.example.com', 'os': 'win'}
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.content, b'ok')
        self.assertEqual(mock_popen.call_count, 1)
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertEqual(kwargs.get('shell'), False)

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_popen(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('rejected')

        request = self.factory.post(
            '/cmd_lab/',
            {'domain': 'example.com; id', 'os': 'win'}
        )
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.content, b'rejected')
        mock_popen.assert_not_called()
        mock_render.assert_called_once()
