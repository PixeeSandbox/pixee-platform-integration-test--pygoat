from django.test import TestCase, Client
from django.contrib.auth.models import User
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='pass12345')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_passes_valid_domain_as_argument_list(self, mock_run):
        mock_run.return_value.stdout = 'lookup ok\n'
        mock_run.return_value.stderr = ''

        response = self.client.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once_with(['nslookup', 'example.com'], capture_output=True, text=True, shell=False)
        self.assertContains(response, 'lookup ok')

    @patch('introduction.views.subprocess.run')
    def test_cmd_lab_rejects_shell_metacharacters_before_subprocess(self, mock_run):
        response = self.client.post('/cmd_lab', {'domain': 'example.com;rm -rf /', 'os': 'linux'})

        mock_run.assert_not_called()
        self.assertContains(response, 'Something went wrong')
