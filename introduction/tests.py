from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    def _post_request(self, data):
        request = self.factory.post('/cmd_lab', data)
        request.user = self.user
        return request

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen):
        request = self._post_request({'domain': 'example.com; rm -rf /', 'os': 'linux'})

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid domain', response.content)
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_nslookup_with_argv_list(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'nslookup output', b'')
        mock_popen.return_value = process

        request = self._post_request({'domain': 'example.com', 'os': 'win'})

        response = views.cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        process.communicate.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'nslookup output', response.content)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_dig_with_argv_list(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'dig output', b'')
        mock_popen.return_value = process

        request = self._post_request({'domain': 'example.com', 'os': 'linux'})

        response = views.cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        process.communicate.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'dig output', response.content)
