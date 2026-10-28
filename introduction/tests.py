from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123',
        )
        self.url = '/cmd_lab'

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_valid_domain_uses_argument_list(self, popen_mock):
        process = Mock()
        process.communicate.return_value = (b'example output', b'')
        popen_mock.return_value = process
        self.client.force_login(self.user)

        response = self.client.post(self.url, {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'example output')
        popen_mock.assert_called_once()
        self.assertEqual(popen_mock.call_args[0][0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', popen_mock.call_args[1])
        self.assertIn('stdout', popen_mock.call_args[1])
        self.assertIn('stderr', popen_mock.call_args[1])

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_popen(self, popen_mock):
        self.client.force_login(self.user)

        response = self.client.post(self.url, {'domain': 'example.com; rm -rf /', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        popen_mock.assert_not_called()
