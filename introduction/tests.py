from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    def _post(self, domain, os_name):
        request = self.factory.post('/cmd_lab', {'domain': domain, 'os': os_name})
        request.user = self.user
        return request

    def _render_stub(self, request, template_name, context=None, **kwargs):
        return HttpResponse((context or {}).get('output', ''))

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_vector_for_hostname(self, popen_mock, render_mock):
        process = Mock()
        process.communicate.return_value = (b'lookup ok', b'')
        popen_mock.return_value = process
        render_mock.side_effect = self._render_stub

        response = views.cmd_lab(self._post('example.com', 'win'))

        self.assertEqual(popen_mock.call_args.args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', popen_mock.call_args.kwargs)
        self.assertEqual(response.content.decode(), 'lookup ok')

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_accepts_ipv4_literal(self, popen_mock, render_mock):
        process = Mock()
        process.communicate.return_value = (b'ipv4 ok', b'')
        popen_mock.return_value = process
        render_mock.side_effect = self._render_stub

        response = views.cmd_lab(self._post('127.0.0.1', 'linux'))

        self.assertEqual(popen_mock.call_args.args[0], ['dig', '127.0.0.1'])
        self.assertEqual(response.content.decode(), 'ipv4 ok')

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_accepts_ipv6_literal(self, popen_mock, render_mock):
        process = Mock()
        process.communicate.return_value = (b'ipv6 ok', b'')
        popen_mock.return_value = process
        render_mock.side_effect = self._render_stub

        response = views.cmd_lab(self._post('2001:db8::1', 'linux'))

        self.assertEqual(popen_mock.call_args.args[0], ['dig', '2001:db8::1'])
        self.assertEqual(response.content.decode(), 'ipv6 ok')

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_strips_numeric_port(self, popen_mock, render_mock):
        process = Mock()
        process.communicate.return_value = (b'port ok', b'')
        popen_mock.return_value = process
        render_mock.side_effect = self._render_stub

        response = views.cmd_lab(self._post('example.com:80', 'win'))

        self.assertEqual(popen_mock.call_args.args[0], ['nslookup', 'example.com'])
        self.assertEqual(response.content.decode(), 'port ok')

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_or_url_like_inputs(self, popen_mock, render_mock):
        render_mock.side_effect = self._render_stub

        for domain in ['example.com;rm -rf /', '-bad.example', 'https://example.com:443/path']:
            with self.subTest(domain=domain):
                response = views.cmd_lab(self._post(domain, 'linux'))
                self.assertEqual(response.content.decode(), 'Something went wrong')

        popen_mock.assert_not_called()
