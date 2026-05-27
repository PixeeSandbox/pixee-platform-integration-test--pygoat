from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from . import views


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _authenticated_post(self, data):
        request = self.factory.post('/cmd_lab', data)
        request.user = Mock(is_authenticated=True)
        return request

    def test_normalize_domain_extracts_hostname_from_url(self):
        self.assertEqual(views._normalize_domain('https://www.example.com/path?q=1'), 'www.example.com')
        self.assertEqual(views._normalize_domain('example.com:53'), 'example.com')

    def test_invalid_domain_is_rejected_before_subprocess(self):
        request = self._authenticated_post({'domain': 'example.com;rm -rf /', 'os': 'win'})

        with patch('introduction.views.subprocess.Popen') as popen:
            response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_without_shell(self, popen):
        process = Mock()
        process.communicate.return_value = (b'output', b'')
        popen.return_value = process

        request = self._authenticated_post({'domain': 'https://www.example.com', 'os': 'win'})
        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        popen.assert_called_once()
        self.assertEqual(popen.call_args.args[0], ['nslookup', 'www.example.com'])
        self.assertFalse(popen.call_args.kwargs.get('shell', False))
