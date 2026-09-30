import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='tester', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_safe_domain(self, popen_mock):
        process = Mock()
        process.communicate.return_value = (b'safe output', b'')
        popen_mock.return_value = process

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        popen_mock.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertContains(response, 'safe output')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, popen_mock):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; cat /etc/passwd', 'os': 'win'})

        popen_mock.assert_not_called()
        self.assertContains(response, 'Something went wrong')
