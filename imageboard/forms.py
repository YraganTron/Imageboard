from django import forms
from django.forms import widgets

from .models import Comment, Thread


class NewThreadForm(forms.ModelForm):
    thread_image = forms.ImageField(required=False)
    thread_tittle = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(NewThreadForm, self).__init__(*args, **kwargs)
        self.fields['thread_text'].widget.attrs.update({'class': 'form_control'})

    class Meta(object):
        model = Thread
        fields = ['thread_tittle', 'thread_text', 'thread_image']


class NewCommentForm(forms.ModelForm):
    comments_image = forms.ImageField(required=False)
    comments_tittle = forms.CharField(required=False)
    comments_sage = forms.BooleanField(widget=widgets.CheckboxInput, required=False)
    op = forms.BooleanField(widget=widgets.CheckboxInput, required=False)

    def __init__(self, *args, **kwargs):
        super(NewCommentForm, self).__init__(*args, **kwargs)
        self.fields['comments_text'].widget.attrs.update({'class': 'form_control'})

    class Meta(object):
        model = Comment
        fields = ['comments_tittle', 'comments_text', 'comments_sage', 'op', 'comments_image']
