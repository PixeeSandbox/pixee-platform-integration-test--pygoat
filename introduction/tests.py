from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import MagicMock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='tester', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_injected_domain_without_invoking_subprocess(self, mock_popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com;whoami', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'Something went wrong')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_allowed_domain_uses_argument_list_and_shell_false(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'lookup ok', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'lookup ok')
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertFalse(mock_popen.call_args.kwargs['shell'])
