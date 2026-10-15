import subprocess
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="cmdlabuser", password="StrongPass123!")
        self.assertTrue(self.client.login(username="cmdlabuser", password="StrongPass123!"))

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_uses_argument_vector_for_valid_domain(self, mock_popen):
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b"ok", b"")

        response = self.client.post("/cmd_lab3", {"domain": "example.com", "os": "win"})

        self.assertEqual(response.status_code, 200)
        args, kwargs = mock_popen.call_args
        self.assertEqual(args[0], ["nslookup", "example.com"])
        self.assertFalse(kwargs["shell"])
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)

    @patch("introduction.other_views.subprocess.Popen")
    def test_cmd_lab3_rejects_malicious_domain(self, mock_popen):
        response = self.client.post("/cmd_lab3", {"domain": "example.com;id", "os": "win"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        mock_popen.assert_not_called()
