from django.test import TestCase, RequestFactory
from unittest.mock import patch

import introduction.views as views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = type("User", (), {"is_authenticated": True})()

    def test_cmd_lab_uses_argument_list_without_shell(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user
        process = type("Process", (), {"communicate": lambda self: (b'output', b'')})()

        with patch('introduction.views.subprocess.Popen', return_value=process) as mock_popen:
            response = views.cmd_lab(request)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertFalse(kwargs['shell'])
        self.assertEqual(response.status_code, 200)

    def test_cmd_lab_rejects_malicious_domain(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'linux'})
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = views.cmd_lab(request)

        mock_popen.assert_not_called()
        self.assertContains(response, 'Something went wrong')
