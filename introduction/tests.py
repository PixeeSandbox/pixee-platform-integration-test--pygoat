from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from . import other_views


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cmd-test-user', password='test-password')
        self.factory = RequestFactory()

    def post_lookup(self, domain, os='win'):
        request = self.factory.post('/cmd-lab3/', {'domain': domain, 'os': os})
        request.user = self.user
        return other_views.cmd_lab3(request)

    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_malicious_domain_without_starting_process(self, popen):
        response = self.post_lookup('example.com; touch /tmp/pwned')

        popen.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')

    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_uses_fixed_lookup_executable(self, popen):
        popen.return_value.communicate.return_value = (b'lookup output', b'')

        response = self.post_lookup('www.example.com')

        popen.assert_called_once_with(
            ['nslookup', 'www.example.com'],
            shell=False,
            stdout=other_views.subprocess.PIPE,
            stderr=other_views.subprocess.PIPE,
        )
        self.assertEqual(response.status_code, 200)
