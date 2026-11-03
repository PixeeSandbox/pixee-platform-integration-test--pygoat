from django.test import RequestFactory, TestCase
from types import SimpleNamespace
from unittest.mock import patch

from .views import cmd_lab


class CmdLabTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cmd_lab_rejects_malicious_domain(self):
        request = self.factory.post('/cmd_lab', data={'domain': 'example.com;id', 'os': 'linux'})
        request.user = SimpleNamespace(is_authenticated=True)

        with patch('introduction.views.subprocess.Popen', side_effect=AssertionError('Popen should not be called')):
            response = cmd_lab(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong')
