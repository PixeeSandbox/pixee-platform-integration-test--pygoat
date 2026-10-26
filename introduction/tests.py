from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='testuser',
            password='testpassword123',
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_run):
        response = self.client.post(
            '/cmd_lab3',
            {'domain': 'example.com; whoami', 'os': 'linux'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_run.assert_not_called()

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_argument_vector(self, mock_run):
        mock_run.return_value.stdout = 'resolved\n'
        mock_run.return_value.stderr = ''

        response = self.client.post(
            '/cmd_lab3',
            {'domain': 'https://www.example.com', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'resolved')
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertTrue(kwargs['capture_output'])
        self.assertTrue(kwargs['text'])
        self.assertFalse(kwargs['check'])
