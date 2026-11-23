from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLab3RegressionTests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='tester', password='StrongPass123!')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_executing_command(self, mock_popen):
        response = self.client.post('/cmd_lab3', {
            'domain': 'https://www.example.com; cat /etc/passwd',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'example output', b'')

        response = self.client.post('/cmd_lab3', {
            'domain': 'https://www.example.com',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        called_args, called_kwargs = mock_popen.call_args
        self.assertEqual(called_args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', called_kwargs)
        self.assertIn('stdout', called_kwargs)
        self.assertIn('stderr', called_kwargs)
        self.assertContains(response, 'example output')
