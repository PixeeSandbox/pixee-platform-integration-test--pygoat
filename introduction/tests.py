from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(self.user)

    def test_rejects_malicious_domain_without_invoking_subprocess(self):
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    def test_executes_fixed_command_with_argv_list(self):
        process = type('Process', (), {'communicate': lambda self: (b'lookup ok', b'')})()
        with patch('introduction.views.subprocess.Popen', return_value=process) as mock_popen:
            response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        called_args, called_kwargs = mock_popen.call_args
        self.assertIsInstance(called_args[0], list)
        self.assertEqual(called_args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', called_kwargs)
        self.assertContains(response, 'lookup ok')
