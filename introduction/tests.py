from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        request = self.factory.post('/cmd_lab', {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'win',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        cmd_lab(request)

        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_invokes_lookup_without_shell(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'lookup output', b'')
        request = self.factory.post('/cmd_lab', {
            'domain': 'example.com',
            'os': 'win',
        })
        request.user = SimpleNamespace(is_authenticated=True)

        cmd_lab(request)

        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertIs(kwargs['shell'], False)

