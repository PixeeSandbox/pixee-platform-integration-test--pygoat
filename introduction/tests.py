from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='StrongPass123!',
        )
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_shell_metacharacters(self):
        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab3', {
                'domain': 'example.com;id',
                'os': 'win',
            })

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    def test_cmd_lab3_uses_argument_list_without_shell(self):
        process = Mock()
        process.communicate.return_value = (b'resolved', b'')
        with patch('introduction.other_views.subprocess.Popen', return_value=process) as mock_popen:
            response = self.client.post('/cmd_lab3', {
                'domain': 'example.com',
                'os': 'win',
            })

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', kwargs)
