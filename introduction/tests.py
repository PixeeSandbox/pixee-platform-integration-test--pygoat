from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username='cmdlab3-user',
            password='StrongPass123!',
        )
        self.assertTrue(
            self.client.login(username='cmdlab3-user', password='StrongPass123!')
        )

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_rejects_malicious_domain_without_invoking_subprocess(self, mock_run):
        response = self.client.post(
            '/cmd_lab3',
            {'domain': 'example.com;id', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_run.assert_not_called()

    @patch('introduction.other_views.subprocess.run')
    def test_cmd_lab3_uses_argument_list_for_valid_domain(self, mock_run):
        mock_run.return_value = type(
            'CompletedProcessResult',
            (),
            {'stdout': 'ok', 'stderr': ''},
        )()

        response = self.client.post(
            '/cmd_lab3',
            {'domain': 'example.com', 'os': 'win'},
        )

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
        self.assertTrue(kwargs['capture_output'])
        self.assertTrue(kwargs['text'])
        self.assertTrue(kwargs['check'])
