import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='password123'
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argv_list_without_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'example output', b'')
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn('shell=True', str(mock_popen.call_args))
        self.assertIn(b'example output', response.content)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_injected_domain_without_spawning_process(self, mock_popen):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; id', 'os': 'linux'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertIn(b'Something went wrong', response.content)
