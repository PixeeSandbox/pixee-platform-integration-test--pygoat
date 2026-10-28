from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_valid_hostname_uses_argument_list(self, mock_popen):
        mock_process = SimpleNamespace(communicate=lambda: (b'ok', b''))
        mock_popen.return_value = mock_process

        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_popen.called)
        self.assertEqual(mock_popen.call_args[0][0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_dash_prefixed_hostname_rejected_before_popen(self, mock_popen):
        request = self.factory.post('/cmd_lab3/', {'domain': '-x.example.com', 'os': 'win'})
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_popen.called)
