from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLab3ValidationTests(TestCase):
    def test_cmd_lab3_rejects_shell_metacharacters(self):
        User = get_user_model()
        user = User.objects.create_user(username='cmdlabuser', password='testpassword123')
        self.client.force_login(user)

        with patch('introduction.other_views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab3', {
                'domain': 'example.com; cat /etc/passwd',
                'os': 'linux',
            })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        mock_popen.assert_not_called()
