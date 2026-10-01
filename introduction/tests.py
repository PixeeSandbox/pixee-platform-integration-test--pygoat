import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='password123',
        )

    def test_rejects_invalid_domain_without_calling_popen(self):
        request = self.factory.post('/cmd_lab', {
            'domain': 'example.com; rm -rf /',
            'os': 'linux',
        })
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    def test_valid_domain_uses_argument_list_and_shell_false(self):
        request = self.factory.post('/cmd_lab', {
            'domain': 'example.com',
            'os': 'linux',
        })
        request.user = self.user

        process = Mock()
        process.communicate.return_value = (b'example.com\n', b'')

        with patch('introduction.views.subprocess.Popen', return_value=process) as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'example.com')
