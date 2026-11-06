from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabValidationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='cmdlabuser',
            password='StrongPass123!'
        )
        logged_in = self.client.login(username='cmdlabuser', password='StrongPass123!')
        self.assertTrue(logged_in)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post(
            '/cmd_lab',
            {
                'domain': 'example.com; id',
                'os': 'linux',
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
