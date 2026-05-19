from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='tester', password='pass12345')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_uses_nslookup_for_windows(self, mock_run):
        mock_run.return_value = SimpleNamespace(stdout='ok\n', stderr='')

        response = self.client.post(reverse('Command Injection Lab'), {'domain': 'https://www.example.com:443', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(['nslookup', 'example.com'], capture_output=True, text=True)

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_accepts_port_bearing_domain(self, mock_run):
        mock_run.return_value = SimpleNamespace(stdout='ok\n', stderr='')

        response = self.client.post(reverse('Command Injection Lab'), {'domain': '127.0.0.1:53', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(['dig', '127.0.0.1'], capture_output=True, text=True)

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_uses_dig_for_non_windows(self, mock_run):
        mock_run.return_value = SimpleNamespace(stdout='ok\n', stderr='')

        response = self.client.post(reverse('Command Injection Lab'), {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(['dig', 'example.com'], capture_output=True, text=True)

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_injection_payload(self, mock_run):
        response = self.client.post(reverse('Command Injection Lab'), {'domain': 'example.com;rm -rf /', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_run.assert_not_called()

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_invalid_port(self, mock_run):
        response = self.client.post(reverse('Command Injection Lab'), {'domain': 'example.com:70000', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_run.assert_not_called()
