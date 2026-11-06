from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cmdlabuser",
            password="StrongPass123!",
        )
        self.client.force_login(self.user)

    def test_cmd_lab3_rejects_malicious_domain_without_invoking_subprocess(self):
        with patch("introduction.other_views.subprocess.Popen") as popen_mock, patch(
            "introduction.other_views.subprocess.run"
        ) as run_mock:
            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com; id", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Something went wrong")
        popen_mock.assert_not_called()
        run_mock.assert_not_called()

    def test_cmd_lab3_invokes_subprocess_with_argument_list_for_valid_domain(self):
        with patch("introduction.other_views.subprocess.Popen") as popen_mock, patch(
            "introduction.other_views.subprocess.run"
        ) as run_mock:
            process_mock = popen_mock.return_value
            process_mock.communicate.return_value = ("expected output", "")

            response = self.client.post(
                "/cmd_lab3",
                {"domain": "example.com", "os": "linux"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "expected output")
        run_mock.assert_not_called()
        popen_mock.assert_called_once()
        called_args, called_kwargs = popen_mock.call_args
        self.assertEqual(called_args[0], ["dig", "example.com"])
        self.assertFalse(called_kwargs.get("shell", False))
