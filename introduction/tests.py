from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from unittest.mock import patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='secret123')

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_shell_metacharacters_in_domain(self, mock_run):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_run.assert_not_called()
