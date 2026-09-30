from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from django.contrib.auth.models import User
from unittest.mock import Mock, patch
import subprocess

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password')

    def _make_request(self, domain, os_value):
        request = self.factory.post('/cmd_lab3/', {'domain': domain, 'os': os_value})
        request.user = self.user
        return request

    @patch('introduction.other_views.render', return_value=HttpResponse('ok'))
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_safe_domain(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process

        request = self._make_request('https://www.example.com', 'linux')
        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.other_views.render', return_value=HttpResponse('ok'))
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_nslookup_for_windows_safe_domain(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process

        request = self._make_request('example.org', 'win')
        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.org'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.other_views.render', return_value=HttpResponse('ok'))
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        request = self._make_request('example.com; rm -rf /', 'linux')
        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
