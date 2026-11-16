from django.test import TestCase
from django.contrib.auth.models import User


class CommandInjectionTests(TestCase):
    def test_cmd_lab_rejects_domain_with_shell_metacharacters(self):
        user = User.objects.create_user(username="cmd-test", password="test-password")
        self.client.force_login(user)
        payload = "example.com;echo COMMAND_INJECTION_TEST"

        response = self.client.post("/cmd_lab", {"domain": payload, "os": "linux"})

        self.assertContains(response, "Invalid domain")
        self.assertNotContains(response, payload)
