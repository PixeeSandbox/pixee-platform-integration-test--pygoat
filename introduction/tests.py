from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from introduction import views


class CmdLabViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    def _post_request(self, data):
        request = self.factory.post('/cmd_lab', data)
        request.user = self.user
        return request

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain_without_subprocess(self, mock_popen):
        request = self._post_request({'domain': 'example.com;rm -rf /', 'os': 'win'})

        response = views.cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertIn(b'Something went wrong', response.content)

    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_and_disables_shell(self, mock_popen):
        process = mock_popen.return_value
        process.communicate.return_value = ('lookup output', '')
        request = self._post_request({'domain': 'example.com', 'os': 'win'})

        response = views.cmd_lab(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])
        self.assertEqual(kwargs['stdout'], views.subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], views.subprocess.PIPE)
        self.assertTrue(kwargs['text'])
        self.assertIn(b'lookup output', response.content)
