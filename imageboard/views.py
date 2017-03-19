from django.views.generic import ListView, TemplateView, CreateView, DetailView, View
from django.http import HttpResponse
from .models import Board, Thread, Comment
from django.shortcuts import redirect, get_list_or_404, get_object_or_404
from .forms import CreateThread
from django.core import serializers


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
        self.form = CreateThread()
        return super(ThreadList, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        threads = get_list_or_404(Thread.objects.order_by('-thread_score'),
                                  board__board_shortcut=self.kwargs['name_board'])
        if len(threads) >= 5:
            threads = threads[:5]
        return threads

    def get_context_data(self, **kwargs):
        context = super(ThreadList, self).get_context_data(**kwargs)
        context['form'] = self.form
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


class ThreadDetail(DetailView):
    model = Thread
    context_object_name = 'thread'
    template_name = 'thread.html'

    def get_object(self, queryset=None):
        thread = get_object_or_404(Thread, pk=self.kwargs['pk'])
        return thread


class AjaxTooltipCommentMixin(object):
    def render_to_response(self, data, **response_kwargs):
        data = serializers.serialize('json', Comment.objects.filter(id=data))
        return HttpResponse(data, **response_kwargs, content_type='application/json')


class AjaxTooltipComment(View, AjaxTooltipCommentMixin):

    def get(self, request, *args, **kwargs):
        data = self.request.GET.get('tooltip')

        return AjaxTooltipCommentMixin.render_to_response(self, data)


class AjaxTooltipThreadMixin(object):

    def render_to_response(self, data, **response_kwargs):
        data = serializers.serialize('json', Thread.objects.filter(id=data))
        return HttpResponse(data, content_type='application/json')


class AjaxTooltipThread(View, AjaxTooltipThreadMixin):

    def get(self, request, *args, **kwargs):
        data = self.request.GET.get('tooltip')

        return AjaxTooltipThreadMixin.render_to_response(self, data)
