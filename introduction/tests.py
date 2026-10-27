from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import patch

import introduction.other_views as other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='tester', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_vector_for_benign_hostname(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'example.com\n', b'')
        process.returncode = 0

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
        self.assertContains(response, 'example.com')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_invoking_popen(self, mock_popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; id', 'os': 'linux'})

        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
