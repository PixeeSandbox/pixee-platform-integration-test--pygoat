from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='StrongPass123!',
        )
        self.client.force_login(self.user)

    def test_cmd_lab_executes_for_valid_domain(self):
        with patch('introduction.views.subprocess.Popen') as mock_process:
            mock_process.return_value.communicate.return_value = (b'93.184.216.34\n', b'')

            response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], '93.184.216.34\n')
        mock_process.assert_called_once()
        args, kwargs = mock_process.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertEqual(kwargs['shell'], False)

    def test_cmd_lab_rejects_malicious_domain(self):
        with patch('introduction.views.subprocess.Popen') as mock_process:
            response = self.client.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'Invalid domain')
        mock_process.assert_not_called()
