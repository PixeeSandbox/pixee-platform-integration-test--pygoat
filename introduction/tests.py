from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch
import subprocess

from . import views


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='testpass123'
        )

    def test_cmd_lab_rejects_malicious_domain_without_popen(self):
        request = self.factory.post('/cmd_lab', data={
            'domain': 'example.com; rm -rf /',
            'os': 'win'
        })
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argument_list_and_shell_false(self):
        request = self.factory.post('/cmd_lab', data={
            'domain': 'example.com',
            'os': 'linux'
        })
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b'example.com\n', b'')

            response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'example.com')
