from pathlib import Path
import tempfile
import uuid

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CommandInjectionLabTests(TestCase):
    def test_cmd_lab_rejects_shell_metacharacters(self):
        user = User.objects.create_user(username="cmduser", password="SafePass123!")
        self.client.force_login(user)

        marker = Path(tempfile.gettempdir()) / f"pygoat_cmd_injection_{uuid.uuid4().hex}"
        payload = f"example.com; touch {marker}"

        response = self.client.post(reverse("Command Injection Lab"), {
            "domain": payload,
            "os": "linux",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid domain")
        self.assertFalse(marker.exists())
