from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CommandInjectionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='StrongPass123!'
        )
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_shell_metacharacters(self):
        malicious_domain = 'example.com;id'

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {
                'domain': malicious_domain,
                'os': 'linux',
            })

        mock_popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        self.assertNotContains(response, malicious_domain)
