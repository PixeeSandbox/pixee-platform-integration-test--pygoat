from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='TestPassword123!'
        )
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain_input(self):
        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab3', {
                'domain': 'example.com; rm -rf /',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    def test_cmd_lab3_passes_domain_as_single_argument(self):
        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            process = mock_popen.return_value
            process.communicate.return_value = (b'OK', b'')

            response = self.client.post('/cmd_lab3', {
                'domain': 'example.com',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_popen.call_args[0][0], ['dig', 'example.com'])
        self.assertFalse(mock_popen.call_args[1].get('shell', True))
