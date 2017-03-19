from django.contrib import admin

from .models import Board, Thread, Comment


class MyModelAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super(MyModelAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(board__board_shortcut=request.user.first_name)

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return self.list_filter
        return ()


class ThreadInLine(admin.StackedInline):
    model = Comment
    extra = 1
    fields = ['comments_tittle', 'comments_text', 'comments_image']


class ThreadAdmin(MyModelAdmin):
    inlines = [ThreadInLine]
    fields = ['board', 'thread_tittle', 'thread_text', 'thread_image']
    search_fields = ['thread_tittle', 'id']
    list_filter = ('board__board_shortcut',)


class BoardAdmin(MyModelAdmin):
    fields = ['board_shortcut', 'board_name', 'board_specification']

admin.site.register(Board, BoardAdmin)
admin.site.register(Thread, ThreadAdmin)
