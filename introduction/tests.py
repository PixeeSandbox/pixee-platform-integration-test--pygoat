from django.test import TestCase, RequestFactory
from unittest.mock import Mock, patch

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Mock(is_authenticated=True)

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process
        mock_render.return_value = Mock()

        request = self.factory.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'win'})
        request.user = self.user

        cmd_lab3(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        mock_render.assert_called_once()

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_popen, mock_render):
        mock_render.return_value = Mock()

        request = self.factory.post('/cmd_lab3', {'domain': 'example.com; id', 'os': 'win'})
        request.user = self.user

        cmd_lab3(request)

        mock_popen.assert_not_called()
        mock_render.assert_called_once()
