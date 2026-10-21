from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdtester',
            password='safepass123',
        )

    def test_cmd_lab_rejects_shell_metacharacters(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; id', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mocked_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Something went wrong', response.content)
        mocked_popen.assert_not_called()

    def test_cmd_lab_rejects_leading_dash_domain(self):
        request = self.factory.post('/cmd_lab', {'domain': '-example.com', 'os': 'win'})
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mocked_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Something went wrong', response.content)
        mocked_popen.assert_not_called()
