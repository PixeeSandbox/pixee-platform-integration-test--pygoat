from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Mock()
        self.user.is_authenticated = True

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_list_for_windows_branch(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process

        request = self.factory.post('/cmd_lab/', {'domain': 'example.com; whoami', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com; whoami'])
        self.assertNotIn('shell', kwargs)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_list_for_non_windows_branch(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'dig output', b'')
        mock_popen.return_value = process

        request = self.factory.post('/cmd_lab/', {'domain': 'example.org && id', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.org && id'])
        self.assertNotIn('shell', kwargs)
