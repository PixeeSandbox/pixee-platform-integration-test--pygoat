from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain_without_invoking_subprocess(self):
        with patch('introduction.other_views.subprocess.run') as mock_run:
            response = self.client.post('/cmd_lab3', {
                'domain': 'example.com; id',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'Something went wrong')
        mock_run.assert_not_called()

    def test_cmd_lab3_uses_argument_list_without_shell_for_valid_domain(self):
        completed = Mock(stdout='resolved\n', stderr='')
        with patch('introduction.other_views.subprocess.run', return_value=completed) as mock_run:
            response = self.client.post('/cmd_lab3', {
                'domain': 'example.com',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'resolved\n')
        mock_run.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            capture_output=True,
            text=True,
        )
