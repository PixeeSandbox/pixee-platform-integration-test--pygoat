from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def test_cmd_lab3_rejects_shell_metacharacters(self):
        user = get_user_model().objects.create_user(username="testuser", password="testpass123")
        self.client.force_login(user)

        with patch("introduction.other_views.subprocess.run") as mock_run, patch("introduction.other_views.render") as mock_render:
            mock_render.side_effect = lambda request, template, context: HttpResponse(context["output"])
            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com; cat /etc/passwd", "os": "win"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Something went wrong")
        mock_run.assert_not_called()
        mock_render.assert_called_once()
