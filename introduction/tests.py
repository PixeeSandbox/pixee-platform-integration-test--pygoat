from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from unittest.mock import patch
from django.http import HttpResponse

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password123')

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('ok')
        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'win'})
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[1], 'Lab/CMD/cmd_lab.html')
        self.assertEqual(mock_render.call_args.args[2], {'output': 'Something went wrong'})
