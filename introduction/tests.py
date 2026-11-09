from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch
import subprocess


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='password123'
        )
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; id',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_valid_hostname(self, mock_popen):
        process_mock = Mock()
        process_mock.communicate.return_value = (b'example.com lookup', b'')
        mock_popen.return_value = process_mock

        response = self.client.post('/cmd_lab', {
            'domain': 'example.com',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'example.com lookup')
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
