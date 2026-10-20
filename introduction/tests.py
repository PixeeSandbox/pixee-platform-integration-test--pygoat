from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase, RequestFactory

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen, mock_render):
        request = self.factory.post('/cmd_lab3/', data={
            'domain': 'example.com; rm -rf /',
            'os': 'linux',
        })
        request.user = SimpleNamespace(is_authenticated=True)
        mock_render.return_value = 'rendered-response'

        response = cmd_lab3(request)

        self.assertEqual(response, 'rendered-response')
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'}
        )

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_popen, mock_render):
        process = mock_popen.return_value
        process.communicate.return_value = (b'answer', b'')
        request = self.factory.post('/cmd_lab3/', data={
            'domain': 'example.com',
            'os': 'linux',
        })
        request.user = SimpleNamespace(is_authenticated=True)
        mock_render.return_value = 'rendered-response'

        response = cmd_lab3(request)

        self.assertEqual(response, 'rendered-response')
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=mock_popen.call_args.kwargs['stdout'],
            stderr=mock_popen.call_args.kwargs['stderr'],
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'answer'}
        )
