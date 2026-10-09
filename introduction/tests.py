from unittest.mock import ANY, Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_list_subprocess_for_valid_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'lookup output', b'')
        mock_popen.return_value = process

        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com',
            'os': 'win',
        })
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'lookup output', response.content)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=ANY,
            stderr=ANY,
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_shell_metacharacters(self, mock_popen):
        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com;id',
            'os': 'linux',
        })
        request.user = self.user

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid domain', response.content)
        mock_popen.assert_not_called()
