from types import SimpleNamespace
from unittest.mock import ANY, patch

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_parameterized_arguments(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'example output', b'')

        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=ANY,
            stderr=ANY,
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_injection_payload_before_subprocess(self, mock_popen):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; id', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
