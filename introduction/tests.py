from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
import subprocess


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'example output', b'')

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(['dig', 'example.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertContains(response, 'example output')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_unsafe_domain(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; id', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Invalid domain')
