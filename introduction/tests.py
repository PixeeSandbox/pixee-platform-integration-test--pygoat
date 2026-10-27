from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='password123'
        )
        self.client.force_login(self.user)

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_safe_domain_uses_argv(self, mock_run):
        mock_run.return_value.stdout = 'safe output'
        mock_run.return_value.stderr = ''

        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], -1)
        self.assertEqual(kwargs['stderr'], -1)
        self.assertTrue(kwargs['text'])
        self.assertFalse(kwargs['check'])
        self.assertContains(response, 'safe output')

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_injected_domain(self, mock_run):
        response = self.client.post('/cmd_lab3', {
            'domain': 'example.com;whoami',
            'os': 'linux',
        })

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, 'Something went wrong')
