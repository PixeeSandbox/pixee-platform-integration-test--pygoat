from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
        )
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain(self):
        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post(
                '/cmd_lab3',
                {'domain': 'example.com; id', 'os': 'linux'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_safe_argument_list_for_valid_domain(self):
        process_mock = Mock()
        process_mock.communicate.return_value = (b'valid output', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=process_mock) as mock_popen:
            response = self.client.post(
                '/cmd_lab3',
                {'domain': 'example.com', 'os': 'win'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'valid output')
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
