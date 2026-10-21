from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3SecurityTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmdlab3user',
            email='cmdlab3user@example.com',
            password='StrongPassword123!'
        )
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain_input(self):
        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post(
                '/cmd_lab3',
                data={'domain': 'example.com; cat /etc/passwd', 'os': 'linux'}
            )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Lab/CMD/cmd_lab.html')
        self.assertContains(response, 'Invalid domain provided')
        mock_popen.assert_not_called()
