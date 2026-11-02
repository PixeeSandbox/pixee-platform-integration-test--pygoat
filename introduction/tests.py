from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import ANY, Mock, patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_cmd_lab3_rejects_malicious_domain_and_accepts_safe_lookup(self):
        self.client.force_login(self.user)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = self.client.post('/cmd_lab3', {
                'domain': 'https://www.example.com; rm -rf /',
                'os': 'win',
            })
            popen.assert_not_called()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain supplied')

        process = Mock()
        process.communicate.return_value = (b'example output', b'')
        with patch('introduction.other_views.subprocess.Popen', return_value=process) as popen:
            response = self.client.post('/cmd_lab3', {
                'domain': 'https://www.example.com',
                'os': 'win',
            })
            popen.assert_called_once_with(['nslookup', 'example.com'], stdout=ANY, stderr=ANY)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'example output')
