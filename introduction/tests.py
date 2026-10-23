from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


class CmdLabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='tester', password='testpass123')
        self.client.force_login(self.user)

    def test_cmd_lab_rejects_malicious_domain(self):
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {'domain': 'example.com; rm -rf /', 'os': 'win'})
        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()

    def test_cmd_lab_rejects_empty_domain(self):
        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = self.client.post('/cmd_lab', {'domain': '', 'os': 'win'})
        self.assertEqual(response.status_code, 400)
        mock_popen.assert_not_called()
