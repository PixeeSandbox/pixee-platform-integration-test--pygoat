from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CmdLabCommandInjectionTest(TestCase):
    def test_injection_shaped_domain_is_rejected_without_running_process(self):
        user = get_user_model().objects.create_user(username='cmd-lab-user', password='test-password')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.Popen') as popen:
            response = self.client.post(
                reverse('Command Injection Lab'),
                {'domain': 'example.com; echo SHOULD_NOT_RUN', 'os': 'win'},
            )

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
