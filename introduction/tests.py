from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch
import subprocess

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlab3user',
            password='testpass123',
        )

    def _make_request(self, os_value):
        request = self.factory.post(
            '/cmd_lab3/',
            {'domain': 'example.com; rm -rf /', 'os': os_value},
        )
        request.user = self.user
        return request

    @patch('introduction.other_views.render', return_value=HttpResponse('ok'))
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_list_for_dig(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'dig output', b'')

        response = cmd_lab3(self._make_request('linux'))

        self.assertEqual(response.content, b'ok')
        mock_popen.assert_called_once_with(
            ['dig', 'example.com; rm -rf /'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        mock_render.assert_called_once()

    @patch('introduction.other_views.render', return_value=HttpResponse('ok'))
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_list_for_nslookup(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'nslookup output', b'')

        response = cmd_lab3(self._make_request('win'))

        self.assertEqual(response.content, b'ok')
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com; rm -rf /'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        mock_render.assert_called_once()
