from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="tester", password="testpass123"
        )

    def fake_render(self, request, template_name, context=None, *args, **kwargs):
        return HttpResponse((context or {}).get("output", ""))

    def test_authenticated_post_uses_argument_separated_subprocess_call(self):
        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "example.com", "os": "win"},
        )
        request.user = self.user

        with patch("introduction.views.render", side_effect=self.fake_render), patch(
            "introduction.views.subprocess.run"
        ) as mock_run:
            mock_run.return_value.stdout = "lookup output"
            mock_run.return_value.stderr = ""

            response = cmd_lab(request)

        self.assertEqual(response.content.decode(), "lookup output")
        mock_run.assert_called_once_with(
            ["nslookup", "example.com"], capture_output=True, text=True
        )
        self.assertNotIn("shell", mock_run.call_args.kwargs)

    def test_shell_metacharacters_are_rejected_before_subprocess(self):
        request = self.factory.post(
            "/cmd_lab/",
            {"domain": "example.com;rm -rf /", "os": "win"},
        )
        request.user = self.user

        with patch("introduction.views.render", side_effect=self.fake_render), patch(
            "introduction.views.subprocess.run"
        ) as mock_run:
            response = cmd_lab(request)

        self.assertEqual(response.content.decode(), "Something went wrong")
        mock_run.assert_not_called()
