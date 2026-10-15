from django.test import TestCase, RequestFactory
from types import SimpleNamespace
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cmd_lab3_valid_domain_uses_safe_subprocess_arguments(self):
        request = self.factory.post('/cmd_lab3/', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.other_views.subprocess.Popen') as mock_popen, patch('introduction.other_views.render') as mock_render:
            mock_popen.return_value.communicate.return_value = (b'example output', b'')
            mock_render.return_value = SimpleNamespace(status_code=200)

            response = cmd_lab3(request)

        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'example output'})
        self.assertEqual(response, mock_render.return_value)

    def test_cmd_lab3_invalid_domain_rejects_input_without_subprocess(self):
        request = self.factory.post('/cmd_lab3/', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.other_views.subprocess.Popen') as mock_popen, patch('introduction.other_views.render') as mock_render:
            mock_render.return_value = SimpleNamespace(status_code=200)

            response = cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once_with(request, 'Lab/CMD/cmd_lab.html', {'output': 'Invalid domain'})
        self.assertEqual(response, mock_render.return_value)
