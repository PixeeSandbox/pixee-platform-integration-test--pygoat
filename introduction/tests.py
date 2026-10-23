from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_shell_metacharacters(self, mock_popen):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; id', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Something went wrong', response.content)
        mock_popen.assert_not_called()
