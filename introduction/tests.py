from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_shell_injection_domain(self, mock_popen):
        request = self.factory.post('/cmd_lab/', {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'win',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Invalid domain', status_code=400)
        mock_popen.assert_not_called()
