from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='password123')

    def _build_request(self, data):
        request = self.factory.post('/cmd_lab3', data)
        request.user = self.user
        return request

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, popen_mock):
        request = self._build_request({'domain': 'example.com; id', 'os': 'linux'})

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Something went wrong', response.content.decode())
        popen_mock.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argv_based_subprocess_call(self, popen_mock):
        process = Mock()
        process.communicate.return_value = (b'example output\n', b'')
        popen_mock.return_value = process
        request = self._build_request({'domain': 'example.com', 'os': 'linux'})

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('example output', response.content.decode())
        popen_mock.assert_called_once()
        args, kwargs = popen_mock.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))
