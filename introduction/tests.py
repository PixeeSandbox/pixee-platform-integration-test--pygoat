import subprocess
from django.test import RequestFactory, TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpass')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_and_disables_shell(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'example output', b'')

        request = self.factory.post('/cmd_lab/', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        called_args, called_kwargs = mock_popen.call_args
        self.assertEqual(called_args[0], ['nslookup', 'example.com'])
        self.assertEqual(called_kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(called_kwargs['stderr'], subprocess.PIPE)
        self.assertNotIn('shell', called_kwargs)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_process_spawn(self, mock_popen):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com; rm -rf /', 'os': 'win'})
        request.user = self.user

        response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
