from django.views.generic import ListView, TemplateView, CreateView, DetailView, View
from django.http import HttpResponse
from .models import Board, Thread, Comment
from django.shortcuts import redirect, get_list_or_404, get_object_or_404
from .forms import CreateThread, AddComment
from django.core import serializers
import re


class Index(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'index.html'


class Contacts(TemplateView):
    template_name = 'contacts.html'


class AjaxThreads(object):

    def render_to_json_response(self, context, **response_kwargs):
        return HttpResponse(self.get_data(context), **response_kwargs, content_type='application/json')

    def get_data(self, context):
        if self.request.GET.get('value'):
            x = int(self.request.GET.get('value'))
            thread_ajax = Thread.objects.filter(
                board__board_shortcut=self.kwargs['name_board']).order_by('-thread_score')
            if x + 5 > len(thread_ajax):
                thread_ajax = thread_ajax[x:len(thread_ajax)]
            else:
                thread_ajax = thread_ajax[x:x + 5]
            comment_ajax = []
            for x in thread_ajax:
                if Comment.objects.filter(thread=x).count() > 3:
                    section = Comment.objects.filter(thread=x).count() - 3
                else:
                    section = 0
                if Comment.objects.filter(thread=x)[section:].count() != 0:
                    comment_ajax.extend(list(Comment.objects.filter(thread=x)[section:]))
            all_ajax = list(thread_ajax) + list(comment_ajax)
            context = serializers.serialize('json', all_ajax)

            return context


class ThreadList(AjaxThreads, ListView):
    model = Thread
    context_object_name = 'threads'
    template_name = 'board.html'

    def dispatch(self, request, *args, **kwargs):
        self.form_thread = CreateThread()
        self.form_comment = AddComment()
        return super(ThreadList, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        threads = get_list_or_404(Thread.objects.order_by('-thread_score'),
                                  board__board_shortcut=self.kwargs['name_board'])
        if len(threads) >= 5:
            threads = threads[:5]
        return threads

    def get_context_data(self, **kwargs):
        context = super(ThreadList, self).get_context_data(**kwargs)
        context['form_thread'] = self.form_thread
        context['form_comment'] = self.form_comment
        context['name_board'] = self.kwargs['name_board']
        context['board'] = Board.objects.get(board_shortcut=self.kwargs['name_board'])
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            return self.render_to_json_response(context, **response_kwargs)
        else:
            return super().render_to_response(context, **response_kwargs)


class AddThread(CreateView):
    form_class = CreateThread

    def form_valid(self, form):
        thread = form.save(commit=False)
        thread.board = Board.objects.get(board_shortcut=self.kwargs['name_board'])
        thread.save()
        return redirect('thread', self.kwargs['name_board'], thread.id)


class AddCommentView(CreateView):
    form_class = AddComment

    def form_valid(self, form):
        comment = form.save(commit=False)
        thread = Thread.objects.get(pk=self.kwargs['pk'])
        comment.thread = thread

        regs = [re.compile('>>[\d]+(?! \(OP\)|\w)'), re.compile('>>[\d]+ \(OP\)')]
        for reg in regs:
            answers = []
            counter_pattern = 0
            for x in re.finditer(reg, comment.comments_text):
                counter_pattern += 1
            count_pattern = counter_pattern
            count_tagged_pattern = 0
            while counter_pattern != 0:
                iters_pattren = re.finditer(reg, comment.comments_text)
                k = 0
                for x in iters_pattren:
                    if count_tagged_pattern == count_pattern - counter_pattern:
                        if x.span()[0] == 0 and count_tagged_pattern == 0:
                            answers.append(comment.comments_text[2:x.span()[1]])
                            if reg == re.compile('>>[\d]+(?! \(OP\)|\w)'):
                                comment.comments_text = '<a class="link-reply" data-num="%s">' % (
                                comment.comments_text[2:x.span()[1]] + ' comment') + comment.comments_text[:x.span()[
                                    1]] + '</a>' + comment.comments_text[x.span()[1]:]
                            else:
                                comment.comments_text = '<a class="link-reply" data-num="%s">' % (
                                comment.comments_text[2:x.span()[1] - 5] + ' thread') + comment.comments_text[:x.span()[
                                    1]] + '</a>' + comment.comments_text[x.span()[1]:]
                            break
                        else:
                            if k == count_pattern - counter_pattern:
                                answers.append(comment.comments_text[x.span()[0] + 2:x.span()[1]])
                                if reg == re.compile('>>[\d]+(?! \(OP\)|\w)'):
                                    comment.comments_text = comment.comments_text[
                                                :x.span()[0]] + '<a class="link-reply" data-num="%s">' % (
                                                comment.comments_text[x.span()[0] + 2:x.span()[1]] + ' comment') + \
                                                            comment.comments_text[x.span()[0]:x.span()[1]] + '</a>' +\
                                                            comment.comments_text[x.span()[1]:]
                                else:
                                    comment.comments_text = comment.comments_text[
                                                :x.span()[0]] + '<a class="link-reply" data-num="%s">' % (
                                                comment.comments_text[x.span()[0] + 2:x.span()[1] - 5] + ' thread') +\
                                                            comment.comments_text[x.span()[0]:x.span()[1]] + '</a>' +\
                                                            comment.comments_text[x.span()[1]:]
                                break
                    k += 1
                count_tagged_pattern += 1
                counter_pattern -= 1

            comment.save()

            for x in answers:
                if reg == re.compile('>>[\d]+(?! \(OP\)|\w)'):
                    comment_for_answers = Comment.objects.get(pk=x)
                    if comment_for_answers.comments_answers == '':
                        comment_for_answers.comments_answers = str(comment.id)
                    else:
                        comment_for_answers.comments_answers += ',' + str(comment.id)
                    comment_for_answers.save()
                else:
                    result = re.search(r'[\d]+', x)
                    x = result.group(0)
                    thread_for_answers = Thread.objects.get(pk=x)
                    if thread_for_answers.thread_answers == '':
                        thread_for_answers.thread_answers = str(comment.id)
                    else:
                        thread_for_answers.thread_answers += ',' + str(comment.id)
                    thread_for_answers.save()

            comment.save()
        form.save()

        if self.request.POST.get('comments_sage') == 'on':
            thread.thread_score -= 3
            thread.save()

        #Дописать работу с сессиями при ОП
        return redirect('thread', self.kwargs['name_board'], self.kwargs['pk'])


class ThreadDetail(DetailView):
    model = Thread
    context_object_name = 'thread'
    template_name = 'thread.html'

    def dispatch(self, request, *args, **kwargs):
        self.form = AddComment()
        return super(ThreadDetail, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        thread = get_object_or_404(Thread, pk=self.kwargs['pk'])
        return thread

    def get_context_data(self, **kwargs):
        context = super(ThreadDetail, self).get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(thread=self.kwargs['pk'])
        context['name_board'] = self.kwargs['name_board']
        context['board'] = Board.objects.get(board_shortcut=self.kwargs['name_board'])
        context['form'] = self.form
        context['pk'] = self.kwargs['pk']
        return context


class AjaxTooltipComment(View):

    def get(self, request, *args, **kwargs):
        data = serializers.serialize('json', Comment.objects.filter(id=self.request.GET.get('tooltip')))

        return HttpResponse(data, content_type='application/json')


class AjaxTooltipThread(View):

    def get(self, request, *args, **kwargs):
        data = serializers.serialize('json', Thread.objects.filter(id=self.request.GET.get('tooltip')))

        return HttpResponse(data, content_type='application/json')


class AjaxTooltip(View):

    def get(self, *args, **kwargs):
        if self.request.GET.get('type_tooltip') == 'thread':
            data = serializers.serialize('json', Thread.objects.filter(id=self.request.GET.get('num_tooltip')))
            return HttpResponse(data, content_type='application/json')
        else:
            data = serializers.serialize('json', Comment.objects.filter(id=self.request.GET.get('num_tooltip')))
            return HttpResponse(data, content_type='application/json')
