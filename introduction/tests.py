from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import Mock, patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="password12345")
        self.client.force_login(self.user)

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_uses_argument_vector_for_valid_domain(self, mock_run):
        mock_run.return_value = Mock(stdout=b"resolved\n", stderr=b"")

        response = self.client.post("/cmd_lab", {"domain": "example.com", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ["dig", "example.com"])
        self.assertNotIn("shell", kwargs)
        self.assertContains(response, "resolved")

    @patch("introduction.views.subprocess.run")
    def test_cmd_lab_rejects_malicious_domain_before_execution(self, mock_run):
        response = self.client.post("/cmd_lab", {"domain": "example.com; whoami", "os": "linux"})

        self.assertEqual(response.status_code, 200)
        mock_run.assert_not_called()
        self.assertContains(response, "Something went wrong")
