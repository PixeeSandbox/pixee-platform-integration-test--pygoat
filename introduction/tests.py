from django.test import RequestFactory, TestCase
from types import SimpleNamespace
from unittest.mock import patch

import introduction.other_views as views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cmd_lab3_uses_argument_list_without_shell(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.other_views.subprocess.Popen') as mock_popen, patch('introduction.other_views.render') as mock_render:
            process = SimpleNamespace(communicate=lambda: (b'out', b'err'))
            mock_popen.return_value = process
            mock_render.return_value = views.HttpResponse('ok')

            response = views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_popen.called)
        self.assertEqual(mock_popen.call_args[0][0], ['nslookup', 'example.com'])
        self.assertFalse(mock_popen.call_args[1].get('shell', False))
        self.assertEqual(mock_popen.call_args[1]['stdout'], views.subprocess.PIPE)
        self.assertEqual(mock_popen.call_args[1]['stderr'], views.subprocess.PIPE)

    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self):
        request = self.factory.post('/cmd_lab3', {'domain': 'https://www.example.com;whoami', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.other_views.subprocess.Popen') as mock_popen, patch('introduction.other_views.render') as mock_render:
            mock_render.return_value = views.HttpResponse('bad')

            response = views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args[0][2], {'output': 'Something went wrong'})
