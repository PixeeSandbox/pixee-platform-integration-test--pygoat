from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLabSecurityTests(TestCase):
    def test_shell_syntax_domain_is_rejected(self):
        user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {'domain': 'example.com; id'})

        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
