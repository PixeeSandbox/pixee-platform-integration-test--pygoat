import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='cmduser',
            password='password123',
        )
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_passes_domain_as_argument_list(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'stdout', b'stderr')

        domain = 'example.com; rm -rf /'
        response = self.client.post('/cmd_lab', {'domain': domain, 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', domain])
        self.assertEqual(kwargs['shell'], False)
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)
