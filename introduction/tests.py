from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmd_lab_user',
            password='password123'
        )

    def test_cmd_lab3_rejects_shell_metacharacters_before_subprocess(self):
        request = self.factory.post(
            '/cmd_lab3',
            data={'domain': 'https://www.example.com;id', 'os': 'win'}
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argument_list_and_disables_shell(self):
        request = self.factory.post(
            '/cmd_lab3',
            data={'domain': 'https://www.example.com', 'os': 'win'}
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            mock_popen.return_value.communicate.return_value = (b'lookup output', b'')
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['nslookup', 'example.com'])
        self.assertFalse(mock_popen.call_args.kwargs.get('shell'))
