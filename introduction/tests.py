import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username='tester', password='password123')

    def setUp(self):
        self.factory = RequestFactory()

    def _post_request(self, domain, os_value='linux'):
        request = self.factory.post('/cmd_lab', {'domain': domain, 'os': os_value})
        request.user = self.user
        return request

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen):
        request = self._post_request('example.com; rm -rf /')

        response = cmd_lab(request)

        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_safe_argv_for_valid_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')
        request = self._post_request('example.com', 'win')

        response = cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'lookup output')
