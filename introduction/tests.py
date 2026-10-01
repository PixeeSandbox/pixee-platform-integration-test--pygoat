from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.run')
    def test_valid_domain_uses_argument_vector_and_renders_output(self, mock_run):
        mock_run.return_value.stdout = 'resolved\n'
        mock_run.return_value.stderr = 'done\n'

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'resolved')
        self.assertContains(response, 'done')
        self.assertEqual(mock_run.call_count, 1)
        self.assertEqual(mock_run.call_args.args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', mock_run.call_args.kwargs)

    @patch('introduction.other_views.subprocess.run')
    def test_malicious_domain_is_rejected_and_does_not_invoke_subprocess(self, mock_run):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; rm -rf /', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        self.assertEqual(mock_run.call_count, 0)
