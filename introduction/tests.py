import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .other_views import cmd_lab3


class CmdLab3Tests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='cmdlab3user',
            password='test-password',
        )

    def test_cmd_lab3_rejects_malicious_domain(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            marker = Path(tmpdir) / 'marker.txt'
            payload = f"example.com; touch {marker}"
            request = self.factory.post('/cmd_lab3', {
                'domain': payload,
                'os': 'linux',
            })
            request.user = self.user

            with patch('introduction.other_views.subprocess.Popen') as mock_popen:
                response = cmd_lab3(request)

            self.assertEqual(response.status_code, 200)
            self.assertFalse(marker.exists())
            self.assertFalse(mock_popen.called)
            self.assertIn(b'Something went wrong', response.content)
            self.assertNotIn(payload.encode(), response.content)

    def test_cmd_lab3_accepts_safe_hyphenated_domain(self):
        request = self.factory.post('/cmd_lab3', {
            'domain': 'my-site.example.com',
            'os': 'linux',
        })
        request.user = self.user

        process = MagicMock()
        process.communicate.return_value = (b'lookup-ok\n', b'')

        with patch('introduction.other_views.subprocess.Popen', return_value=process) as mock_popen:
            response = cmd_lab3(request)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_popen.called)
        self.assertEqual(
            mock_popen.call_args[0][0],
            ['dig', 'my-site.example.com'],
        )
        self.assertNotIn('shell', mock_popen.call_args.kwargs)
        self.assertNotIn(b'Something went wrong', response.content)
        self.assertIn(b'lookup-ok', response.content)
