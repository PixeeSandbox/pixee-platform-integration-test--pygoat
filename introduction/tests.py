from django.test import TestCase, RequestFactory
from unittest.mock import patch, MagicMock
from django.http import HttpResponse

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _build_authenticated_request(self, domain, os_value):
        request = self.factory.post('/cmd_lab/', {'domain': domain, 'os': os_value})
        request.user = MagicMock(is_authenticated=True)
        return request

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_list_for_shell_metacharacters(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'lookup ok', b'')
        mock_popen.return_value = process

        request = self._build_authenticated_request('example.com;rm -rf /', 'linux')
        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com;rm -rf /'])
        self.assertNotIn('shell', kwargs)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_nslookup_without_shell_on_windows_branch(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'win out', b'')
        mock_popen.return_value = process

        request = self._build_authenticated_request('example.com', 'win')
        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_returns_rendered_output(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b'stdout-', b'stderr')
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse('rendered')

        request = self._build_authenticated_request('example.com', 'linux')
        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'stdout-stderr'})
