from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_login(self.user)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})

        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_vector_for_valid_hostname(self, mock_popen):
        mock_popen.return_value.communicate.return_value = (b'answer', b'')

        for os_value, executable in [('win', 'nslookup'), ('linux', 'dig')]:
            with self.subTest(os_value=os_value):
                response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': os_value})

                self.assertEqual(response.status_code, 200)
                mock_popen.assert_called_once()
                command = mock_popen.call_args.args[0]
                self.assertIsInstance(command, list)
                self.assertEqual(command[0], executable)
                self.assertEqual(command[1], 'example.com')
                mock_popen.reset_mock()
