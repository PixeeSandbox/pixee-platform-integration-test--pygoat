import subprocess
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='testuser@example.com',
        )

    def test_cmd_lab_rejects_malicious_domain(self):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com;whoami', 'os': 'linux'},
        )
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid domain', response.content)
        mock_popen.assert_not_called()

    def test_cmd_lab_uses_argument_list_for_valid_domain(self):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'example.com', 'os': 'linux'},
        )
        request.user = self.user

        process_mock = MagicMock()
        process_mock.communicate.return_value = (b'lookup ok', b'')

        with patch('introduction.views.subprocess.Popen', return_value=process_mock) as mock_popen:
            response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'lookup ok', response.content)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
