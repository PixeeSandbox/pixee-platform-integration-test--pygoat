from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
import subprocess


class CmdLab3Tests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='cmdlabuser', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_benign_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'example.com lookup', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
