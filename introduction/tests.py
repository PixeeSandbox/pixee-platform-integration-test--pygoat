from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123'
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_safe_authenticated_post_renders_successfully(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'lookup ok', b'')

        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com',
            'os': 'linux',
        })
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'lookup ok', response.content)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen):
        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com;whoami',
            'os': 'linux',
        })
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Something went wrong', response.content)
        mock_popen.assert_not_called()

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_with_shell_disabled(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'win lookup ok', b'')

        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.org',
            'os': 'win',
        })
        request.user = self.user

        response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        called_args, called_kwargs = mock_popen.call_args
        self.assertEqual(called_args[0], ['nslookup', 'example.org'])
        self.assertFalse(called_kwargs.get('shell'))
        self.assertEqual(called_kwargs['stdout'], other_views.subprocess.PIPE)
        self.assertEqual(called_kwargs['stderr'], other_views.subprocess.PIPE)
        self.assertIn(b'win lookup ok', response.content)
