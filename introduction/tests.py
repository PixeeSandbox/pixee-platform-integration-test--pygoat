import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username='testuser',
            password='testpass123',
        )
        self.assertTrue(self.client.login(username='testuser', password='testpass123'))

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_invokes_popen_with_argument_list(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'example output', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)

    @patch('introduction.other_views.subprocess.Popen')
    def test_injected_domain_is_rejected_before_popen(self, mock_popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; id', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
