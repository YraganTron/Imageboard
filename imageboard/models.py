from django.db import models
from django.contrib.sessions.models import Session


class Board(models.Model):

    board_shortcut = models.CharField(max_length=10)
    board_name = models.TextField()
    board_specification = models.TextField()
    board_posts = models.IntegerField(default=0)
    board_in_hour = models.IntegerField(default=0)
    board_active_24hour = models.IntegerField(default=0)

    class Meta:
        ordering = ['board_shortcut', ]

    def __str__(self):
        return self.board_shortcut


class Thread(models.Model):

    board = models.ForeignKey(Board)
    thread_tittle = models.CharField(max_length=255, blank=True)
    thread_text = models.TextField()
    thread_image = models.ImageField(blank=True)
    thread_time = models.DateTimeField(auto_now_add=True)
    thread_score = models.IntegerField(default=0)
    thread_answers = models.TextField(blank=True)

    class Meta:
        ordering = ['-thread_time', ]

    def __str__(self):
        if self.thread_tittle == '':
            return str(self.id)
        else:
            return self.thread_tittle

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.pk is None:
            super(Thread, self).save(force_insert, force_update, using, update_fields)
            board = Board.objects.get(board_shortcut=self.board)
            board.board_posts += 1
            board.save()
        else:
            return super(Thread, self).save(force_insert, force_update, using, update_fields)


class Comment(models.Model):

    thread = models.ForeignKey(Thread)
    comments_tittle = models.CharField(max_length=100, blank=True)
    comments_text = models.TextField()
    comments_image = models.ImageField(blank=True)
    comments_time = models.DateTimeField(auto_now_add=True)
    comments_op = models.CharField(max_length=5, blank=True)
    comments_answers = models.TextField(blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.pk is None:
            super(Comment, self).save(force_insert, force_update, using, update_fields)
            if update_fields is None and force_update is False:
                thread = Thread.objects.get(pk=self.thread.pk)
                board = Board.objects.get(board_shortcut=thread.board)
                board.board_posts += 1
                board.save()
        else:
            return super(Comment, self).save(force_insert, force_update, using, update_fields)


class MySession(models.Model):
    session_key = models.ForeignKey(Session)
    name_board = models.CharField(max_length=1024)
    expire_date = models.DateTimeField()
    active = models.CharField(max_length=1024, blank=True)
    thread = models.TextField(blank=True)
