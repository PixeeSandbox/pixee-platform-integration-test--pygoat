from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabCommandInjectionTest(TestCase):
    def test_rejects_malicious_domain_before_creating_process(self):
        request = RequestFactory().post('/cmd_lab/', {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'win',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.views.subprocess.Popen') as popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
