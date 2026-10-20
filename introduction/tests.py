from django.test import TestCase
from unittest.mock import patch

from django.contrib.auth import get_user_model


class CmdLabTests(TestCase):
    def test_cmd_lab_rejects_malicious_domain(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username='tester', password='password123')
        self.client.force_login(user)

        with patch('introduction.views.subprocess.run') as mocked_run:
            response = self.client.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'win'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['output'], 'Something went wrong')
        mocked_run.assert_not_called()
