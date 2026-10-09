from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username='cmd-user',
            password='StrongPassword123!'
        )
        self.client.force_login(self.user)

    def test_cmd_lab_uses_nslookup_argument_list_for_windows(self):
        process = Mock()
        process.communicate.return_value = (b'nslookup output', b'')

        with patch('introduction.views.subprocess.Popen', return_value=process) as mocked_popen:
            response = self.client.post('/cmd_lab', {'domain': 'https://www.example.com', 'os': 'win'})

        mocked_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        self.assertContains(response, 'nslookup output')

    def test_cmd_lab_uses_dig_argument_list_for_non_windows(self):
        process = Mock()
        process.communicate.return_value = (b'dig output', b'')

        with patch('introduction.views.subprocess.Popen', return_value=process) as mocked_popen:
            response = self.client.post('/cmd_lab', {'domain': 'example.org', 'os': 'linux'})

        mocked_popen.assert_called_once_with(
            ['dig', 'example.org'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        self.assertContains(response, 'dig output')

    def test_cmd_lab_rejects_malicious_domain_without_invoking_subprocess(self):
        with patch('introduction.views.subprocess.Popen') as mocked_popen:
            response = self.client.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'win'})

        mocked_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
