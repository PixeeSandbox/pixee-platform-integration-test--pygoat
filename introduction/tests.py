from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import ANY, MagicMock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_without_shell(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(['dig', 'example.com'], stdout=ANY, stderr=ANY)
        self.assertEqual(response.context['output'], 'example output')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen):
        response = self.client.post(
            '/cmd_lab',
            {'domain': 'https://www.example.com; rm -rf /', 'os': 'linux'},
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertEqual(response.context['output'], 'Something went wrong')
