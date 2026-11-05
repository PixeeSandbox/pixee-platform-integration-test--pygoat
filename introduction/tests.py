from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from . import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _build_request(self, data):
        request = self.factory.post('/cmd_lab3/', data)
        request.user = Mock(is_authenticated=True)
        return request

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen, mock_render):
        mock_render.return_value = 'error-response'
        request = self._build_request({'domain': 'example.com; rm -rf /', 'os': 'win'})

        response = other_views.cmd_lab3(request)

        self.assertEqual(response, 'error-response')
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'},
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_without_shell(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process
        mock_render.return_value = 'success-response'
        request = self._build_request({'domain': 'https://www.example.com', 'os': 'win'})

        response = other_views.cmd_lab3(request)

        self.assertEqual(response, 'success-response')
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'lookup output'},
        )
