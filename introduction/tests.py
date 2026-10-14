from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase


class CmdLabCommandInjectionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_shell_metacharacters(self):
        malicious_domain = 'example.com; echo injected-output'
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {
                'domain': malicious_domain,
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        self.assertNotContains(response, 'injected-output')
        mock_popen.assert_not_called()
