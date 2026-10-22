import subprocess
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username='cmdlabuser',
            password='strong-password',
        )

    def setUp(self):
        self.factory = RequestFactory()

    def test_cmd_lab_valid_input_uses_argument_list(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        process = patch('introduction.views.subprocess.Popen')
        with process as mock_popen:
            mock_process = mock_popen.return_value
            mock_process.communicate.return_value = (b'example output', b'')

            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ['nslookup', 'example.com'])
        self.assertIsInstance(args[0], list)
        self.assertNotIn('shell', kwargs)
        self.assertEqual(kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(kwargs['stderr'], subprocess.PIPE)

    def test_cmd_lab_rejects_malicious_domain_before_popen(self):
        request = self.factory.post('/cmd_lab', {'domain': 'example.com; id', 'os': 'win'})
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Something went wrong', response.content)
        mock_popen.assert_not_called()
