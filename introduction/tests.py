from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CommandInjectionViewTests(TestCase):
    def test_cmd_lab3_rejects_invalid_domain_before_subprocess(self):
        request = RequestFactory().post(
            '/cmd_lab3', {'domain': 'example.com; id', 'os': 'linux'}
        )
        request.user = get_user_model()()

        with patch('introduction.other_views.subprocess.Popen') as popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 400)
        popen.assert_not_called()
