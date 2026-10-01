from django.test import TestCase, RequestFactory
from unittest.mock import MagicMock, patch

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _build_request(self, domain, os_name):
        request = self.factory.post('/cmd_lab', {'domain': domain, 'os': os_name})
        request.user = MagicMock(is_authenticated=True)
        return request

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_vector_for_windows(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process
        mock_render.return_value = MagicMock()

        request = self._build_request(' https://www.example.com ', 'win')
        views.cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        mock_render.assert_called_once()

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_vector_for_non_windows(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b'dig output', b'')
        mock_popen.return_value = process
        mock_render.return_value = MagicMock()

        request = self._build_request(' https://www.example.com ', 'linux')
        views.cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        mock_render.assert_called_once()

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_invalid_domain(self, mock_popen, mock_render):
        mock_render.return_value = MagicMock()

        request = self._build_request('example.com; rm -rf /', 'linux')
        views.cmd_lab(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'},
        )
