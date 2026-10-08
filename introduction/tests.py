from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='cmd_user', password='password123')
        self.client.force_login(self.user)

    def test_cmd_lab_uses_list_invocation_for_linux(self):
        domain = 'example.com; echo injected'
        process = Mock()
        process.communicate.return_value = (b'mocked stdout', b'mocked stderr')

        with patch('introduction.views.subprocess.Popen', return_value=process) as mock_popen:
            response = self.client.post('/cmd_lab', {'domain': domain, 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('mocked stdout', response.content.decode())
        self.assertIn('mocked stderr', response.content.decode())
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['dig', domain])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], -1)
        self.assertEqual(kwargs['stderr'], -1)

    def test_cmd_lab_uses_list_invocation_for_windows(self):
        domain = 'example.com && whoami'
        process = Mock()
        process.communicate.return_value = (b'mocked stdout', b'mocked stderr')

        with patch('introduction.views.subprocess.Popen', return_value=process) as mock_popen:
            response = self.client.post('/cmd_lab', {'domain': domain, 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('mocked stdout', response.content.decode())
        self.assertIn('mocked stderr', response.content.decode())
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', domain])
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], -1)
        self.assertEqual(kwargs['stderr'], -1)
