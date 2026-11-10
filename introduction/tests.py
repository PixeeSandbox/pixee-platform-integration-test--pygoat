from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    def test_cmd_lab3_rejects_malicious_domain_without_popen(self):
        request = self.factory.post(
            '/cmd_lab3',
            data={'domain': 'example.com; rm -rf /', 'os': 'linux'}
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argument_list_without_shell(self):
        request = self.factory.post(
            '/cmd_lab3',
            data={'domain': 'example.com', 'os': 'linux'}
        )
        request.user = self.user

        mock_process = patch('introduction.other_views.subprocess.Popen').start()
        self.addCleanup(patch.stopall)
        mock_process.return_value.communicate.return_value = (b'answer', b'')

        response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        mock_process.assert_called_once()
        args, kwargs = mock_process.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)
