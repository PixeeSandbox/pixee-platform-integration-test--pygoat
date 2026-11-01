from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from .other_views import _is_valid_domain


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='securityuser', password='password123')
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_injection_payload(self):
        with patch('introduction.other_views.subprocess.Popen') as mocked_popen:
            response = self.client.post('/cmd_lab3', {'domain': 'example.com;id', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mocked_popen.assert_not_called()

    def test_cmd_lab3_domain_allowlist_helper(self):
        self.assertTrue(_is_valid_domain('example.com'))
        self.assertFalse(_is_valid_domain('example.com;id'))
