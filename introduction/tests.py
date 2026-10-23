from django.test import RequestFactory, TestCase
from django.contrib.auth.models import User
from unittest.mock import Mock, patch

from introduction import views


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='password123')

    def test_cmd_lab_uses_argument_list_for_valid_domain(self):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com', 'os': 'win'})
        request.user = self.user

        process = Mock()
        process.communicate.return_value = (b'valid output', b'')

        with patch('introduction.views.subprocess.Popen', return_value=process) as mock_popen:
            response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        mock_popen.assert_called_once_with(
            ['nslookup', 'example.com'],
            shell=False,
            stdout=views.subprocess.PIPE,
            stderr=views.subprocess.PIPE,
        )

    def test_cmd_lab_rejects_malicious_domain(self):
        request = self.factory.post('/cmd_lab/', {'domain': 'example.com; whoami', 'os': 'win'})
        request.user = self.user

        with patch('introduction.views.subprocess.Popen') as mock_popen:
            response = views.cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
        mock_popen.assert_not_called()
