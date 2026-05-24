from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from . import views


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _request(self, domain, os_name):
        request = self.factory.post('/cmd_lab', {'domain': domain, 'os': os_name})
        request.user = SimpleNamespace(is_authenticated=True)
        return request

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_linux(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse('ok')

        response = views.cmd_lab(self._request('https://www.example.com/path', 'linux'))

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_windows(self, mock_popen, mock_render):
        process = MagicMock()
        process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process
        mock_render.return_value = HttpResponse('ok')

        response = views.cmd_lab(self._request('http://www.example.com', 'win'))

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_invalid_domain_before_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = HttpResponse('Something went wrong')

        response = views.cmd_lab(self._request('example.com;rm -rf /', 'linux'))

        mock_popen.assert_not_called()
        self.assertIn('Something went wrong', response.content.decode())
