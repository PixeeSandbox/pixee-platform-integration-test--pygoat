import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='StrongPass123!')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup result', b'')

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'lookup result')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
