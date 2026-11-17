from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase


class CmdLabCommandInjectionTest(TestCase):
    def test_invalid_domain_is_rejected_without_starting_subprocess(self):
        user = get_user_model().objects.create_user(username='cmd-test', password='test-password')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as popen:
            response = self.client.post('/cmd_lab', {
                'domain': 'example.com; <shell command>',
                'os': 'win',
            })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        popen.assert_not_called()
