import subprocess
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def test_cmd_lab_uses_argv_list_without_shell(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username='cmduser', password='password123')
        self.client.force_login(user)

        process_mock = Mock()
        process_mock.communicate.return_value = (b'output', b'')

        with patch('introduction.views.subprocess.Popen', return_value=process_mock) as popen_mock:
            response = self.client.post('/cmd_lab', {
                'domain': 'example.com; rm -rf /',
                'os': 'win',
            })

        self.assertEqual(response.status_code, 200)
        popen_mock.assert_called_once_with(
            ['nslookup', 'example.com; rm -rf /'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotIn('shell', popen_mock.call_args.kwargs)
