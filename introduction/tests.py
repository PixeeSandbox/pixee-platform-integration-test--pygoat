from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_cmd_lab3_rejects_malicious_domain(self):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com;id', 'os': 'linux'}
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = other_views.cmd_lab3(request)

        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
