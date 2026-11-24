from unittest.mock import patch

from django.test import RequestFactory, TestCase
from types import SimpleNamespace

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacters(self, mock_popen):
        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'linux',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Invalid domain')
        mock_popen.assert_not_called()
