from django.test import TestCase, RequestFactory
from types import SimpleNamespace
from unittest.mock import patch

import introduction.other_views as other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_without_shell(self, mock_popen, mock_render):
        mock_process = SimpleNamespace(communicate=lambda: (b'example output', b''))
        mock_popen.return_value = mock_process
        mock_render.return_value = SimpleNamespace(status_code=200)

        request = self.factory.post('/cmd_lab3/', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], other_views.subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], other_views.subprocess.PIPE)
        mock_render.assert_called_once()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = SimpleNamespace(status_code=200)

        request = self.factory.post('/cmd_lab3/', {'domain': 'https://www.example.com; rm -rf /', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Something went wrong'}
        )
