from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch, ANY

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123',
        )

    def test_cmd_lab_rejects_malicious_domain(self):
        request = self.factory.post('/cmd_lab', data={
            'domain': 'example.com; whoami',
            'os': 'linux',
        })
        request.user = self.user

        with patch('introduction.views.subprocess.run') as mock_run:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid domain', response.content.decode())
        mock_run.assert_not_called()

    def test_cmd_lab_uses_argument_list_without_shell(self):
        request = self.factory.post('/cmd_lab', data={
            'domain': 'example.com',
            'os': 'linux',
        })
        request.user = self.user

        process = Mock(stdout='lookup ok\n', stderr='')
        with patch('introduction.views.subprocess.run', return_value=process) as mock_run:
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('lookup ok', response.content.decode())
        mock_run.assert_called_once_with(
            ['dig', 'example.com'],
            stdout=ANY,
            stderr=ANY,
            shell=False,
            text=True,
        )
