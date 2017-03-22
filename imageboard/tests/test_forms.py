from django.test import TestCase
from ..forms import NewThreadForm, NewCommentForm


class FormCreateThread(TestCase):

    def test_init_form(self):
        form = NewThreadForm()

        self.assertIn('class="form_control"', str(form))


class FormAddComment(TestCase):

    def test_init_form(self):
        form = NewCommentForm()

        self.assertIn('class="form_control"', str(form))
