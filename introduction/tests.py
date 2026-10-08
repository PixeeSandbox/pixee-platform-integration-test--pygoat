from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

import introduction.views as views


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='testpassword123',
        )
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_shell_metacharacters(self):
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post(
                '/cmd_lab',
                {'domain': 'example.com; whoami', 'os': 'win'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_invokes_subprocess_safely(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup ok', b'')

        response = self.client.post(
            '/cmd_lab',
            {'domain': 'example.com', 'os': 'win'},
        )

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup ok')
