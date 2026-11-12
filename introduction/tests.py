from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def test_invalid_domain_does_not_start_process(self):
        request = RequestFactory().post('/cmd/', {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'linux',
        })
        request.user = Mock(is_authenticated=True)

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = cmd_lab3(request)

        popen.assert_not_called()
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
