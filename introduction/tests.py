from unittest.mock import patch
from types import SimpleNamespace

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_popen):
        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com; whoami',
            'os': 'linux',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
