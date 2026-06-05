from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _request(self, domain, target_os):
        request = self.factory.post('/cmd_lab/', {'domain': domain, 'os': target_os})
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    def test_cmd_lab_rejects_shell_injection_payload(self):
        request = self._request('example.com;id', 'win')

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 400)

    def test_cmd_lab_rejects_url_with_path(self):
        request = self._request('https://example.com/path', 'win')

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 400)

    @patch('introduction.views.render', return_value=HttpResponse('ok'))
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_nslookup(self, mock_popen, _mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'out', b'err')

        request = self._request('https://www.example.com/', 'win')
        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'www.example.com'])
        self.assertNotIn('shell', kwargs)

    @patch('introduction.views.render', return_value=HttpResponse('ok'))
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_dig_ip_literal(self, mock_popen, _mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'out', b'err')

        request = self._request('8.8.8.8', 'linux')
        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', '8.8.8.8'])
        self.assertNotIn('shell', kwargs)
