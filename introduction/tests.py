from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_cmd_lab3_rejects_shell_metacharacters_in_domain(self):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com;id', 'os': 'linux'}
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mocked_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mocked_popen.assert_not_called()
