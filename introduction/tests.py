import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'valid output', b'')
        mock_render.return_value = HttpResponse('ok')

        request = self.factory.post('/cmd_lab3/', {
            'domain': 'example.com',
            'os': 'win',
        })
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('Something went wrong')

        request = self.factory.post('/cmd_lab3/', {
            'domain': 'example.com; rm -rf /',
            'os': 'win',
        })
        request.user = self.user

        response = cmd_lab3(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertIn('Something went wrong', response.content.decode())
