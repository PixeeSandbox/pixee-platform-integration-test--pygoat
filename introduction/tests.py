from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123',
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'example.com.\n', b'')
        mock_popen.return_value = process

        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'https://www.example.com', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertEqual(mock_popen.call_args.kwargs['shell'], False)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_injected_domain_before_subprocess(self, mock_popen):
        request = self.factory.post(
            '/cmd_lab3',
            {'domain': 'https://www.example.com; rm -rf /', 'os': 'win'},
        )
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
