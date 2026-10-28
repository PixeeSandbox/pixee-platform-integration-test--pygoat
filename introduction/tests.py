from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from introduction.other_views import cmd_lab3


class CmdLab3SecurityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmd_lab3_user',
            password='test-password',
        )

    def test_cmd_lab3_rejects_malicious_domain(self):
        request = self.factory.post(
            '/cmd_lab',
            data={'domain': 'example.com; echo hacked', 'os': 'linux'},
        )
        request.user = self.user

        with patch('introduction.other_views.subprocess.run') as mock_run:
            response = cmd_lab3(request)

        mock_run.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain')
        self.assertNotContains(response, 'hacked')
