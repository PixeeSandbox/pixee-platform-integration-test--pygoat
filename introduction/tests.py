from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from introduction import other_views


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cmd_lab3_rejects_shell_metacharacters(self):
        request = self.factory.post('/cmd_lab3', {
            'domain': 'example.com; whoami',
            'os': 'linux',
        })
        request.user = Mock(is_authenticated=True)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = other_views.cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()

    def test_cmd_lab3_invokes_subprocess_without_shell_for_valid_hostname(self):
        for os_value, executable in (('win', 'nslookup'), ('linux', 'dig')):
            with self.subTest(os=os_value):
                request = self.factory.post('/cmd_lab3', {
                    'domain': 'www.example-domain.com',
                    'os': os_value,
                })
                request.user = Mock(is_authenticated=True)

                with patch('introduction.other_views.subprocess.Popen') as popen:
                    popen.return_value.communicate.return_value = (b'lookup result', b'')
                    response = other_views.cmd_lab3(request)

                self.assertEqual(response.status_code, 200)
                popen.assert_called_once_with(
                    [executable, 'www.example-domain.com'],
                    shell=False,
                    stdout=other_views.subprocess.PIPE,
                    stderr=other_views.subprocess.PIPE,
                )
