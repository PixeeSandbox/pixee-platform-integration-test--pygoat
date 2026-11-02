from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from introduction import views


class CmdLabCommandSafetyTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='tester', password='secret123')
        self.client.force_login(user)

    def test_valid_hostname_executes_without_shell(self):
        process = MagicMock()
        process.communicate.return_value = (b'resolved\n', b'')

        self.assertTrue(views._is_valid_domain('example.com'))
        with patch('introduction.views.subprocess.Popen', return_value=process) as mocked_popen:
            response = self.client.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'resolved')
        self.assertEqual(
            mocked_popen.call_args.args[0],
            ['nslookup', 'example.com'],
        )
        self.assertEqual(
            mocked_popen.call_args.kwargs,
            {'stdout': views.subprocess.PIPE, 'stderr': views.subprocess.PIPE},
        )

    def test_malicious_payload_is_rejected_before_subprocess(self):
        self.assertFalse(views._is_valid_domain('example.com && whoami'))
        with patch('introduction.views.subprocess.Popen') as mocked_popen:
            response = self.client.post('/cmd_lab', {'domain': 'example.com && whoami', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mocked_popen.assert_not_called()
