from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase


class CommandInjectionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='cmdtest', password='password123')
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain(self):
        malicious_domain = 'https://www.example.com;whoami'

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab3', {'domain': malicious_domain, 'os': 'linux'})

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
