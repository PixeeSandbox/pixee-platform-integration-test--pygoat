from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(self.user)

    def test_rejects_malicious_domain_without_invoking_popen(self):
        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    def test_valid_domain_uses_argument_list_and_disables_shell(self):
        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            mock_popen.return_value.communicate.return_value = (b'lookup ok', b'')

            response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))
        self.assertEqual(kwargs['stdout'], -1)
        self.assertEqual(kwargs['stderr'], -1)
        self.assertContains(response, 'lookup ok')
