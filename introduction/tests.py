from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username='cmdlabuser',
            password='StrongPass123!'
        )
        self.assertTrue(
            self.client.login(username='cmdlabuser', password='StrongPass123!')
        )

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_popen(self, mock_popen):
        response = self.client.post(
            '/cmd_lab',
            {
                'domain': 'example.com; rm -rf /',
                'os': 'linux',
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = (b'valid output', b'')

        response = self.client.post(
            '/cmd_lab',
            {
                'domain': 'example.com',
                'os': 'linux',
            }
        )

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertContains(response, 'valid output')
