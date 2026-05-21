from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    def _post(self, data):
        request = self.factory.post('/cmd_lab', data)
        request.user = self.user
        return request

    def test_validate_cmd_domain_accepts_safe_hostnames_and_ips(self):
        self.assertEqual(views._validate_cmd_domain('https://www.example.com'), 'example.com')
        self.assertEqual(views._validate_cmd_domain('8.8.8.8'), '8.8.8.8')
        self.assertEqual(views._validate_cmd_domain('[2001:db8::1]'), '2001:db8::1')

    def test_validate_cmd_domain_rejects_injection_payloads(self):
        for value in ['', ' -foo', ';id', 'example.com;id', 'example.com | cat /etc/passwd']:
            with self.subTest(value=value):
                self.assertIsNone(views._validate_cmd_domain(value))

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_and_decodes_output(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'stdout', b'stderr')
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse('rendered')

        request = self._post({'domain': 'example.com', 'os': 'win'})
        response = views.cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        self.assertEqual(response.content, b'rendered')
        self.assertEqual(mock_render.call_args[0][2], {'output': 'stdoutstderr'})

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_invalid_domain_before_invoking_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('rendered')

        request = self._post({'domain': ';id', 'os': 'win'})
        response = views.cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.content, b'rendered')
        self.assertEqual(mock_render.call_args[0][2], {'output': 'Something went wrong'})

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_unsupported_os_before_invoking_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('rendered')

        request = self._post({'domain': 'example.com', 'os': 'mac'})
        response = views.cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertEqual(response.content, b'rendered')
        self.assertEqual(mock_render.call_args[0][2], {'output': 'Something went wrong'})
