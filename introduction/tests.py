from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import Mock, patch


class CommandInjectionTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='cmduser', password='password123')
        self.assertTrue(self.client.login(username='cmduser', password='password123'))

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, popen_mock):
        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com; whoami', 'os': 'linux'}
        )

        self.assertEqual(response.status_code, 200)
        popen_mock.assert_not_called()
        self.assertContains(response, 'Something went wrong')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, popen_mock):
        process = Mock()
        process.communicate.return_value = (b'mocked output', b'')
        popen_mock.return_value = process

        response = self.client.post(
            reverse('Command Injection Lab'),
            {'domain': 'example.com', 'os': 'linux'}
        )

        self.assertEqual(response.status_code, 200)
        args, kwargs = popen_mock.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertContains(response, 'mocked output')
