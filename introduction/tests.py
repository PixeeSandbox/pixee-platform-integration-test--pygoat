from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_command_syntax_in_domain(self):
        request = RequestFactory().post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.views.subprocess.Popen') as popen:
            response = cmd_lab(request)

        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()
