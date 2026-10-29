from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_malicious_domain_input(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as mocked_popen:
            response = self.client.post('/cmd_lab3', {'domain': 'example.com;id', 'os': 'linux'})

        self.assertContains(response, 'Something went wrong')
        mocked_popen.assert_not_called()
