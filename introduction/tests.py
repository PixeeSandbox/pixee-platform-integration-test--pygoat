from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmduser', password='safe-password123')

    def test_cmd_lab_rejects_injection_style_domain(self):
        self.assertTrue(self.client.login(username='cmduser', password='safe-password123'))

        with patch('introduction.views.subprocess.Popen') as popen_mock:
            response = self.client.post('/cmd_lab', {'domain': 'example.com;whoami', 'os': 'linux'})

        self.assertFalse(popen_mock.called)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
