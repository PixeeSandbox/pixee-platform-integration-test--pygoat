from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.assertTrue(self.client.login(username='testuser', password='testpass123'))

    def test_cmd_lab_rejects_malicious_domain(self):
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {
                'domain': 'example.com; rm -rf /',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argument_list_and_shell_false(self):
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            mock_process_instance = mock_popen.return_value
            mock_process_instance.communicate.return_value = (b'output', b'')

            response = self.client.post('/cmd_lab', {
                'domain': 'example.com',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs['shell'])
