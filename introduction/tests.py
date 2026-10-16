from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from introduction.views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123'
        )

    def test_cmd_lab_rejects_shell_metacharacters(self):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com;id', 'os': 'win'})
        request.user = self.user

        with patch('introduction.views.subprocess.run') as mock_run:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Invalid domain', status_code=400)
        mock_run.assert_not_called()
