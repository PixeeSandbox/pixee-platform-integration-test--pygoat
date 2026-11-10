from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from unittest.mock import patch

from introduction.other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def test_rejects_shell_metacharacters_before_running_command(self):
        request = RequestFactory().post('/cmd_lab3', {
            'domain': 'example.com; touch /tmp/injected',
            'os': 'linux',
        })
        request.user = User(username='test-user')

        with patch('introduction.other_views.subprocess.run') as run:
            response = cmd_lab3(request)

        run.assert_not_called()
        self.assertContains(response, 'Invalid domain')
