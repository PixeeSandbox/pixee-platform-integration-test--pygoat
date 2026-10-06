import subprocess
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='cmduser', password='pass12345')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'valid lookup', b'')

        response = self.client.post(reverse('Command Injection Lab'), {
            'domain': 'https://www.example.com',
            'os': 'win',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertEqual(kwargs.get('shell', False), False)
        self.assertEqual(kwargs.get('stdout'), subprocess.PIPE)
        self.assertEqual(kwargs.get('stderr'), subprocess.PIPE)
        self.assertContains(response, 'valid lookup')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self, mock_popen):
        response = self.client.post(reverse('Command Injection Lab'), {
            'domain': 'example.com; id',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Invalid domain')
