from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _make_request(self, data):
        request = self.factory.post('/cmd_lab/', data)
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.views.render', return_value=HttpResponse('rendered'))
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_windows(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'windows stdout', b'')

        request = self._make_request({'domain': 'example.com', 'os': 'win'})
        response = cmd_lab(request)

        self.assertEqual(response.content, b'rendered')
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertFalse(mock_popen.call_args.kwargs['shell'])

    @patch('introduction.views.render', return_value=HttpResponse('rendered'))
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_non_windows(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'linux stdout', b'')

        request = self._make_request({'domain': 'example.com', 'os': 'linux'})
        response = cmd_lab(request)

        self.assertEqual(response.content, b'rendered')
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['dig', 'example.com'])
        self.assertFalse(mock_popen.call_args.kwargs['shell'])

    @patch('introduction.views.render', return_value=HttpResponse('rendered'))
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen, mock_render):
        request = self._make_request({'domain': 'example.com; rm -rf /', 'os': 'win'})
        response = cmd_lab(request)

        self.assertEqual(response.content, b'rendered')
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Invalid domain'}
        )
