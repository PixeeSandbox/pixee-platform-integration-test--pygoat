from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='cmduser', password='StrongPass123!')
        self.client.force_login(self.user)
        self.url = '/cmd_lab3'

    def test_cmd_lab3_rejects_malicious_domain_without_running_subprocess(self):
        payload = 'example.com; cat /etc/passwd'
        with patch('introduction.other_views.subprocess.run') as mock_run, patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post(self.url, {'domain': payload, 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_run.assert_not_called()
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argument_list_for_valid_domain(self):
        completed = type('CompletedProcess', (), {'stdout': 'lookup ok', 'stderr': ''})()
        with patch('introduction.other_views.subprocess.run', return_value=completed) as mock_run:
            response = self.client.post(self.url, {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lookup ok')
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
