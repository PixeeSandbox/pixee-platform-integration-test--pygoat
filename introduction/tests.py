from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('introduction.views.subprocess.Popen')
    def test_valid_domain_uses_argument_vector(self, popen):
        process = popen.return_value
        process.communicate.return_value = (b'lookup result', b'')
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'linux'})
        request.user = User()

        response = views.cmd_lab(request)

        popen.assert_called_once_with(
            ['dig', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE)
        self.assertContains(response, 'lookup result')

    @patch('introduction.views.subprocess.Popen')
    def test_malformed_domain_is_rejected(self, popen):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; whoami', 'os': 'linux'})
        request.user = User()

        response = views.cmd_lab(request)

        popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
