import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_shell_injection(self):
        User = get_user_model()
        user = User.objects.create_user(username="cmduser", password="password123")
        self.client.force_login(user)

        with tempfile.TemporaryDirectory() as tmpdir:
            marker = Path(tmpdir) / "cmd_lab_injection_marker"
            malicious_domain = f"example.com; python -c \"from pathlib import Path; Path(r'{marker}').write_text('pwned')\""

            response = self.client.post(
                "/cmd_lab",
                {"domain": malicious_domain, "os": "win"},
            )

            self.assertEqual(response.status_code, 200)
            self.assertFalse(marker.exists())
