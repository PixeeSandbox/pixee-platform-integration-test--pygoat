from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch
import subprocess


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmduser', password='testpass123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen):
        mock_process = Mock()
        mock_process.communicate.return_value = (b'example.com answer', b'')
        mock_popen.return_value = mock_process

        response = self.client.post(reverse('Command Injection Lab'), {
            'domain': 'https://www.example.com',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(reverse('Command Injection Lab'), {
            'domain': 'example.com; id',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
