from django import template
from ..models import Comment

register = template.Library()


@register.filter
def make_mylist(value):
    return value.split(',')


@register.tag
def add_comments_context(parser, token):
    return AddCommentsContextNode()


class AddCommentsContextNode(template.Node):

    def render(self, context):
        comments = []
        for x in context['threads']:
            if Comment.objects.filter(thread=x).count() > 3:
                section = Comment.objects.filter(thread=x).count() - 3
            else:
                section = 0
            comments.append(Comment.objects.filter(thread=x)[section:])
        context['comments'] = comments
        return ''
