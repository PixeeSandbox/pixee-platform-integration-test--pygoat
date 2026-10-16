import subprocess
from django.contrib.auth.models import User
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_malicious_domain_without_subprocess(self):
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {
                'domain': 'example.com; rm -rf /',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argument_array_for_valid_domain(self):
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b'lookup output', b'')
            response = self.client.post('/cmd_lab', {
                'domain': 'example.com',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'lookup output')
