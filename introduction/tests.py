from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import MagicMock, patch


class TestCmdLab(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='cmduser', password='password123')
        self.client.login(username='cmduser', password='password123')

    def test_cmd_lab_uses_argv_without_shell_for_valid_domain(self):
        process = MagicMock()
        process.communicate.return_value = (b'lookup ok', b'')

        with patch('introduction.views.subprocess.Popen', return_value=process) as mock_popen:
            response = self.client.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)

    def test_cmd_lab_rejects_malicious_domain(self):
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'linux'})

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
