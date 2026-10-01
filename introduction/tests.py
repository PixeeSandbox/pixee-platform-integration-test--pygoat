from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from unittest.mock import patch, ANY


class CmdLab3Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser', password='password123')

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'nslookup output', b'')

        response = self.client.post('/cmd_lab3', {'domain': 'https://www.example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])
        self.assertEqual(kwargs['stdout'], ANY)
        self.assertEqual(kwargs['stderr'], ANY)

    @patch('introduction.other_views.subprocess.Popen')
    def test_cmd_lab3_rejects_malicious_domain_before_subprocess(self, mock_popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; whoami', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_popen.called)
        self.assertContains(response, 'Something went wrong')
