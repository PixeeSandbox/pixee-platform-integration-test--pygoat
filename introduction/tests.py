from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from unittest.mock import ANY, Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_list_for_valid_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process

        response = self.client.post(reverse('Command Injection Lab'), {
            'domain': 'https://www.example.com',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
        self.assertContains(response, 'example output')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_injection_domain_without_invoking_shell(self, mock_popen):
        response = self.client.post(reverse('Command Injection Lab'), {
            'domain': 'example.com; whoami',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
