from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import Mock, patch

import subprocess


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='testpass123')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_safe_domain(self, mock_popen):
        self.client.force_login(self.user)
        mock_process = Mock()
        mock_process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = mock_process

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertTemplateUsed(response, 'Lab/CMD/cmd_lab.html')
        self.assertEqual(response.context['output'], 'example output')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_executing(self, mock_popen):
        self.client.force_login(self.user)

        response = self.client.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertTemplateUsed(response, 'Lab/CMD/cmd_lab.html')
        self.assertEqual(response.context['output'], 'Invalid domain')
