from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from unittest.mock import patch
import subprocess
from introduction import other_views


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlabtester',
            password='testpassword123'
        )

    def test_malicious_domain_is_rejected_without_subprocess(self):
        request = self.factory.post('/cmd_lab', {
            'domain': 'example.com; rm -rf /',
            'os': 'linux',
        })
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertIn(b'Something went wrong', response.content)

    def test_valid_domain_uses_safe_subprocess_invocation(self):
        request = self.factory.post('/cmd_lab', {
            'domain': 'example.com',
            'os': 'win',
        })
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            mock_popen.return_value.communicate.return_value = (b'lookup output', b'')
            response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        called_args, called_kwargs = mock_popen.call_args
        self.assertEqual(called_args[0], ['nslookup', 'example.com'])
        self.assertFalse(called_kwargs['shell'])
        self.assertEqual(called_kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(called_kwargs['stderr'], subprocess.PIPE)
        self.assertIn(b'lookup output', response.content)
