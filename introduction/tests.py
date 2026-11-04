from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_malicious_domain(self, mock_popen):
        self.client.force_login(self.user)
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com;rm -rf /',
            'os': 'linux'
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Lab/CMD/cmd_lab.html')
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
