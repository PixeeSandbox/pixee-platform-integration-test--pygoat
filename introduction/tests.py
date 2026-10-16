import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='testpass123'
        )
        self.client.force_login(self.user)

    def test_cmd_lab_uses_argv_list_for_valid_domain(self):
        process = Mock()
        process.communicate.return_value = (b'example.com has address 93.184.216.34\n', b'')

        with patch('introduction.views.subprocess.Popen', return_value=process) as mock_popen:
            response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('example.com has address 93.184.216.34', response.content.decode())
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
        self.assertNotIn('shell', kwargs)

    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self):
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {'domain': 'example.com; id', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('Something went wrong', response.content.decode())
        mock_popen.assert_not_called()
