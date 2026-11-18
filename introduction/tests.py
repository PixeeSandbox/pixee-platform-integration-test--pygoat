from django.test import RequestFactory, TestCase
from types import SimpleNamespace
from unittest.mock import patch

from introduction.views import cmd_lab


class CommandInjectionTests(TestCase):
    def test_cmd_lab_rejects_shell_injection_domain(self):
        request = RequestFactory().post('/cmd_lab', {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'linux',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.views.subprocess.Popen') as popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
