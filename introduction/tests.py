from unittest.mock import ANY, Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmd_user',
            password='testpassword123',
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.Popen')
    def test_harmless_domain_executes_command(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'safe output\n', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Lab/CMD/cmd_lab.html')
        self.assertContains(response, 'safe output')
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=ANY,
            stderr=ANY,
        )
        self.assertFalse(mock_popen.call_args.kwargs.get('shell', False))

    @patch('introduction.other_views.subprocess.Popen')
    def test_malicious_domain_is_rejected(self, mock_popen):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com;id', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Lab/CMD/cmd_lab.html')
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
