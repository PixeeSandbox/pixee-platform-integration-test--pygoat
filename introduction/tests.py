from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from . import other_views


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _post_lookup(self, domain):
        request = self.factory.post('/cmd_lab3/', {'domain': domain, 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)
        return other_views.cmd_lab3(request)

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_injection_shaped_domain_without_starting_process(self, popen, render):
        self._post_lookup('example.com; touch /tmp/injected')

        popen.assert_not_called()
        render.assert_called_once()
        self.assertEqual(render.call_args.kwargs['status'], 400)

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_rejects_option_like_domain_without_starting_process(self, popen, render):
        self._post_lookup('--help')

        popen.assert_not_called()
        render.assert_called_once()
        self.assertEqual(render.call_args.kwargs['status'], 400)

    @patch('introduction.other_views.render')
    @patch('introduction.other_views.subprocess.Popen')
    def test_valid_domain_is_passed_as_separate_argument_without_shell(self, popen, render):
        popen.return_value.communicate.return_value = (b'lookup result', b'')

        self._post_lookup('https://www.example.com')

        popen.assert_called_once()
        args, kwargs = popen.call_args
        self.assertEqual(args[0], ['dig', 'example.com'])
        self.assertIs(kwargs['shell'], False)
