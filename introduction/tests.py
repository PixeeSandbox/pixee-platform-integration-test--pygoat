from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def test_cmd_lab_uses_argv_without_shell(self):
        User = get_user_model()
        user = User.objects.create_user(username='tester', password='password123')
        client = Client()
        client.force_login(user)

        process = Mock()
        process.communicate.return_value = (b'example output', b'')

        with patch('introduction.views.subprocess.Popen', return_value=process) as mocked_popen:
            response = client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        mocked_popen.assert_called_once()
        args, kwargs = mocked_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs.get('shell', False))
