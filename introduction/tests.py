from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch

from introduction import views


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='secret')

    def _make_request(self, data):
        request = self.factory.post('/cmd_lab/', data)
        request.user = self.user
        return request

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_popen(self, mock_popen):
        request = self._make_request({'domain': 'example.com; rm -rf /', 'os': 'win'})

        response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_windows_and_non_windows(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = (b'output', b'')
        mock_popen.return_value = process

        for os_value, expected_command in (
            ('win', ['nslookup', 'example.com']),
            ('linux', ['dig', 'example.com']),
        ):
            mock_popen.reset_mock()
            process.communicate.reset_mock()
            request = self._make_request({'domain': 'example.com', 'os': os_value})

            response = views.cmd_lab(request)

            self.assertEqual(response.status_code, 200)
            mock_popen.assert_called_once()
            called_args, called_kwargs = mock_popen.call_args
            self.assertEqual(called_args[0], expected_command)
            self.assertFalse(called_kwargs['shell'])
            self.assertEqual(called_kwargs['stdout'], views.subprocess.PIPE)
            self.assertEqual(called_kwargs['stderr'], views.subprocess.PIPE)
            process.communicate.assert_called_once()
