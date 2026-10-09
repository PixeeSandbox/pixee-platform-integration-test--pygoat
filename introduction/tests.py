import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='tester', password='password')
        self.client.force_login(self.user)

    def test_cmd_lab3_allows_safe_domain_with_argument_list(self):
        mock_process = Mock()
        mock_process.communicate.return_value = (b'lookup ok', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=mock_process) as mock_popen:
            response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup ok')
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_cmd_lab3_rejects_shell_metacharacters(self):
        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab3', {'domain': 'example.com; id', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
