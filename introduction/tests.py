from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch
import subprocess

from introduction.views import cmd_lab


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='testpass123')

    def test_cmd_lab_rejects_malicious_domain_without_invoking_subprocess(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com;rm -rf /', 'os': 'win'})
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as popen_mock:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid domain', response.content.decode())
        popen_mock.assert_not_called()

    def test_cmd_lab_uses_argument_list_for_valid_domains(self):
        process = MagicMock()
        process.communicate.return_value = (b'lookup ok', b'')

        for os_name, expected_command in (
            ('win', ['nslookup', 'example.com']),
            ('linux', ['dig', 'example.com']),
        ):
            with self.subTest(os=os_name):
                request = self.factory.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': os_name})
                request.user = self.user

                with patch('introduction.views.subprocess.Popen', return_value=process) as popen_mock:
                    response = cmd_lab(request)

                self.assertEqual(response.status_code, 200)
                popen_mock.assert_called_once()
                args, kwargs = popen_mock.call_args
                self.assertEqual(args[0], expected_command)
                self.assertNotIn('shell', kwargs)
                self.assertEqual(kwargs['stdout'], subprocess.PIPE)
                self.assertEqual(kwargs['stderr'], subprocess.PIPE)
