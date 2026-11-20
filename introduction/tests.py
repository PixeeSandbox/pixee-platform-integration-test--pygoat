import subprocess
from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Mock(is_authenticated=True)

    def test_cmd_lab_rejects_malicious_domain_without_subprocess(self):
        request = self.factory.post('/cmd_lab', {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'linux',
        })
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    def test_cmd_lab_passes_valid_domain_as_safe_arguments(self):
        request = self.factory.post('/cmd_lab', {
            'domain': 'example.com',
            'os': 'linux',
        })
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as popen:
            popen.return_value.communicate.return_value = (b'lookup output', b'')
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
