from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_login(self.user)
        self.url = '/cmd_lab3'

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_popen(self, mock_popen):
        response = self.client.post(
            self.url,
            {'domain': 'example.com; id', 'os': 'linux'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_vector_for_valid_domain(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')

        for os_value, expected_command in (
            ('win', ['nslookup', 'example.com']),
            ('linux', ['dig', 'example.com']),
        ):
            with self.subTest(os=os_value):
                mock_popen.reset_mock()
                response = self.client.post(
                    self.url,
                    {'domain': 'https://www.example.com', 'os': os_value}
                )

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'lookup output')
                mock_popen.assert_called_once()
                args, kwargs = mock_popen.call_args
                self.assertEqual(args[0], expected_command)
                self.assertFalse(kwargs['shell'])
