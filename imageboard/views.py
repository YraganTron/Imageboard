import re

from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, redirect
from django.views.generic import (CreateView, DetailView, ListView,
                                  TemplateView, View)

from .forms import NewCommentForm, NewThreadForm
from .models import Board, Comment, MySession, Thread
from .utils import (add_answers, create_mysession_in_board,
                    create_mysession_in_thread, search_patterns,
                    set_active_user_in_board, set_active_user_in_thread)


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
        """
        Динамически загруждаем треды с комментариями
        """
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
        self.form_thread = NewThreadForm()
        self.form_comment = NewCommentForm()
        create_mysession_in_board(request, kwargs['name_board'])
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
    form_class = NewThreadForm

    def form_valid(self, form):
        thread = form.save(commit=False)
        thread.board = Board.objects.get(board_shortcut=self.kwargs['name_board'])
        thread.save()
        set_active_user_in_board(self.request, self.kwargs['name_board'])

        response = redirect('thread', self.kwargs['name_board'], thread.id)
        # Ставим куку для отслеживания создателя треда
        response.set_cookie('thread{}'.format(thread.id), 'op', 10368000)
        return response


class AddCommentView(CreateView):
    form_class = NewCommentForm

    def form_valid(self, form):
        comment = form.save(commit=False)
        thread = Thread.objects.get(pk=self.kwargs['pk'])
        comment.thread = thread

        # Проверяем были ли использованы ответы по id(tooltip) и обрабатыаем их
        regs = [re.compile('>>[\d]+(?! \(OP\)|\w)'), re.compile('>>[\d]+ \(OP\)')]
        for reg in regs:
            answers = []
            search_patterns(answers, comment, reg)
            comment.save()
            add_answers(reg, comment, answers)
            comment.save()

        if self.request.POST.get('comments_sage') == 'on':
            thread.thread_score -= 3
            thread.save()

        set_active_user_in_thread(self.request, self.kwargs['name_board'])

        response = redirect('thread', self.kwargs['name_board'], self.kwargs['pk'])

        if 'thread{}'.format(thread.id) in self.request.COOKIES:
            if self.request.COOKIES['thread{}'.format(thread.id)] == 'op':
                if self.request.POST.get('op') == 'on':
                    comment.comments_op = '# OP'
                    comment.save()
        return response


class ThreadDetail(DetailView):
    model = Thread
    context_object_name = 'thread'
    template_name = 'thread.html'

    def dispatch(self, request, *args, **kwargs):
        self.form = NewCommentForm()
        create_mysession_in_thread(request, kwargs['name_board'], kwargs['pk'])
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
        thread = context['thread']
        thread.thread_score = \
            MySession.objects.filter(thread__contains=context['pk']).count() + 3 * context['comments'].count()
        thread.save()
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
