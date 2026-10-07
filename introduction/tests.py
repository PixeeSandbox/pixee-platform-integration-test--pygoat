from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cmd_lab_rejects_malicious_domain_before_subprocess(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com && whoami', 'os': 'linux'})
        request.user = Mock(is_authenticated=True)

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = views.cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')

    def test_cmd_lab_invokes_subprocess_with_argument_list(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = Mock(is_authenticated=True)
        process = Mock()
        process.communicate.return_value = (b'example output', b'')

        with patch('introduction.views.subprocess.Popen', return_value=process) as mock_popen:
            response = views.cmd_lab(request)

        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )
        self.assertContains(response, 'example output')
