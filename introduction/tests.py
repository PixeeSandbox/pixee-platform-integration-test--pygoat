import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username='cmduser',
            password='testpassword123',
        )

    def test_cmd_lab_uses_argument_list_for_valid_domain(self):
        self.client.force_login(self.user)
        process = Mock()
        process.communicate.return_value = (b'lookup ok', b'')

        with patch('introduction.views.subprocess.Popen', return_value=process) as mock_popen:
            response = self.client.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertFalse(mock_popen.call_args.kwargs.get('shell', False))

    def test_cmd_lab_rejects_malicious_domain(self):
        self.client.force_login(self.user)

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {'domain': 'example.com; id', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
