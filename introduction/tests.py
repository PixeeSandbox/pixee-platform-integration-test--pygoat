from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='password123'
        )

    def test_cmd_lab_rejects_shell_metacharacters(self):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com; id', 'os': 'win'}
        )
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain provided')
        mock_popen.assert_not_called()
