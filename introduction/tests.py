from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .views import cmd_lab


class CmdLabTests(TestCase):
    def test_rejects_shell_metacharacters_before_running_command(self):
        request = RequestFactory().post('/cmd_lab', {'domain': 'example.com;whoami'})
        request.user = get_user_model()(username='tester')

        with patch('introduction.views.subprocess.Popen') as popen:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
