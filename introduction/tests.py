from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username='cmdlabuser',
            password='StrongPass123!',
        )
        self.assertTrue(self.client.login(username='cmdlabuser', password='StrongPass123!'))

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen):
        response = self.client.post('/cmd_lab', {'domain': 'example.com; id', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        self.assertFalse(mock_popen.called)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_accepts_valid_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'example.com lookup output', b'')

        response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'example.com lookup output')
        self.assertNotContains(response, 'Invalid domain')
        self.assertTrue(mock_popen.called)
        self.assertEqual(mock_popen.call_args.kwargs['shell'], False)
        self.assertEqual(mock_popen.call_args.args[0], ['dig', 'example.com'])
