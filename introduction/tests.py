from django.test import TestCase, RequestFactory
from unittest.mock import MagicMock, patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_without_shell(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'example output', b'')
        mock_popen.return_value = process

        request = self.factory.post('/cmd_lab/', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = MagicMock(is_authenticated=True)

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
