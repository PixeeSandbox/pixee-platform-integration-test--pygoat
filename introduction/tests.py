from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_shell_metacharacters(self):
        user = get_user_model().objects.create_user(
            username='cmd_user',
            password='StrongPassword123!',
        )
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post(
                reverse('Command Injection Lab'),
                {'domain': 'example.com;id', 'os': 'win'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'Something went wrong')
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
