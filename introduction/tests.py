from django.test import TestCase, RequestFactory
from unittest.mock import patch

from introduction import views


class DummyUser:
    is_authenticated = True


class CmdLabSecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = DummyUser()

    def _post_request(self, domain, os_value):
        request = self.factory.post('/cmd_lab/', {'domain': domain, 'os': os_value})
        request.user = self.user
        return request

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_rejects_malicious_domain(self, mock_popen, mock_render):
        mock_render.return_value = views.HttpResponse('ok')
        request = self._post_request('example.com;rm -rf /', 'linux')

        response = views.cmd_lab(request)

        self.assertEqual(response.content, b'ok')
        mock_popen.assert_not_called()
        mock_render.assert_called_once()
        self.assertEqual(mock_render.call_args.args[1], 'Lab/CMD/cmd_lab.html')
        self.assertEqual(mock_render.call_args.args[2], {'output': 'Invalid domain'})

    @patch('introduction.views.render')
    @patch('introduction.views.subprocess.Popen')
    def test_cmd_lab_uses_argument_list_for_valid_domain(self, mock_popen, mock_render):
        mock_render.return_value = views.HttpResponse('ok')
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'lookup ok', b'')
        request = self._post_request('example.com', 'linux')

        response = views.cmd_lab(request)

        self.assertEqual(response.content, b'ok')
        mock_popen.assert_called_once()
        self.assertEqual(mock_popen.call_args.args[0], ['dig', 'example.com'])
        self.assertFalse(mock_popen.call_args.kwargs.get('shell', False))
        self.assertEqual(mock_render.call_args.args[1], 'Lab/CMD/cmd_lab.html')
        self.assertEqual(mock_render.call_args.args[2], {'output': 'lookup ok'})
