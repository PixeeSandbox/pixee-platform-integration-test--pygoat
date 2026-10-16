from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='StrongPass123!'
        )
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_list_and_disables_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = ('lookup output', '')

        response = self.client.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))
        self.assertTrue(kwargs.get('text', False))

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_shell_metacharacters_before_subprocess(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
