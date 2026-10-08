from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from .other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cmd_lab3_rejects_malicious_domain_without_invoking_popen(self):
        request = self.factory.post(
            '/cmd_lab3',
            data={'domain': 'example.com;id', 'os': 'linux'},
        )
        request.user = MagicMock(is_authenticated=True)

        with patch('introduction.other_views.subprocess.Popen') as mock_popen, patch(
            'introduction.other_views.render'
        ) as mock_render:
            mock_render.return_value = HttpResponse('invalid domain')

            response = cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'Invalid domain'},
        )
        self.assertEqual(response.content.decode(), 'invalid domain')

    def test_cmd_lab3_uses_argv_list_and_disables_shell_for_valid_domain(self):
        request = self.factory.post(
            '/cmd_lab3',
            data={'domain': 'example.com', 'os': 'linux'},
        )
        request.user = MagicMock(is_authenticated=True)
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'lookup output', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=mock_process) as mock_popen, patch(
            'introduction.other_views.render'
        ) as mock_render:
            mock_render.return_value = HttpResponse('ok')

            response = cmd_lab3(request)

        mock_popen.assert_called_once()
        called_args, called_kwargs = mock_popen.call_args
        self.assertEqual(called_args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', called_kwargs)
        mock_render.assert_called_once_with(
            request,
            'Lab/CMD/cmd_lab.html',
            {'output': 'lookup output'},
        )
        self.assertEqual(response.content.decode(), 'ok')
