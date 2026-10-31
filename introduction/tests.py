from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Password123!'
        )
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_malicious_domain(self, mock_run):
        response = self.client.post('/cmd_lab', {
            'domain': 'example.com;whoami',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_run.assert_not_called()
