import subprocess

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='cmduser', password='StrongPass123!')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup ok', b'')

        response = self.client.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(['nslookup', 'example.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertContains(response, 'lookup ok')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_popen(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; id', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Invalid domain. Please enter a valid hostname.')
