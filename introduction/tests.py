from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import Mock, patch

from . import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="alice", password="password")

    def _request(self, domain, os_value):
        request = self.factory.post("/cmd_lab", {"domain": domain, "os": os_value})
        request.user = self.user
        return request

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_valid_domain_uses_argument_list(self, mock_popen, mock_render):
        process = Mock()
        process.communicate.return_value = (b"valid output", b"")
        mock_popen.return_value = process
        mock_render.side_effect = lambda request, template, context=None, *args, **kwargs: HttpResponse(context.get("output", ""))

        response = views.cmd_lab(self._request("example.com", "win"))

        self.assertEqual(response.content, b"valid output")
        mock_popen.assert_called_once_with(["nslookup", "example.com"], stdout=views.subprocess.PIPE, stderr=views.subprocess.PIPE)
        self.assertNotIn("shell", mock_popen.call_args.kwargs)

    @patch("introduction.views.render")
    @patch("introduction.views.subprocess.Popen")
    def test_cmd_lab_rejects_malicious_domain_without_invoking_subprocess(self, mock_popen, mock_render):
        mock_render.side_effect = lambda request, template, context=None, *args, **kwargs: HttpResponse(context.get("output", ""))

        response = views.cmd_lab(self._request("example.com;rm -rf /", "win"))

        self.assertEqual(response.content, b"Something went wrong")
        mock_popen.assert_not_called()
        mock_render.assert_called_once()
