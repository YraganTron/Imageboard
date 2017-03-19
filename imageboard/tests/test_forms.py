from django.test import TestCase
from ..forms import CreateThread, AddComment


class FormCreateThread(TestCase):

    def test_init_form(self):
        form = CreateThread()

        self.assertIn('class="form_control"', str(form))


class FormAddComment(TestCase):

    def test_init_form(self):
        form = AddComment()

        self.assertIn('class="form_control"', str(form))
