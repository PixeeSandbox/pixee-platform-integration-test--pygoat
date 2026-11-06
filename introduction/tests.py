from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from unittest.mock import ANY, MagicMock, patch


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='cmduser', password='strong-password-123')
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain_without_invoking_subprocess(self):
        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = self.client.post('/cmd_lab3', {'domain': 'example.com; id', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        popen.assert_not_called()

    def test_cmd_lab3_uses_argv_invocation_and_renders_subprocess_output(self):
        process = MagicMock()
        process.communicate.return_value = (b'lookup output\n', b'lookup warning\n')

        with patch('introduction.other_views.subprocess.Popen', return_value=process) as popen:
            response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once_with(['nslookup', 'example.com'], stdout=ANY, stderr=ANY)
        self.assertContains(response, 'lookup output')
        self.assertContains(response, 'lookup warning')
