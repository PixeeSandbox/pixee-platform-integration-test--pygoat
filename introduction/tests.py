from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='tester', password='testerpass123')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_list_for_safe_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup output', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertIsInstance(args[0], list)
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertContains(response, 'lookup output')

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_shell_metacharacters_without_subprocess_call(self, mock_popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
