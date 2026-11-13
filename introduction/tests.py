from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabCommandInjectionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test-user', password='test-password')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_domain_with_shell_payload(self, mock_popen):
        response = self.client.post('/cmd_lab', {
            'domain': 'example.com; touch /tmp/pwned',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
