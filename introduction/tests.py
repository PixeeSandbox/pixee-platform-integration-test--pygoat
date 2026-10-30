from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='StrongPass123!'
        )
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_without_shell_for_safe_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'safe output', b'')

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_injected_domain_before_process_execution(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com;whoami', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
