from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
import re
from bs4 import BeautifulSoup
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


@register.filter(needs_autoescape=True)
def my_safe(text, autoescape=True):
    string = ''
    tags = []
    regs = [re.compile('>>[\d]+(?! \(OP\)|\w)'), re.compile('>>[\d]+ \(OP\)')]
    for reg in regs:
        counter_pattren = 0
        for x in re.finditer(reg, text):
            counter_pattren += 1
        count_pattren = counter_pattren
        count_tagged_pattern = 0
        while counter_pattren != 0:
            iters_pattern = re.finditer(reg, text)
            k = 0
            for x in iters_pattern:
                if count_tagged_pattern == count_pattren - counter_pattren:
                    if x.span()[0] == 0 and count_tagged_pattern == 0:
                        if reg == re.compile('>>[\d]+(?! \(OP\)|\w)'):
                            tags.append('<a class="link-reply" data-num="%s">' %(text[2:x.span()[1]] + ' comment') + text[:x.span()[1]] + '</a>')
                        else:
                            tags.append('<a class="link-reply" data-num="%s">' %(text[2:x.span()[1] - 5] + ' thread') + text[:x.span()[1]] + '</a>')
                        break
                    else:
                        if k == count_pattren - counter_pattren:
                            if reg == re.compile('>>[\d]+(?! \(OP\)|\w)'):
                                tags.append('<a class="link-reply" data-num="%s">' %(text[x.span()[0] +2:x.span()[1]] + ' comment') +\
                                       text[x.span()[0]:x.span()[1]] + '</a>')
                            else:
                                tags.append('<a class="link-reply" data-num="%s">' %(text[x.span()[0] + 2:x.span()[1] - 5] + ' thread') +\
                                       text[x.span()[0]:x.span()[1]] + '</a>')
                            break
                k += 1
            count_tagged_pattern += 1
            counter_pattren -= 1
    counter = 0
    soup = BeautifulSoup(text)
    soup = soup.find_all(text=True)
    for x in soup:
        if re.fullmatch(regs[0], x) == None and re.fullmatch(regs[1], x) == None:
            string += conditional_escape(x)
        else:
            for y in tags:
                if x in y:
                    string += y
                    counter += 1
                    break
    return mark_safe(string)
