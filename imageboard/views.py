from django.views.generic import ListView, TemplateView, CreateView, DetailView
from django.views.generic.edit import FormView
from .models import Board, Thread, Comment
from django.shortcuts import resolve_url, redirect
from .forms import CreateThread


class Index(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'index.html'


class Contacts(TemplateView):
    template_name = 'contacts.html'


class ThreadList(ListView):
    model = Thread
    context_object_name = 'threads'
    template_name = 'board.html'

    def dispatch(self, request, *args, **kwargs):
        self.form = CreateThread(request.POST, request.FILES or None)
        return super(ThreadList, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        threads = Thread.objects.filter(board__board_shortcut=self.kwargs['name_board']).order_by('-thread_score')
        if len(threads) >= 5:
            threads = threads[:5]
        return threads

    def get_context_data(self, **kwargs):
        context = super(ThreadList, self).get_context_data(**kwargs)
        context['form'] = self.form
        context['name_board'] = self.kwargs['name_board']
        context['board'] = Board.objects.get(board_shortcut=self.kwargs['name_board'])
        return context


class AddThread(CreateView):
    form_class = CreateThread

    def form_valid(self, form):
        thread = form.save(commit=False)
        board = Board.objects.get(board_shortcut=self.kwargs['name_board'])
        board.board_posts += 1
        thread.board = board
        thread.save()
        board.save()
        return redirect('thread', self.kwargs['name_board'], thread.id)


class ThreadDetail(DetailView):
    model = Thread
    context_object_name = 'thread'
    template_name = 'thread.html'

    def get_object(self, queryset=None):
        thread = Thread.objects.get(pk=self.kwargs['pk'])
        return thread
