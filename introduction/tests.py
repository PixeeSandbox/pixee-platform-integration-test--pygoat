from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import ANY, Mock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_cmd_lab3_rejects_malicious_domain(self):
        self.client.force_login(self.user)

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab3', {
                'domain': 'example.com; rm -rf /',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argument_list_for_valid_domain(self):
        self.client.force_login(self.user)
        process = Mock()
        process.communicate.return_value = (b'example output', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=process) as mock_popen:
            response = self.client.post('/cmd_lab3', {
                'domain': 'example.com',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=ANY,
            stderr=ANY,
        )
        self.assertContains(response, 'example output')
