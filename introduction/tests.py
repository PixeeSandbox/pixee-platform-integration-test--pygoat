import subprocess
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmduser', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'example output', b'')

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
        self.assertNotIn('shell', kwargs)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_shell_metacharacters_before_popen(self, mock_popen):
        for malicious_domain in ['example.com; id', 'example.com && id']:
            with self.subTest(malicious_domain=malicious_domain):
                mock_popen.reset_mock()
                response = self.client.post('/cmd_lab', {'domain': malicious_domain, 'os': 'win'})

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'Something went wrong')
                mock_popen.assert_not_called()
