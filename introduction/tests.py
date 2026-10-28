from django.contrib.auth.models import User
from django.test import Client, TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_cmd_lab_rejects_malicious_domain(self):
        self.assertTrue(self.client.login(username='testuser', password='testpass123'))

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {'domain': 'example.com;id', 'os': 'linux'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid domain. Please enter a valid hostname.')
        mock_popen.assert_not_called()
