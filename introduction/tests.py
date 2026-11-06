from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import ANY, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username='cmdlabuser',
            password='testpassword123',
        )
        self.assertTrue(self.client.login(username='cmdlabuser', password='testpassword123'))
        self.url = reverse('Command Injection Lab')

    def test_cmd_lab_uses_argv_without_shell_for_safe_domain(self):
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b'mocked nslookup output', b'')

            response = self.client.post(
                self.url,
                {'domain': 'example.com', 'os': 'win'},
            )

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
        self.assertContains(response, 'mocked nslookup output')

    def test_cmd_lab_rejects_malicious_domain_without_running_subprocess(self):
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post(
                self.url,
                {'domain': 'example.com; whoami', 'os': 'win'},
            )

        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
