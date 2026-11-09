from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    def fake_render(self, request, template_name, context=None, *args, **kwargs):
        response = HttpResponse((context or {}).get('output', ''))
        response.context_data = context or {}
        response.template_name = template_name
        return response

    def test_cmd_lab_valid_domain_uses_argument_list(self):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'https://example.com/path', 'os': 'win'},
        )
        request.user = self.user

        with patch('introduction.views.render', side_effect=self.fake_render), patch('introduction.views.subprocess.run') as mock_run:
            mock_run.return_value = SimpleNamespace(stdout='resolved', stderr='')

            response = views.cmd_lab(request)

        mock_run.assert_called_once()
        self.assertEqual(mock_run.call_args.args[0], ['nslookup', 'example.com'])
        self.assertNotIn('shell', mock_run.call_args.kwargs)
        self.assertEqual(mock_run.call_args.kwargs, {'capture_output': True, 'text': True})
        self.assertEqual(response.context_data['output'], 'resolved')

    def test_cmd_lab_rejects_shell_metacharacters_before_subprocess(self):
        request = self.factory.post(
            '/cmd_lab',
            {'domain': 'https://example.com;rm -rf /', 'os': 'linux'},
        )
        request.user = self.user

        with patch('introduction.views.render', side_effect=self.fake_render), patch('introduction.views.subprocess.run') as mock_run:
            response = views.cmd_lab(request)

        mock_run.assert_not_called()
        self.assertEqual(response.context_data['output'], 'Something went wrong')
