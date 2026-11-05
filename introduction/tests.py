import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='StrongPass123!'
        )
        logged_in = self.client.login(username='cmduser', password='StrongPass123!')
        self.assertTrue(logged_in)
        self.url = '/cmd_lab3'

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list(self, mock_popen):
        process_mock = mock_popen.return_value
        process_mock.communicate.return_value = (b'example output', b'')

        response = self.client.post(
            self.url,
            {'domain': 'https://www.Example.com/', 'os': 'win'}
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.assertContains(response, 'example output')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_injected_domain(self, mock_popen):
        response = self.client.post(
            self.url,
            {'domain': 'example.com;id', 'os': 'linux'}
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Invalid domain supplied')
