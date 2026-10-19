import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmduser', password='StrongPass123!')
        self.client.force_login(self.user)
        self.url = reverse('Command Injection Lab')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'stdout', b'')

        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertIn('stdout', response.content.decode())

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(self.url, {'domain': 'example.com;id', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
