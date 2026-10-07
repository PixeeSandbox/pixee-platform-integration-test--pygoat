from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass12345')
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_accepts_normal_domain(self, mock_run):
        mock_run.return_value = SimpleNamespace(returncode=0, stdout='resolved\n', stderr='')

        response = self.client.post('/cmd_lab3', {'domain': 'example.com', 'os': 'lin'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'resolved')
        mock_run.assert_called_once()

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_shell_separators(self, mock_run):
        response = self.client.post('/cmd_lab3', {'domain': 'example.com; echo pwned', 'os': 'lin'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        self.assertNotContains(response, 'pwned')
        mock_run.assert_not_called()
