from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLabSecurityTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmduser', password='secure-password')
        self.assertTrue(self.client.login(username='cmduser', password='secure-password'))

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_popen):
        process = Mock()
        process.communicate.return_value = (b'lookup ok', b'')
        mock_popen.return_value = process

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertIn(b'lookup ok', response.content)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_input(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_not_called()
        self.assertIn(b'Invalid domain', response.content)

# Create your tests here.
