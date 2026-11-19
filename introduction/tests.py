from unittest.mock import patch
from types import SimpleNamespace

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.views.subprocess.Popen')
    def test_rejects_domain_with_shell_metacharacter(self, mock_popen):
        request = self.factory.post('/cmd_lab/', {
            'domain': 'example.com;id',
            'os': 'linux',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
